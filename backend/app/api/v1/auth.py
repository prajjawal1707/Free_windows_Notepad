from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_session_token
from app.db.database import get_db
from app.models import User
from app.repositories import user_repo
from app.schemas import AuthStatus, LoginRequest, LoginResponse, PasswordChange, RegisterRequest, UserOut
from app.services import auth_service, user_service

router = APIRouter()


@router.get("/status", response_model=AuthStatus)
def auth_status(db: Session = Depends(get_db)):
    return AuthStatus(has_users=user_repo.count_users(db) > 0)


@router.post("/register", response_model=LoginResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """First-run setup only: creates the initial admin account."""
    auth_service.register_first_user(db, data)
    token, user = auth_service.login(db, data.username, data.password)
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token, user = auth_service.login(db, data.username, data.password)
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@router.post("/logout")
def logout(token: str = Depends(get_session_token), db: Session = Depends(get_db)):
    auth_service.logout(db, token)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/change-password")
def change_password(data: PasswordChange, user: User = Depends(get_current_user),
                    token: str = Depends(get_session_token), db: Session = Depends(get_db)):
    user_service.change_own_password(db, user, data.current_password, data.new_password, token)
    return {"ok": True}
