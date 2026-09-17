# Warehouse Inventory Tracking

A single-admin web app for tracking warehouse inventory: items are assigned
to racks with quantities, each rack has a defined capacity so you can see
remaining space at a glance, and a report view lists every item's name, rack
number, and quantity.

See [specs/001-inventory-tracking/](specs/001-inventory-tracking/) for the
full spec, plan, data model, and API contract this was built from.

## Prerequisites

- Python 3.11+ (developed and tested against 3.12)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.database init   # creates warehouse.db and a default Admin
```

The default Admin account is `admin` / `admin` — override before first run
with the `ADMIN_USERNAME`/`ADMIN_PASSWORD` environment variables if you want
different credentials from the start; there is no in-app way to change the
password afterward in this version.

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` (or the machine's LAN IP from another device on
the same network) in a browser and log in.

## Validation

See [specs/001-inventory-tracking/quickstart.md](specs/001-inventory-tracking/quickstart.md)
for the end-to-end scenarios used to confirm the feature works.
