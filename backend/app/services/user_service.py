from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User
from app.repositories import user_repo
from app.schemas import UserCreate, UserUpdate


def create_user(db: Session, data: UserCreate) -> User:
    if user_repo.get_by_username(db, data.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    return user_repo.add_user(
        db, username=data.username, full_name=data.full_name,
        password_hash=hash_password(data.password), role=data.role,
    )


def remove_user(db: Session, user_id: int, acting: User) -> None:
    target = user_repo.get_user(db, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if target.id == acting.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot delete your own account")
    if target.role == "admin" and user_repo.count_admins(db) <= 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot delete the last admin")
    user_repo.delete_user(db, target)


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    target = user_repo.get_user(db, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if data.role and data.role != target.role:
        if target.role == "admin" and user_repo.count_admins(db) <= 1:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot demote the last admin")
        target.role = data.role
    if data.full_name is not None:
        target.full_name = data.full_name
    db.commit()
    return target


def reset_password(db: Session, user_id: int, new_password: str) -> None:
    target = user_repo.get_user(db, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    target.password_hash = hash_password(new_password)
    db.commit()
    user_repo.delete_other_sessions(db, target.id)  # force re-login everywhere


def change_own_password(db: Session, user: User, current: str, new: str, keep_token: str) -> None:
    if not verify_password(current, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    user.password_hash = hash_password(new)
    db.commit()
    user_repo.delete_other_sessions(db, user.id, keep_token)
