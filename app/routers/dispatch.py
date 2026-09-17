"""Dispatch endpoint: POST /dispatch — subtract quantity from an item to
send it out with a trucker for delivery. See contracts/api.md.

FR-014: a request exceeding the item's current quantity is a hard
rejection (409, "Item out of quantity") — no confirm-to-override, unlike
the capacity-warning soft-block on item creation/update.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import current_admin
from ..database import get_db
from ..models import Item
from .items import serialize_item

router = APIRouter()


class DispatchRequest(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)


@router.post("/dispatch")
def dispatch_item(
    payload: DispatchRequest,
    db: Session = Depends(get_db),
    admin=Depends(current_admin),
):
    item = db.get(Item, payload.item_id)
    if item is None:
        raise HTTPException(status_code=422, detail="item_id does not exist")

    if payload.quantity > item.quantity:
        return JSONResponse(status_code=409, content={"error": "Item out of quantity"})

    item.quantity -= payload.quantity
    db.commit()
    db.refresh(item)
    return serialize_item(item)
