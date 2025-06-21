# repository/log_repository.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Log

class LogRepository:
    def __init__(self, db):
        self.db = db

    def create_log(self, log: Log):
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
