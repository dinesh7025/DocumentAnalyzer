# services/processing_stage_service.py
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import ProcessingStage

class ProcessingStageRepository:
    def __init__(self, db):
        self.db = db

    def add_stage(self, processing_data : ProcessingStage):
        new_stage_data = processing_data
        self.db.add(new_stage_data)
        self.db.commit()
        self.db.refresh(new_stage_data)
        return new_stage_data.id

    def get_stages_for_document(self, document_id: int):
        return (
            self.db.query(ProcessingStage)
            .filter(ProcessingStage.document_id == document_id)
            .order_by(ProcessingStage.start_time.asc())
            .all()
        )
