"""Session-based auth: POST /login, POST /logout, and the current_admin
dependency that gates every Rack/Item/report endpoint (FR-009)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import get_db
from .models import Admin, verify_password

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


def current_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    admin_id = request.session.get("admin_id")
    if admin_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    admin = db.get(Admin, admin_id)
    if admin is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return admin


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == payload.username).first()
    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["admin_id"] = admin.id
    return {"status": "ok"}


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"status": "ok"}
