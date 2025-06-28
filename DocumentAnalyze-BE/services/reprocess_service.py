# reprocess_document_service.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import io
from database.base import get_db_connection
import requests
from datetime import datetime, timezone
from services.document_service import DocumentService
from services.processing_stage_service import ProcessingStageService
from agents.classifier_agent import classify_document
from agents.ingestor_agent import extract_text_from_pdf, extract_text_from_image
from agents.router_agent import route_document
from services.routing_service import RoutingService
from services.log_service import LogService
from services.user_service import UserService
import json


def reprocess_document(document_id: int):
    db = next(get_db_connection())
    doc_service = DocumentService(db)
    stage_service = ProcessingStageService(db)
    routing_service = RoutingService(db)
    log_service = LogService(db)
    user_service = UserService(db)

    # 1. Get document metadata
    print("🔍 Looking up doc_id:", document_id)
    document = doc_service.get_document_by_id(document_id)
    if not document:
        raise Exception("Document not found")

    file_url = document.storage_path
    filename = document.filename.lower()
    uploaded_by = document.uploaded_by

    # 2. Download file from Azure Blob Storage
    response = requests.get(file_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch file from Blob")

    file_stream = io.BytesIO(response.content)
    file_stream.seek(0)

    # 3. Extract Text (Ingest)
    ocr_start = datetime.now(timezone.utc)
    if filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_stream)
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        extracted_text = extract_text_from_image(file_stream)
    else:
        raise Exception("Unsupported file type")
    ocr_end = datetime.now(timezone.utc)
    ocr_duration = round((ocr_end - ocr_start).total_seconds(), 2)

    # 4. Update extracted text
    doc_service.update_extracted_text(document_id, extracted_text)

    # 5. Update OCR stage
    stage_service.update_stage(
        document_id=document_id,
        stage="ocr",
        duration=ocr_duration,
        details=json.dumps({"note": "Reprocessed OCR"})
    )

    # 6. Classify
    class_start = datetime.now(timezone.utc)
    classified_data = classify_document(extracted_text)
    class_end = datetime.now(timezone.utc)

    doc_type = classified_data.get("label", "others")
    confidence = classified_data.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        confidence = 0.0

    class_duration = round((class_end - class_start).total_seconds(), 2)

    # 7. Update classification stage
    stage_service.update_stage(
        document_id=document_id,
        stage="classification",
        duration=class_duration,
        details=json.dumps({"type": doc_type, "confidence": f"{confidence:.2f}"})
    )

    # 8. Update status based on confidence
    if confidence >= 0.8:
        doc_service.update_status(document_id, "classified")
    else:
        doc_service.update_status(document_id, "review_needed")
        log_service.log_event(
            event_type="WARNING",
            message="Low classification confidence on reprocess",
            source="reprocess_document",
            user_id=uploaded_by,
            document_id=document_id
        )
        return  # skip routing

    # 9. Route document

    user = user_service.get_user_by_id(uploaded_by)
    if not user:
        raise Exception("User not found")
    route_start = datetime.now(timezone.utc)
    target_system = route_document(doc_type, filename, file_url,user.email)
    route_end = datetime.now(timezone.utc)
    route_duration = round((route_end - route_start).total_seconds(), 2)

    routing_service.add_route(document_id, target_system)
    stage_service.update_stage(
        document_id=document_id,
        stage="routing",
        duration=route_duration,
        details=json.dumps({"routed_to": target_system})
    )
    doc_service.update_status(document_id, "routed")
    log_service.log_event(
        event_type="INFO",
        message=f"Reprocessed and routed to {target_system}",
        source="reprocess_document",
        user_id=uploaded_by,
        document_id=document_id
    )

    return {"status": "success", "routed_to": target_system}
