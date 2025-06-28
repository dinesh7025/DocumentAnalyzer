# services/processing_stage_service.py

from database.models import ProcessingStage
from datetime import datetime
import json
from repository.processing_stage_repoitory import ProcessingStageRepository

class ProcessingStageService:
    def __init__(self, db):
        self.repo = ProcessingStageRepository(db)

    def add_stage(self, document_id: int, stage: str, duration : float, details: dict = None):
        stage_entry = ProcessingStage(
            document_id=document_id,
            stage=stage,
            duration = duration,
            details=json.dumps(details or {})
        )
        return self.repo.add_stage(stage_entry)

    def get_stages_for_document(self, document_id: int):
        return self.get_stages_for_document()
    
    def update_stage(self, document_id: int, stage: str, duration: float, details: dict):
        return self.repo.update_stage(document_id, stage, duration, details)

