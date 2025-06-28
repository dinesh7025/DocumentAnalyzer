# services/routing_service.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.routing_repository import RoutingRepository
from database.models import Routing

class RoutingService:
    def __init__(self, db):
        self.routing_repo = RoutingRepository(db)

    def add_route(self, document_id, target_system, reason=None):
        route = Routing(
            document_id=document_id,
            routed_to=target_system,
            reason="Routed by router_agent"
        )
        return self.routing_repo.create_route(route)

    def update_route(self, documnet_id, target_system, reason):
        return self.routing_repo.update_route(documnet_id, target_system, reason)