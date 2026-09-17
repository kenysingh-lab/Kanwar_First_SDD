"""Rack endpoints: GET/POST /racks, PATCH /racks/{id} — see contracts/api.md.

used_capacity/remaining_capacity (FR-004) are computed on Rack itself
(see app/models.py); this module only serializes and validates.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import current_admin
from ..database import get_db
from ..models import Rack

router = APIRouter()


class RackCreate(BaseModel):
    rack_number: str
    aisle: str = Field(min_length=1)
    capacity: int = Field(gt=0)


class RackUpdate(BaseModel):
    aisle: str | None = Field(default=None, min_length=1)
    capacity: int | None = Field(default=None, gt=0)


def serialize_rack(rack: Rack) -> dict:
    return {
        "id": rack.id,
        "rack_number": rack.rack_number,
        "aisle": rack.aisle,
        "capacity": rack.capacity,
        "used_capacity": rack.used_capacity,
        "remaining_capacity": rack.remaining_capacity,
    }


@router.get("/racks")
def list_racks(db: Session = Depends(get_db), admin=Depends(current_admin)):
    return [serialize_rack(r) for r in db.query(Rack).order_by(Rack.rack_number).all()]


@router.post("/racks", status_code=201)
def create_rack(payload: RackCreate, db: Session = Depends(get_db), admin=Depends(current_admin)):
    existing = db.query(Rack).filter(Rack.rack_number == payload.rack_number).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="rack_number already exists")
    rack = Rack(rack_number=payload.rack_number, aisle=payload.aisle, capacity=payload.capacity)
    db.add(rack)
    db.commit()
    db.refresh(rack)
    return serialize_rack(rack)


@router.patch("/racks/{rack_id}")
def update_rack(
    rack_id: int,
    payload: RackUpdate,
    db: Session = Depends(get_db),
    admin=Depends(current_admin),
):
    rack = db.get(Rack, rack_id)
    if rack is None:
        raise HTTPException(status_code=404, detail="Rack not found")
    if payload.aisle is not None:
        rack.aisle = payload.aisle
    if payload.capacity is not None:
        rack.capacity = payload.capacity
    db.commit()
    db.refresh(rack)
    return serialize_rack(rack)
