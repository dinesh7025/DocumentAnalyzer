import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from agents.ingestor_agent import ingest_document
from services.kafka_producer_service import send_to_kafka

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
    username = request.form.get("username", "system")

    send_to_kafka("document_ingest", {
        "filename": filename,
        "extracted_text": extracted_text,
        "file_url": file_url,
        "uploaded_by": username
    })

    return jsonify({"message": "File ingested and queued for processing", "details": result})
