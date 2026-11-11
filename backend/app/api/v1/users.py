from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.database import get_db
from app.models import User
from app.repositories import user_repo
from app.schemas import PasswordReset, UserCreate, UserOut, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return user_repo.list_users(db)


@router.post("/", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return user_service.create_user(db, data)


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return user_service.update_user(db, user_id, data)


@router.put("/{user_id}/password")
def reset_password(user_id: int, data: PasswordReset, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user_service.reset_password(db, user_id, data.new_password)
    return {"ok": True}


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user_service.remove_user(db, user_id, admin)
    return {"ok": True}
