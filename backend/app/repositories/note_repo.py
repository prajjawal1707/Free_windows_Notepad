from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Note


def count_notes(db: Session, user_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Note).where(Note.user_id == user_id)) or 0


def list_notes(db: Session, user_id: int, q: str = "") -> List[Note]:
    stmt = select(Note).where(Note.user_id == user_id)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.content.ilike(like), Note.tags.ilike(like)))
    stmt = stmt.order_by(Note.pinned.desc(), Note.updated_at.desc(), Note.id.desc())
    return list(db.scalars(stmt))


def get_note(db: Session, user_id: int, note_id: int) -> Optional[Note]:
    return db.scalar(select(Note).where(Note.id == note_id, Note.user_id == user_id))


def add_note(db: Session, user_id: int, **fields) -> Note:
    note = Note(user_id=user_id, **fields)
    db.add(note)
    db.commit()
    return note


def add_many(db: Session, user_id: int, rows: List[dict]) -> int:
    db.add_all([Note(user_id=user_id, **r) for r in rows])
    db.commit()
    return len(rows)


def delete_note(db: Session, note: Note) -> None:
    db.delete(note)
    db.commit()
