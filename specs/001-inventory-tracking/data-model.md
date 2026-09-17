# Phase 1 Data Model: Warehouse Inventory Tracking

Derived from the Key Entities in [spec.md](spec.md) and the Functional
Requirements (FR-001 through FR-009).

## Rack

Represents a physical storage location in the warehouse.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK | auto-generated |
| `rack_number` | string | unique, required (FR-001) |
| `aisle` | string | required (FR-011) |
| `capacity` | integer | required, must be > 0 (FR-001) |
| `created_at` | datetime | auto-set on create |
| `updated_at` | datetime | auto-set on update |

**Derived value** (not stored, computed on read):
- `used_capacity` = sum of `quantity` across all `Item` rows where `rack_id`
  matches this rack (FR-004)
- `remaining_capacity` = `capacity` - `used_capacity`

**Validation rules**:
- `capacity` must be a positive integer (edge case: editing capacity below
  current `used_capacity` is allowed rather than rejected — the Admin made
  the edit intentionally, e.g. to correct a data-entry mistake. This simply
  makes `remaining_capacity` negative; per FR-005, the Admin is warned the
  next time an assignment to that rack would exceed it, matching the spec's
  requirements exactly rather than introducing a separate persistent
  over-capacity flag).

## Item

Represents a stock entry stored on a rack.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK | auto-generated |
| `name` | string | required (FR-002) |
| `quantity` | integer | required, must be >= 0 (FR-002, FR-006) |
| `rack_id` | integer, FK → Rack.id | required (FR-002) |
| `created_at` | datetime | auto-set on create |
| `updated_at` | datetime | auto-set on update |

**Validation rules**:
- `quantity` cannot be negative (FR-006).
- Assigning an item to a rack, or increasing its quantity, when doing so
  would push the rack's `used_capacity` above its `capacity` MUST trigger a
  warning to the Admin before the change is confirmed (FR-005). This is a
  soft gate (confirmable), not a hard block, since the Admin may need to
  record real-world overflow.
- The same `name` may appear in multiple `Item` rows across different racks
  (edge case in spec: overflow item split across racks) — each row is
  tracked independently; no merging/deduplication by name.
- A dispatch (FR-012/FR-013) decreases `quantity` by the dispatched amount,
  subject to the same "cannot be negative" rule (FR-006): a dispatch request
  exceeding the current `quantity` MUST be rejected outright (FR-014, "Item
  out of quantity"), not partially applied or allowed to go negative. Unlike
  the capacity-warning soft gate above, this has no confirm-to-override path
  — you cannot dispatch stock that doesn't exist.

## Admin

Represents the authenticated user who manages racks and items.

| Field | Type | Rules |
|---|---|---|
| `id` | integer, PK | auto-generated |
| `username` | string | unique, required |
| `password_hash` | string | required, never stored/returned in plaintext |
| `created_at` | datetime | auto-set on create |

**Validation rules**:
- Only authenticated Admins can reach any Rack/Item/report endpoint (FR-009).
- Single role in scope for this version — no separate permission levels.

## Relationships

- `Rack 1 ── * Item`: one rack has zero or more items; every item belongs to
  exactly one rack (`rack_id` is required, not nullable).
- `Admin` has no direct relationship to `Rack`/`Item` beyond being the
  authenticated actor performing all operations (single-role system).

## State Transitions

No multi-step lifecycle beyond simple field updates:
- Item quantity changes value (received/shipped) — no distinct "state",
  just a numeric update.
- An item reaching `quantity = 0` remains a row (per spec Edge Cases: history
  is not required to be preserved, but rows are not required to be deleted
  either) — deletion is an explicit Admin action, not automatic.
