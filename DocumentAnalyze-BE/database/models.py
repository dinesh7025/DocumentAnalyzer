from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    email = Column(String(255), unique=True)
    role = Column(String(50), default='user')
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="uploader")


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    upload_time = Column(DateTime, default=datetime.utcnow)
    document_type = Column(Text)
    status = Column(String(50), default='pending')
    language = Column(Text)

    uploader = relationship("User", back_populates="documents")
    extracted_text = relationship("DocumentText", back_populates="document", uselist=False)
    errors = relationship("Error", back_populates="document")


class DocumentText(Base):
    __tablename__ = 'document_texts'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'))
    extracted_text = Column(Text, nullable=False)

    document = relationship("Document", back_populates="extracted_text")


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    document_id = Column(Integer, ForeignKey('documents.id'))

    __table_args__ = (
        CheckConstraint("event_type IN ('ERROR', 'INFO', 'WARNING')", name='event_type_check'),
    )


class Error(Base):
    __tablename__ = 'errors'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'))
    error_message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)

    document = relationship("Document", back_populates="errors")
