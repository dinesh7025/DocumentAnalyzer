import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer
import json
from agents.classifier_agent import classify_document
from services.document_service import DocumentService
from services.user_service import UserService
from database.base import get_db_connection
from datetime import datetime

def consume_documents():
    db = next(get_db_connection())
    doc_service = DocumentService(db)
    user_service = UserService(db)

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
        uploaded_by_username = data.get("uploaded_by", "")

        if not filename or not extracted_text or not uploaded_by_username:
            print("⚠️ Missing fields in message. Skipping.")
            continue

        doc_type = classify_document(extracted_text)
        print(f"📄 Classified as: {doc_type}")

        # Get user ID from username
        user_id = user_service.get_user_id_by_username(uploaded_by_username)
        if not user_id:
            print(f"❌ User '{uploaded_by_username}' not found. Skipping document.")
            continue

        # Insert document metadata
        document_data = {
            "filename": filename,
            "storage_path": file_url,
            "uploaded_by": user_id,
            "upload_time": datetime.utcnow(),
            "document_type": doc_type,
            "status": "processed"
        }
        doc_id = doc_service.create_document(document_data)

        if doc_id:
            doc_service.add_extracted_text(doc_id, extracted_text)
            print(f"✅ Document stored with ID: {doc_id}")
        else:
            print("❌ Failed to insert document.")

if __name__ == "__main__":
    consume_documents()
