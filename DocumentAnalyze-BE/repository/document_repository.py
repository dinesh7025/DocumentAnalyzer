import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError
from database.models import Document, DocumentText
from sqlalchemy.orm import joinedload




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

    def get_documents_by_user(self, user_id):
        try:
            stmt = (
                select(Document)
                .options(
                    joinedload(Document.uploader),
                    joinedload(Document.stages)
                )
                .where(Document.uploaded_by == user_id)
                .order_by(desc(Document.upload_time))
            )
            return self.db.execute(stmt).unique().scalars().all()
        except SQLAlchemyError as e:
            print(f"Get by user error: {e}")
            return []

    def get_all_documents_with_details(self):
        try:
            stmt = (
                select(Document)
                .options(
                    joinedload(Document.uploader),
                    joinedload(Document.extracted_text),
                    joinedload(Document.stages)
                )
                .order_by(desc(Document.upload_time))
            )
            return self.db.execute(stmt).unique().scalars().all()
        except SQLAlchemyError as e:
            print(f"Get all error: {e}")
            return []
        
    def update_status(self, document_id, status):
        doc = self.db.query(Document).filter_by(id=document_id).first()
        if doc:
            doc.status = status
            self.db.commit()
            return True
        return False

    def delete_document(self, document_id):
        try:
            doc = self.db.query(Document).filter_by(id=document_id).first()
            if doc:
                # Delete related entries manually if not using cascade
                if doc.extracted_text:
                    self.db.delete(doc.extracted_text)
                for error in doc.errors:
                    self.db.delete(error)
                for route in doc.routing:
                    self.db.delete(route)

                self.db.delete(doc)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Delete error: {e}")
            return False
