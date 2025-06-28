# agents/router_agent.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.azure_blob import copy_blob_to_container
from Utils.email_service import send_email_with_attachment
def route_document(doc_type, filename, source_url, user_email=None):
    doc_type = doc_type.strip().lower()

    routing_map = {
        "invoice": "erp",
        "contract": "dms",
        "resume": "email",
        "report": "report"
    }

    system = routing_map.get(doc_type, "unknown")

    if system == "dms":
        try:
            dest_container = "dms-container"
            copy_blob_to_container(source_url, dest_container, filename)
        except Exception as e:
            raise Exception(f"Blob copy failed: {e}")
    elif system == "erp":
        try:
            dest_container = "erp-container"
            copy_blob_to_container(source_url, dest_container, filename)
        except Exception as e:
            raise Exception(f"Blob copy failed: {e}")
    elif system == "report":
        try:
            dest_container = "report-container"
            copy_blob_to_container(source_url, dest_container, filename)
        except Exception as e:
            raise Exception(f"Blob copy failed: {e}")
    elif system == "email":
        if user_email:
            send_email_with_attachment(to_email=user_email, subject="Resume Document", body="Attached is the resume.", attachment_path=source_url, attachment_filename=filename)
    else:
        print("⚠️ Unknown document type. Skipping routing.")

    return system

