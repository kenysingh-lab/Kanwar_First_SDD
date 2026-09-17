# Quickstart: Warehouse Inventory Tracking

Validation guide for confirming the feature works end-to-end once
implemented. See [data-model.md](data-model.md) for field details and
[contracts/api.md](contracts/api.md) for endpoint shapes.

## Prerequisites

- Python 3.11+
- `pip install -r requirements.txt` (FastAPI, Uvicorn, SQLAlemy, pytest —
  see research.md for why these were chosen)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.database init   # creates the SQLite file + tables
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` (or the machine's LAN IP from another device on
the same network) in a browser and log in as the Admin.

## Validation scenarios

Each scenario below maps to an Acceptance Scenario in [spec.md](spec.md).

1. **Rack starts empty** (User Story 1, Scenario 1)
   - Create a rack with capacity 10.
   - Confirm the rack view shows 10/10 remaining.

2. **Adding an item updates remaining space** (User Story 1, Scenario 2)
   - Add an item with quantity 4 to that rack.
   - Confirm the rack now shows 6 remaining.

3. **Rack at capacity warns before overflow** (User Story 1, Scenario 3)
   - Add another item with quantity 6 to the same rack (now exactly full).
   - Attempt to add one more unit of any item to that rack.
   - Confirm the app surfaces a capacity warning (per `contracts/api.md`)
     before the assignment is saved, and does not silently overflow.

4. **Report lists every item correctly** (User Story 2, Scenario 1)
   - Add items across at least two different racks.
   - Open the report.
   - Confirm every item appears with its item name, rack number, and
     quantity, matching what was entered.

5. **Report reflects updates without extra steps** (User Story 2, Scenario 2)
   - Change an item's quantity.
   - Re-open the report.
   - Confirm the new quantity is shown with no manual refresh/export step.

6. **Empty state before any data exists** (User Story 2, Scenario 3)
   - On a freshly initialized database, open the report before creating any
     racks or items.
   - Confirm an empty-state message is shown rather than an error.

## Expected outcome

All six scenarios pass without needing to inspect the database directly —
everything is observable through the rack view and the report view alone.
