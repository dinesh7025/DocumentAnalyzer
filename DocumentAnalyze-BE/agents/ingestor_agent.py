from datetime import datetime, timezone
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ocr_service import extract_text_from_image
from services.pdf_extractor import extract_text_from_pdf
from Utils.azure_blob import upload_file_to_blob


def ingest_document(file):

    filename = file.filename.lower()
    file_url = upload_file_to_blob(file.stream, file.filename, file.content_type)

    file.stream.seek(0)

    if filename.endswith(".pdf"):
        ocr_start = datetime.now(timezone.utc)
        text = extract_text_from_pdf(file)
        ocr_end = datetime.now(timezone.utc)
        duration = round((ocr_end - ocr_start).total_seconds(), 2)
        
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        file.stream.seek(0)
        ocr_start = datetime.now(timezone.utc)
        text = extract_text_from_image(file)
        ocr_end = datetime.now(timezone.utc)
        duration = round((ocr_end - ocr_start).total_seconds(), 2)
    else:
        return {"error": "Unsupported file type"}
    MAX_CHAR = 20000
    # Placeholder for Kafka publishing (later step)
    return {
        "filename": filename,
        "extracted_text": text[:MAX_CHAR] + "..." if len(text) > MAX_CHAR else text,
        "file_url": file_url,
        "status": "success",
        "duration": duration
    }
