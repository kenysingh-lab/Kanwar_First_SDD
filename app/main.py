"""FastAPI app instance, middleware, and route registration.

JSON API endpoints live at the paths defined in
specs/001-inventory-tracking/contracts/api.md (/login, /logout, /racks,
/items, /report). The server-rendered UI that wraps those same operations
lives under /ui/*, per plan.md's server-rendered-template decision.
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from . import auth
from .database import get_db
from .models import Admin, Item, Rack
from .routers import dispatch as dispatch_router
from .routers import items as items_router
from .routers import racks as racks_router
from .routers import report as report_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Warehouse Inventory Tracking")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "dev-secret-change-me"),
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(auth.router)
app.include_router(racks_router.router)
app.include_router(items_router.router)
app.include_router(report_router.router)
app.include_router(dispatch_router.router)


def _session_admin(request: Request, db: Session) -> Admin | None:
    admin_id = request.session.get("admin_id")
    if admin_id is None:
        return None
    return db.get(Admin, admin_id)


@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    if _session_admin(request, db) is None:
        return RedirectResponse("/ui/login")
    return RedirectResponse("/ui/racks")


@app.get("/ui/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/ui/racks")
def racks_page(request: Request, db: Session = Depends(get_db)):
    admin = _session_admin(request, db)
    if admin is None:
        return RedirectResponse("/ui/login")
    all_racks = db.query(Rack).order_by(Rack.rack_number).all()
    return templates.TemplateResponse(
        "racks.html",
        {"request": request, "racks": [racks_router.serialize_rack(r) for r in all_racks]},
    )


@app.get("/ui/items")
def items_page(request: Request, db: Session = Depends(get_db)):
    admin = _session_admin(request, db)
    if admin is None:
        return RedirectResponse("/ui/login")
    all_racks = db.query(Rack).order_by(Rack.rack_number).all()
    all_items = db.query(Item).order_by(Item.name).all()
    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "racks": [racks_router.serialize_rack(r) for r in all_racks],
            "items": [
                {**items_router.serialize_item(i), "rack_number": i.rack.rack_number}
                for i in all_items
            ],
        },
    )


@app.get("/ui/report")
def report_page(request: Request, db: Session = Depends(get_db)):
    admin = _session_admin(request, db)
    if admin is None:
        return RedirectResponse("/ui/login")
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "rows": report_router.query_report_rows(db)},
    )


@app.get("/ui/dispatch")
def dispatch_page(request: Request, db: Session = Depends(get_db)):
    admin = _session_admin(request, db)
    if admin is None:
        return RedirectResponse("/ui/login")
    all_items = db.query(Item).order_by(Item.name).all()
    return templates.TemplateResponse(
        "dispatch.html",
        {
            "request": request,
            "items": [
                {**items_router.serialize_item(i), "rack_number": i.rack.rack_number}
                for i in all_items
            ],
        },
    )
