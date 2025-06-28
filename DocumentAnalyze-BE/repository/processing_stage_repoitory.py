# services/processing_stage_service.py
from datetime import datetime,timezone
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import ProcessingStage
from sqlalchemy import update, select


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
    def update_stage(self, document_id: int, stage: str, duration: float, details: dict):
        try:
            stmt = (
                select(ProcessingStage)
                .where(ProcessingStage.document_id == document_id, ProcessingStage.stage == stage)
            )
            existing = self.db.execute(stmt).scalar_one_or_none()

            if existing:
                existing.duration = duration
                existing.details = details
            else:
                new_stage = ProcessingStage(
                    document_id=document_id,
                    stage=stage,
                    duration=duration,
                    details=details,
                )
                self.db.add(new_stage)

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error Occurred in upsert_stage: {e}")

