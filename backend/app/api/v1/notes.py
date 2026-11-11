from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models import User
from app.repositories import note_repo
from app.schemas import ImportRequest, NoteIn, NoteOut
from app.services import note_service

router = APIRouter()  # every note belongs to, and is visible only to, its owner


def _own(db: Session, user: User, note_id: int):
    note = note_repo.get_note(db, user.id, note_id)
    if not note:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return note


@router.get("/", response_model=List[NoteOut])
def list_notes(q: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return note_repo.list_notes(db, user.id, q)


@router.post("/", response_model=NoteOut, status_code=201)
def create_note(data: NoteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return note_repo.add_note(db, user.id, **data.model_dump())


@router.get("/export")
def export_notes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    notes = note_repo.list_notes(db, user.id)
    if not notes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have no notes to export")
    path = note_service.export_csv(notes)
    return {"path": str(path), "count": len(notes)}


@router.post("/import")
def import_notes(data: ImportRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"imported": note_service.import_csv(db, user.id, data.csv)}


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _own(db, user, note_id)


@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, data: NoteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = _own(db, user, note_id)
    for k, v in data.model_dump().items():
        setattr(note, k, v)
    db.commit()
    return note


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note_repo.delete_note(db, _own(db, user, note_id))
    return {"ok": True}
