# services/user_service.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.user_repository import UserRepository  # ✅ Required
from database.models import User


class UserService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user_by_username(self, username):
        return self.user_repo.get_user_by_username(username)

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)

    def get_user_id_by_username(self, username):
        return self.user_repo.get_user_id_by_username(username)

    def create_user(self, user_data):
        return self.user_repo.create_user(user_data)

    def update_app_credentials(self, user_id, app_email, app_password):
        user = self.db.query(User).filter_by(id=user_id).first()
        if user:
            user.app_email = app_email
            user.app_password = app_password
            self.db.commit()
