# services/document_service.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repository.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, db):
        self.repo = DocumentRepository(db)

    def create_document(self, document_data):
        return self.repo.insert_document(document_data)

    def add_extracted_text(self, document_id, extracted_text):
        return self.repo.insert_extracted_text(document_id, extracted_text)

    def update_document(self, document_id, updates):
        self.repo.update_document(document_id, updates)

    def delete_document(self, document_id):
        self.repo.delete_document(document_id)

    def get_document(self, document_id):
        return self.repo.get_document_by_id(document_id)

    def list_documents(self):
        return self.repo.get_all_documents()
