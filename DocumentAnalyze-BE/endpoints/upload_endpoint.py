import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from agents.ingestor_agent import ingest_document
from services.kafka_producer_service import send_to_kafka
from services.document_service import DocumentService
from database.base import get_db_connection

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

    send_to_kafka("document_ingest", {
        "filename": filename,
        "extracted_text": extracted_text,
        "file_url": file_url,
        "uploaded_by": userId
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
            doc_info = {
                "id": doc.id,
                "filename": doc.filename,
                "classified_as": doc.document_type,
                "routed_to": doc.routing[0].routed_to if hasattr(doc, 'routing') and doc.routing else "Not Routed",
                "uploaded_time": doc.upload_time.strftime("%Y-%m-%d %H:%M:%S") if doc.upload_time else None,
                "status": doc.status,
                "storage_path": doc.storage_path,
                "uploaded_by": doc.uploader.username if doc.uploader else "Unknown"
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
            doc_info = {
                "id": doc.id,
                "filename": doc.filename,
                "classified_as": doc.document_type,
                "routed_to": doc.routing[0].routed_to if hasattr(doc, 'routing') and doc.routing else "Not Routed",
                "uploaded_time": doc.upload_time.strftime("%Y-%m-%d %H:%M:%S") if doc.upload_time else None,
                "status": doc.status,
                "storage_path": doc.storage_path,
                "uploaded_by": doc.uploader.username if doc.uploader else "Unknown"
            }
            doc_list.append(doc_info)
        return jsonify(doc_list)
    finally:
        db.close()

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