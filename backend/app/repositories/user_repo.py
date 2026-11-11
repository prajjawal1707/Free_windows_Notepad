from typing import Dict, List, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import AppSetting, AuthSession, Note, User
from app.models.user import utcnow


def count_users(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(User)) or 0


def count_admins(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(User).where(User.role == "admin")) or 0


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.scalar(select(User).where(func.lower(User.username) == username.lower()))


def list_users(db: Session) -> List[User]:
    return list(db.scalars(select(User).order_by(User.id)))


def add_user(db: Session, **fields) -> User:
    user = User(**fields)
    db.add(user)
    db.commit()
    return user


def delete_user(db: Session, user: User) -> None:
    db.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    db.execute(delete(Note).where(Note.user_id == user.id))
    db.delete(user)
    db.commit()


def add_session(db: Session, token: str, user_id: int, expires_at) -> None:
    db.add(AuthSession(token=token, user_id=user_id, expires_at=expires_at))
    db.commit()


def get_session(db: Session, token: str) -> Optional[AuthSession]:
    return db.get(AuthSession, token)


def delete_session(db: Session, token: str) -> None:
    db.execute(delete(AuthSession).where(AuthSession.token == token))
    db.commit()


def count_active_sessions(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(AuthSession).where(AuthSession.expires_at > utcnow())) or 0


def get_settings(db: Session) -> Dict[str, str]:
    return {s.key: s.value or "" for s in db.scalars(select(AppSetting))}


def set_settings(db: Session, values: Dict[str, str]) -> None:
    for key, value in values.items():
        db.merge(AppSetting(key=key, value=value))
    db.commit()


def delete_other_sessions(db: Session, user_id: int, keep_token: Optional[str] = None) -> None:
    stmt = delete(AuthSession).where(AuthSession.user_id == user_id)
    if keep_token:
        stmt = stmt.where(AuthSession.token != keep_token)
    db.execute(stmt)
    db.commit()
