# repository/routing_repository.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import select, desc, update
from database.models import Routing
from datetime import datetime, timezone

class RoutingRepository:
    def __init__(self, db):
        self.db = db

    def create_route(self, routing : Routing):
        self.db.add(routing)
        self.db.commit()
        self.db.refresh(routing)
        return routing
    
    def update_route(self, document_id, new_target, reason):
        stmt = update(Routing).where(Routing.document_id == document_id).values(
            routed_to=new_target,
            timestamp=datetime.now(timezone.utc),
            reason=reason
        )
        self.db.execute(stmt)
        self.db.commit()
