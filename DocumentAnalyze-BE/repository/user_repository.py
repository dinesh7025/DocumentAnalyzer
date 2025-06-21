""# repositories/user_repository.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import insert, update, delete, select
from sqlalchemy.exc import SQLAlchemyError
from database.models import User

class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_user_by_username(self, username):
        stmt = select(User).where(User.username == username)
        result = self.db.execute(stmt).scalar_one_or_none()
        return result

    def get_user_by_id(self, user_id):
        stmt = select(User).where(User.id == user_id)
        result = self.db.execute(stmt).scalar_one_or_none()
        return result

    def get_user_id_by_username(self, username):
        user = self.get_user_by_username(username)
        return user.id if user else None
    
    def create_user(self, user_data):
        try:
            new_user = User(**user_data)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Create user error: {e}")
            return None

