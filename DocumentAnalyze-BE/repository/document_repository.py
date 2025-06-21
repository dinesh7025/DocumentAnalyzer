import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database.models import Document, DocumentText

class DocumentRepository:
    def __init__(self, db):
        self.db = db

    def insert_document(self, document_data):
        try:
            new_doc = Document(**document_data)
            self.db.add(new_doc)
            self.db.commit()
            self.db.refresh(new_doc)  # So we can get the auto-generated ID
            return new_doc.id
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Insert error: {e}")
            return None

    def insert_extracted_text(self, document_id, extracted_text):
        try:
            new_text = DocumentText(document_id=document_id, extracted_text=extracted_text)
            self.db.add(new_text)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Text insert error: {e}")
            return False

    def update_document(self, document_id, updates):
        try:
            stmt = select(Document).where(Document.id == document_id)
            doc = self.db.execute(stmt).scalar_one_or_none()
            if doc:
                for key, value in updates.items():
                    setattr(doc, key, value)
                self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Update error: {e}")

    def delete_document(self, document_id):
        try:
            stmt = select(Document).where(Document.id == document_id)
            doc = self.db.execute(stmt).scalar_one_or_none()
            if doc:
                self.db.delete(doc)
                self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Delete error: {e}")

    def get_document_by_id(self, document_id):
        stmt = select(Document).where(Document.id == document_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_documents(self):
        stmt = select(Document)
        return self.db.execute(stmt).scalars().all()
    
    def update_status(self, document_id, status):
        doc = self.db.query(Document).filter_by(id=document_id).first()
        if doc:
            doc.status = status
            self.db.commit()
            return True
        return False

