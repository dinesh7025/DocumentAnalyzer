import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import request, jsonify, session
from services.user_service import UserService
from database.base import get_db_connection
from flask import Blueprint, request, jsonify
from agents.ingestor_agent import ingest_document
from services.kafka_producer_service import send_to_kafka
from services.document_service import DocumentService
from services.user_service import UserService
from database.base import get_db_connection
from services.reprocess_service import reprocess_document
from services.routing_service import RoutingService
from datetime import datetime, timezone
from services.email_service import fetch_email_attachments
from agents.router_agent import route_document

upload_bp = Blueprint("upload", __name__, url_prefix="/api")


@upload_bp.route("/upload", methods=["POST"])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    result = ingest_document(file)

    filename = result.get("filename")
    extracted_text = result.get("extracted_text")
    file_url = result.get("file_url")
    userId = request.form.get("userId", "system")
    ocr_duration = result.get("duration")


    send_to_kafka("document_ingest", {
        "filename": filename,
        "extracted_text": extracted_text,
        "file_url": file_url,
        "uploaded_by": userId,
        "ocr_duration": ocr_duration

    })

    return jsonify({"message": "File ingested and queued for processing", "details": result})

# === [NEW] Get all documents (admin use only) ===
@upload_bp.route("/documents", methods=["GET"])
def get_all_documents():
    db = next(get_db_connection())
    service = DocumentService(db)
    try:
        documents = service.get_all_documents()
        doc_list = []
        for doc in documents:
            #add stage details for each document
            stages_info = []
            for stage in doc.stages:
                stage_data = {
                    "name": stage.stage,
                    "duration": stage.duration,
                    "details": json.loads(stage.details or "{}")
                }
                stages_info.append(stage_data)
            
            doc_info = {
                "id": doc.id,
                "filename": doc.filename,
                "classified_as": doc.document_type,
                "routed_to": doc.routing[0].routed_to if hasattr(doc, 'routing') and doc.routing else "Not Routed",
                "uploaded_time": doc.upload_time.strftime("%Y-%m-%d %H:%M:%S") if doc.upload_time else None,
                "status": doc.status,
                "storage_path": doc.storage_path,
                "uploaded_by": doc.uploader.username if doc.uploader else "Unknown",
                "stages": stages_info
            }
            doc_list.append(doc_info)
        return jsonify(doc_list)
    finally:
        db.close()
# === [NEW] Get documents by username ===
@upload_bp.route("/documents/<userId>", methods=["GET"])
def get_documents_by_user(userId):
    db = next(get_db_connection())
    service = DocumentService(db)
    try:
        documents = service.get_documents_by_user(int(userId))
        doc_list = []
        
        for doc in documents:
            #add stage details for each document
            stages_info = []
            for stage in doc.stages:
                stage_data = {
                    "name": stage.stage,
                    "duration": stage.duration,
                    "details": json.loads(stage.details or "{}")
                }
                stages_info.append(stage_data)
            
            doc_info = {
                "id": doc.id,
                "filename": doc.filename,
                "classified_as": doc.document_type,
                "routed_to": doc.routing[0].routed_to if hasattr(doc, 'routing') and doc.routing else "Not Routed",
                "uploaded_time": doc.upload_time.strftime("%Y-%m-%d %H:%M:%S") if doc.upload_time else None,
                "status": doc.status,
                "storage_path": doc.storage_path,
                "uploaded_by": doc.uploader.username if doc.uploader else "Unknown",
                "stages": stages_info
            }
            doc_list.append(doc_info)
        
        return jsonify(doc_list)
    finally:
        db.close()

@upload_bp.route("/documents/<int:document_id>/reprocess", methods=["POST"])
def reprocess_document_endpoint(document_id):
    try:
        reprocess_document(document_id)
        return jsonify({"message": f"Document {document_id} reprocessed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_bp.route('/documents/<int:doc_id>/route-to', methods=['POST'])
def reroute_document(doc_id):
    db = next(get_db_connection())
    doc_service = DocumentService(db)
    user_service = UserService(db)
    routing_service = RoutingService(db)

    data = request.get_json()
    doc_type = data.get("doc_type", "").strip().lower()

    if not doc_type:
        return jsonify({"error": "Document type is required"}), 400

    # Fetch document metadata
    document = doc_service.get_document_by_id(doc_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404

    # Fetch uploader's email
    user = user_service.get_user_by_id(document.uploaded_by)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Route logic
    try:
        route_start = datetime.now(timezone.utc)
        target_system = route_document(doc_type, document.filename, document.storage_path, user.email)
        route_end = datetime.now(timezone.utc)

        route_duration = round((route_end - route_start).total_seconds(), 2)

        # Update routing record and stage
        routing_service.update_route(doc_id, target_system,"Re-routed to this system")
        doc_service.update_status(doc_id, "routed")

        from services.processing_stage_service import ProcessingStageService
        stage_service = ProcessingStageService(db)
        stage_service.update_stage(
            document_id=doc_id,
            stage="routing",
            duration=route_duration,
            details=json.dumps({"routed_to": target_system})
        )

        return jsonify({
            "message": f"Document routed to {target_system} successfully.",
            "duration": route_duration
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# === [NEW] Delete document by ID ===
@upload_bp.route("/documents/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):
    db = next(get_db_connection())
    service = DocumentService(db)
    try:
        success = service.delete_document(document_id)
        if success:
            return jsonify({"message": "Document deleted successfully"})
        return jsonify({"error": "Document not found"}), 404
    finally:
        db.close()

@upload_bp.route("/fetch-email", methods=["POST"])
def fetch_documents_from_email():
    from werkzeug.datastructures import FileStorage
    from services.user_service import UserService

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 401

    db = next(get_db_connection())
    user_service = UserService(db)

    try:
        user = user_service.get_user_by_id(user_id)
        if not user or not user.app_email or not user.app_password:
            return jsonify({"error": "No saved email credentials found"}), 400

        attachments = fetch_email_attachments(user.app_email, user.app_password)
        results = []

        for att in attachments:
            byte_stream = att["content"]
            byte_stream.seek(0)

            file = FileStorage(
                stream=byte_stream,
                filename=att["filename"],
                content_type="application/octet-stream"
            )

            result = ingest_document(file)

            result["email_subject"] = att["subject"]
            result["email_from"] = att["from"]
            result["email_date"] = att["date"].strftime("%Y-%m-%d %H:%M:%S")

            send_to_kafka("document_ingest", {
                "filename": result["filename"],
                "extracted_text": result["extracted_text"],
                "file_url": result["file_url"],
                "uploaded_by": user_id,
                "ocr_duration": result["duration"],
            })

            results.append(result)

        return jsonify({
            "message": f"{len(results)} documents fetched and queued",
            "documents": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        db.close()

@upload_bp.route("/users/save-app-credentials", methods=["POST"])
def save_app_credentials():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        app_email = data.get("app_email")
        app_password = data.get("app_password")

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        if not app_email or not app_password:
            return jsonify({"error": "Both app_email and app_password are required"}), 400

        db = next(get_db_connection())
        user_service = UserService(db)

        user = user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # ✅ Save credentials to the user model
        user.app_email = app_email
        user.app_password = app_password
        db.commit()

        return jsonify({"message": "Email credentials saved successfully"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@upload_bp.route("/users/clear-app-credentials", methods=["POST"])
def clear_app_credentials():
    from services.user_service import UserService
    from database.base import get_db_connection

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    db = next(get_db_connection())
    user_service = UserService(db)

    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_service.update_app_credentials(user_id, None, None)

        return jsonify({"message": "App email and password cleared successfully"}), 200
    finally:
        db.close()
