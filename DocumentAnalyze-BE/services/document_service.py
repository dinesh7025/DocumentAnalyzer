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

    def get_all_documents(self):
        return self.repo.get_all_documents_with_details()

    def get_documents_by_user(self, user_id):
        return self.repo.get_documents_by_user(user_id)
    
    def get_document_by_id(self, doc_id):
        return self.repo.get_documment_by_id(doc_id)
    
    def update_status(self, doc_id, status):
        return self.repo.update_status(doc_id, status)
    
    def update_extracted_text(self, document_id: int, new_text: str):
        return self.repo.update_extracted_text(document_id, new_text)


    def delete_document(self, document_id):
        return self.repo.delete_document(document_id)

