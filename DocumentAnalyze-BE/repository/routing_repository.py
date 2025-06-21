# repository/routing_repository.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Routing

class RoutingRepository:
    def __init__(self, db):
        self.db = db

    def create_route(self, routing : Routing):
        self.db.add(routing)
        self.db.commit()
        self.db.refresh(routing)
        return routing