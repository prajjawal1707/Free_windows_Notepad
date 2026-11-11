from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import APP_VERSION, settings
from app.db.database import get_db
from app.models import User
from app.models.user import utcnow
from app.repositories import note_repo, user_repo
from app.schemas import DashboardStats

router = APIRouter()


@router.get("/", response_model=DashboardStats)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DashboardStats(
        total_users=user_repo.count_users(db),
        admins=user_repo.count_admins(db),
        active_sessions=user_repo.count_active_sessions(db),
        my_notes=note_repo.count_notes(db, user.id),
        server_time=utcnow(),
        version=APP_VERSION,
        database_path=str(settings.db_path),
    )
