# API Contract: Warehouse Inventory Tracking

Session-based auth (login required for every endpoint below except
`/login`). All request/response bodies are JSON unless noted; HTML pages
returned by the server-rendered UI wrap these same operations.

## Auth

### `POST /login`
- Request: `{ "username": string, "password": string }`
- Response `200`: session cookie set
- Response `401`: invalid credentials

### `POST /logout`
- Response `200`: session cookie cleared

## Racks

### `GET /racks`
- Response `200`: array of
  `{ id, rack_number, aisle, capacity, used_capacity, remaining_capacity }`
  (Supports User Story 1 — Admin sees remaining space per rack.)

### `POST /racks`
- Request: `{ "rack_number": string, "aisle": string, "capacity": int }`
- Response `201`: created rack object
- Response `409`: `rack_number` already exists
- Response `422`: `capacity` not a positive integer, or `aisle` missing/empty

### `PATCH /racks/{id}`
- Request: `{ "rack_number"?: string, "aisle"?: string, "capacity"?: int }`
- Response `200`: updated rack object (recomputed `used_capacity`/
  `remaining_capacity` per data-model.md)
- Response `404`: rack not found
- Response `409`: `rack_number` already in use by another rack

## Items

### `GET /items`
- Query params: optional `rack_id` filter
- Response `200`: array of `{ id, name, quantity, rack_id }`

### `POST /items`
- Request: `{ "name": string, "quantity": int, "rack_id": int }`
- Response `201`: created item object
- Response `409` (soft-block, confirmable): assigning this quantity would
  exceed the target rack's remaining capacity — response includes
  `{ "warning": "capacity_exceeded", "remaining_capacity": int }`; client
  must resubmit with `{ "confirm": true }` to force the assignment
  (FR-005 — Admin is warned, not silently blocked)
- Response `422`: `quantity` negative, or `rack_id` does not exist

### `PATCH /items/{id}`
- Request: `{ "quantity"?: int, "rack_id"?: int }`
- Same capacity-warning behavior as `POST /items` when the update would
  exceed the target rack's capacity
- Response `200`: updated item object
- Response `404`: item not found

### `DELETE /items/{id}`
- Response `204`: item removed
- Response `404`: item not found

## Report

### `GET /report`
- Response `200`: array of `{ item_name, rack_number, aisle, quantity }`,
  one row per item (per data-model.md — no merging across racks)
- Supports User Story 2 in full: this is the entire contract needed for the
  report view (SC-002: MUST respond fast enough to render within 3s for up
  to 1,000 items).
