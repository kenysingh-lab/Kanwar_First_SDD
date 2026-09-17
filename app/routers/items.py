"""Item endpoints: GET/POST /items, PATCH /items/{id}, DELETE /items/{id}.

See contracts/api.md for the capacity-warning soft-block behavior (FR-005)
and FR-006 (no negative quantities) / FR-010 (remove an item entirely).
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import current_admin
from ..database import get_db
from ..models import Item, Rack

router = APIRouter()


class ItemCreate(BaseModel):
    name: str
    quantity: int = Field(ge=0)
    rack_id: int
    confirm: bool = False


class ItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=0)
    rack_id: int | None = None
    confirm: bool = False


def serialize_item(item: Item) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "quantity": item.quantity,
        "rack_id": item.rack_id,
    }


def _remaining_capacity_after(rack: Rack, item: Item | None, new_quantity: int) -> int:
    """remaining_capacity that WOULD result if item were set to new_quantity on rack."""
    current_quantity_on_rack = item.quantity if item is not None and item.rack_id == rack.id else 0
    used_without_this_item = rack.used_capacity - current_quantity_on_rack
    return rack.capacity - used_without_this_item - new_quantity


@router.get("/items")
def list_items(
    rack_id: int | None = None,
    db: Session = Depends(get_db),
    admin=Depends(current_admin),
):
    query = db.query(Item)
    if rack_id is not None:
        query = query.filter(Item.rack_id == rack_id)
    return [serialize_item(i) for i in query.order_by(Item.name).all()]


@router.post("/items", status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db), admin=Depends(current_admin)):
    rack = db.get(Rack, payload.rack_id)
    if rack is None:
        raise HTTPException(status_code=422, detail="rack_id does not exist")

    remaining_after = _remaining_capacity_after(rack, None, payload.quantity)
    if remaining_after < 0 and not payload.confirm:
        return JSONResponse(
            status_code=409,
            content={"warning": "capacity_exceeded", "remaining_capacity": rack.remaining_capacity},
        )

    item = Item(name=payload.name, quantity=payload.quantity, rack_id=payload.rack_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_item(item)


@router.patch("/items/{item_id}")
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    admin=Depends(current_admin),
):
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    new_quantity = payload.quantity if payload.quantity is not None else item.quantity
    new_rack_id = payload.rack_id if payload.rack_id is not None else item.rack_id
    rack = db.get(Rack, new_rack_id)
    if rack is None:
        raise HTTPException(status_code=422, detail="rack_id does not exist")

    remaining_after = _remaining_capacity_after(rack, item, new_quantity)
    if remaining_after < 0 and not payload.confirm:
        return JSONResponse(
            status_code=409,
            content={"warning": "capacity_exceeded", "remaining_capacity": rack.remaining_capacity},
        )

    item.quantity = new_quantity
    item.rack_id = new_rack_id
    db.commit()
    db.refresh(item)
    return serialize_item(item)


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), admin=Depends(current_admin)):
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return Response(status_code=204)
