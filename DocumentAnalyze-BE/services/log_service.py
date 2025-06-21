# services/log_service.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import g  # Import g to access user info
from database.models import Log
from repository.log_repository import LogRepository

class LogService:
    def __init__(self, db):
        self.log_repo = LogRepository(db)

    def log_event(self, event_type, message, source, document_id, user_id=None):
        if user_id is None and has_request_context():
            user_id = getattr(g, 'user_id', None)

        new_log = Log(
            event_type=event_type,
            message=message,
            source=source,
            user_id=user_id,
            document_id=document_id
        )
        return self.log_repo.create_log(new_log)
