import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer
from datetime import datetime, timezone
import json
from agents.classifier_agent import classify_document
from services.document_service import DocumentService
from services.user_service import UserService
from agents.router_agent import route_document
from services.routing_service import RoutingService
from services.log_service import LogService
from services.processing_stage_service import ProcessingStageService

from database.base import get_db_connection
from datetime import datetime

def consume_documents():
    db = next(get_db_connection())
    doc_service = DocumentService(db)
    user_service = UserService(db)
    routing_service = RoutingService(db)
    log_service = LogService(db)
    stage_service = ProcessingStageService(db)


    consumer = KafkaConsumer(
        'document_ingest',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='doc_ingest_group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print("✅ Kafka consumer started... Waiting for messages.")
    
    for message in consumer:
        data = message.value
        print(f"📥 Received: {data}")

        filename = data.get("filename")
        extracted_text = data.get("extracted_text")
        file_url = data.get("file_url", "")
        uploaded_by = data.get("uploaded_by", "")
        ocr_duration = data.get("ocr_duration",0)

        if not filename or not extracted_text or not uploaded_by:
            print("⚠️ Missing fields in message. Skipping.")
            continue
        
        class_start = datetime.now(timezone.utc)
        classified_data = classify_document(extracted_text)
        class_end = datetime.now(timezone.utc)

        doc_type = classified_data.get("label", "others")
        confidence = classified_data.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (ValueError, TypeError):
             confidence = 0.0

        print(f"📄 Classified as: {doc_type} ({confidence:.2f} confidence)")

        class_duration = round((class_end - class_start).total_seconds(),2)

        # Insert document metadata
        document_data = {
            "filename": filename,
            "storage_path": file_url,
            "uploaded_by": uploaded_by,
            "upload_time": datetime.now(timezone.utc),
            "document_type": doc_type,
            "status": "processed"
        }
        doc_id = doc_service.create_document(document_data)

        if not doc_id:
            print("❌ Failed to insert document.")
            continue

        doc_service.add_extracted_text(doc_id, extracted_text)
        print(f"✅ Document stored with ID: {doc_id}")

        #add process stage for OCR
        try:
            stage_service.add_stage(
                document_id=doc_id,
                stage="ocr",
                duration = ocr_duration,
                details={"note": "Time taken by OCR step"}
            )
        except Exception as e:
            print(f"⚠️ Failed to record OCR stage: {e}")
            
        #add process stage for classfication
        try:
            stage_service.add_stage(
                document_id=doc_id,
                stage="classification",
                duration= class_duration,
                details={"type": doc_type, "confidence": f"{confidence:.2f}"}
            )
        except Exception as e:
            print(f"⚠️ Failed to record classify stage: {e}")

        # Route document based on type
        # Routing Stage
        route_start = datetime.now(timezone.utc)
        target_system = route_document(doc_type)
        route_end = datetime.now(timezone.utc)
        routing_service.add_route(doc_id, target_system)
        route_end = datetime.now(timezone.utc)

        route_duration = round((route_end - route_start).total_seconds(),2)
        # 📝 Record routing stage
        try:
         stage_service.add_stage(
            document_id=doc_id,
            stage="routing",
            duration=route_duration,
            details={"routed_to": target_system}
        )
        except Exception as e:
            print(f"⚠️ Failed to record Routing stage: {e}")
            

        # Update document status to "routed"
        doc_service.update_status(doc_id, "routed")
        # Log routing
        log_service.log_event(
        event_type="INFO",
        message=f"Document routed to {target_system}",
        source="router_agent",
        user_id=uploaded_by,
        document_id=doc_id
        )

        print(f"🚚 Routed to: {target_system}")

if __name__ == "__main__":
    consume_documents()
