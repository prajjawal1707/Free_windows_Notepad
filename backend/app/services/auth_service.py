from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, new_session_token, verify_password
from app.models import User
from app.models.user import utcnow
from app.repositories import user_repo
from app.schemas import RegisterRequest

SESSION_LIFETIME = timedelta(days=30)


def register_first_user(db: Session, data: RegisterRequest) -> User:
    if user_repo.count_users(db) > 0:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Setup already completed. Ask an admin to create your account.")
    return user_repo.add_user(
        db, username=data.username, full_name=data.full_name,
        password_hash=hash_password(data.password), role="admin",
    )


def login(db: Session, username: str, password: str):
    user = user_repo.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")
    token = new_session_token()
    user_repo.add_session(db, token, user.id, utcnow() + SESSION_LIFETIME)
    return token, user


def user_from_token(db: Session, token: str) -> Optional[User]:
    session = user_repo.get_session(db, token)
    if not session:
        return None
    if session.expires_at < utcnow():
        user_repo.delete_session(db, token)
        return None
    return user_repo.get_user(db, session.user_id)


def logout(db: Session, token: str) -> None:
    user_repo.delete_session(db, token)
