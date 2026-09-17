"""Report endpoint: GET /report — item name, rack number, quantity per row.

query_report_rows() is a single joined query (Item join Rack) rather than
per-item lookups, to meet SC-002 (loads within 3s for up to 1,000 items).
No merging across racks: each Item row is its own report row.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import current_admin
from ..database import get_db
from ..models import Item, Rack

router = APIRouter()


def query_report_rows(db: Session) -> list[dict]:
    rows = (
        db.query(Item.name, Rack.rack_number, Item.quantity)
        .join(Rack, Item.rack_id == Rack.id)
        .order_by(Rack.rack_number, Item.name)
        .all()
    )
    return [
        {"item_name": name, "rack_number": rack_number, "quantity": quantity}
        for name, rack_number, quantity in rows
    ]


@router.get("/report")
def get_report(db: Session = Depends(get_db), admin=Depends(current_admin)):
    return query_report_rows(db)
