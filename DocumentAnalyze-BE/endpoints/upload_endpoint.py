import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from agents.ingestor_agent import ingest_document
from services.kafka_producer_service import send_to_kafka
from services.document_service import DocumentService
from services.user_service import UserService
from database.base import get_db_connection
from services.reprocess_service import reprocess_document
from services.routing_service import RoutingService
from datetime import datetime, timezone
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