from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models import User
from app.repositories import user_repo
from app.schemas import SettingsPayload

router = APIRouter()


@router.get("/", response_model=Dict[str, str])
def get_settings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return user_repo.get_settings(db)


@router.put("/", response_model=Dict[str, str])
def put_settings(payload: SettingsPayload, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    user_repo.set_settings(db, payload.values)
    return user_repo.get_settings(db)
