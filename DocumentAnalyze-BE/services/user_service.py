""# services/user_service.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repository.user_repository import UserRepository

class UserService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)

    def get_user_by_username(self, username):
        return self.user_repo.get_user_by_username(username)

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)

    def get_user_id_by_username(self, username):
        return self.user_repo.get_user_id_by_username(username)

    def create_user(self, user_data):
        return self.user_repo.create_user(user_data)
