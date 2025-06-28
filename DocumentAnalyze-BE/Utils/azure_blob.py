from azure.storage.blob import BlobServiceClient, ContentSettings
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
container_name = os.getenv("AZURE_BLOB_CONTAINER_NAME")

blob_service_client = BlobServiceClient(
    f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)

def upload_file_to_blob(file_stream, filename, content_type="application/octet-stream"):
    blob_name = f"{uuid.uuid4()}_{filename}"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Define content settings to trigger download behavior
    content_settings = ContentSettings(
        content_type=content_type,
        content_disposition=f'attachment; filename="{filename}"'
    )

    # Upload the file with content settings
    blob_client.upload_blob(
        file_stream,
        overwrite=True,
        content_settings=content_settings
    )

    return blob_client.url  # Save this in DB

def copy_blob_to_container(source_url: str, target_container: str, target_filename: str = None) -> str:
    target_filename = target_filename or f"{uuid.uuid4()}_{os.path.basename(source_url)}"

    target_blob_client = blob_service_client.get_blob_client(container=target_container, blob=target_filename)
    target_blob_client.start_copy_from_url(source_url)

    print(f"✅ File copied to container '{target_container}' as '{target_filename}'")
    return target_blob_client.url