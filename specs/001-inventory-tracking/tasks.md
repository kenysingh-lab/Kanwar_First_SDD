---

description: "Task list for Warehouse Inventory Tracking"
---

# Tasks: Warehouse Inventory Tracking

**Input**: Design documents from `/specs/001-inventory-tracking/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Not explicitly requested in spec.md and no TDD approach was requested, so no
dedicated test tasks are included. `quickstart.md` provides the end-to-end
validation scenarios instead (run in the Polish phase).

**Organization**: Tasks are grouped by user story (US1, US2) from spec.md so each can be
implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- File paths follow the single-project structure from plan.md (`app/`, `tests/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per plan.md: `app/` (with `routers/`, `templates/`, `static/`) at repository root — no `tests/` scaffolding, since no automated test suite was requested (see plan.md Technical Context)
- [X] T002 Initialize Python 3.11+ project with a `requirements.txt` pinning FastAPI, Uvicorn, SQLAlchemy, Jinja2, `python-multipart`, and `passlib[bcrypt]` (for Admin password hashing) per research.md
- [X] T003 [P] Configure linting/formatting (e.g. `ruff` + `black` config) for the `app/` package

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Set up SQLAlchemy engine and session factory against a SQLite file in `app/database.py`, plus a `python -m app.database init` bootstrap command that creates the tables (per quickstart.md Setup)
- [X] T005 [P] Create the `Rack` ORM model in `app/models.py` with fields `rack_number` (string, "unique, required"), `capacity` (integer, "required, must be > 0"), `created_at`, `updated_at` per data-model.md
- [X] T006 [P] Create the `Item` ORM model in `app/models.py` with fields `name` (string, required), `quantity` (integer, "required, must be >= 0"), `rack_id` (FK to `Rack`, required, not nullable), `created_at`, `updated_at` per data-model.md
- [X] T007 [P] Create the `Admin` ORM model in `app/models.py` with fields `username` (string, "unique, required"), `password_hash` (string, "required, never stored/returned in plaintext"), `created_at` per data-model.md
- [X] T008 Implement session-based auth in `app/auth.py`: `POST /login` (sets session cookie, 401 on invalid credentials), `POST /logout` (clears cookie), and a `current_admin` dependency so "Only authenticated Admins can reach any Rack/Item/report endpoint" (FR-009), per contracts/api.md
- [X] T009 Wire up the FastAPI app instance, router registration, Jinja2 template config, and static file serving in `app/main.py` per plan.md's Project Structure

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Track Inventory and Rack Space (Priority: P1) 🎯 MVP

**Goal**: Admin can record items in racks and see, per rack, whether there is
remaining capacity before adding more.

**Independent Test**: Create a rack with a capacity, assign items with
quantities to it, and confirm the app correctly shows used/remaining
capacity — including warning before an assignment would overflow the rack
(quickstart.md scenarios 1-3).

### Implementation for User Story 1

- [X] T010 [US1] Implement rack capacity calculation in `app/routers/racks.py`: `used_capacity` = "sum of `quantity` across all `Item` rows where `rack_id` matches this rack", `remaining_capacity` = `capacity` - `used_capacity`, per data-model.md
- [X] T011 [US1] Implement `GET /racks` and `POST /racks` in `app/routers/racks.py` per contracts/api.md (409 if `rack_number` already exists, 422 if `capacity` is not a positive integer)
- [X] T012 [US1] Implement `PATCH /racks/{id}` in `app/routers/racks.py` per contracts/api.md, recomputing `used_capacity`/`remaining_capacity` after a capacity edit (404 if rack not found)
- [X] T013 [US1] Implement `POST /items` and `PATCH /items/{id}` in `app/routers/items.py` per contracts/api.md, including the capacity-warning soft-block: return 409 with `{"warning": "capacity_exceeded", "remaining_capacity": int}` when an assignment/update would exceed the target rack's remaining capacity, and honor `{"confirm": true}` to force it (FR-005)
- [X] T014 [US1] Implement `GET /items` (with optional `rack_id` filter) and `DELETE /items/{id}` in `app/routers/items.py` per contracts/api.md and FR-010 (remove an item entirely, freeing the rack capacity it used)
- [X] T015 [US1] Add validation guard rails across `app/routers/racks.py` and `app/routers/items.py` so quantity/capacity "cannot be negative" (FR-006) and rack `capacity` "must be a positive integer" are enforced with 422 responses
- [X] T016 [P] [US1] Build rack list/detail templates in `app/templates/racks.html` showing capacity used/remaining per rack, wired to the `GET`/`POST`/`PATCH /racks` endpoints
- [X] T017 [P] [US1] Build item add/edit forms in `app/templates/items.html`, including the capacity-warning confirmation flow, wired to the items endpoints

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Inventory Report (Priority: P2)

**Goal**: Admin can view a single report listing every item's name, rack
number, and quantity.

**Independent Test**: Populate items across multiple racks (via User Story 1),
open the report, and confirm every item appears with the correct name, rack
number, and quantity (quickstart.md scenarios 4-6).

### Implementation for User Story 2

- [X] T018 [US2] Implement `GET /report` in `app/routers/report.py` returning one row per item as `{item_name, rack_number, quantity}` with "no merging across racks" per data-model.md and contracts/api.md
- [X] T019 [US2] Write the report query as a single joined query (Item ⨝ Rack) rather than N+1 lookups, to meet SC-002 ("loads within 3 seconds for a warehouse of up to 1,000 tracked items")
- [X] T020 [P] [US2] Build the report template in `app/templates/report.html` listing item name, rack number, and quantity, with an empty-state message when no items exist yet (spec Acceptance Scenario 3)
- [X] T021 [US2] Wire the report route into `app/main.py`'s navigation alongside the racks/items views

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the whole feature

- [X] T022 [P] Finalize `requirements.txt` versions and add a `README.md` with setup/run instructions mirroring quickstart.md's Setup/Run sections
- [X] T023 [P] Harden auth in `app/auth.py`: session cookies set `httponly`, passwords hashed via `passlib[bcrypt]`, never logged or returned in plaintext (per data-model.md's Admin rules) — verified `httponly; samesite=lax` on the actual `Set-Cookie` header from a running instance
- [X] T024 Run all six quickstart.md validation scenarios end-to-end against a running instance and fix any discrepancies found — all 6 passed (see implementation commit notes)

---

## Phase 6: Add Aisle to Racks (Change Request)

**Purpose**: FR-011 — record which aisle each rack belongs to, and surface it
in the report (FR-007/SC-002 updates)

- [X] T025 Add `aisle` (string, required) to the `Rack` model in `app/models.py` per the updated data-model.md
- [X] T026 Add `aisle` to `RackCreate`/`RackUpdate` schemas and `serialize_rack` in `app/routers/racks.py`, per the updated contracts/api.md (422 if `aisle` missing/empty on create)
- [X] T027 Add `aisle` to the report query and serialized rows in `app/routers/report.py` per the updated contracts/api.md
- [X] T028 [P] Update `app/templates/racks.html`: add an `aisle` input to the add-rack form, an `aisle` column to the racks table, and allow editing it alongside capacity
- [X] T029 [P] Update `app/templates/report.html`: add an `aisle` column
- [X] T030 [P] Update `app/templates/items.html`: show each rack's aisle in the rack-selection dropdown, to help the Admin pick the right rack
- [X] T031 Migrated the live `warehouse.db` in place (`ALTER TABLE racks ADD COLUMN aisle ... DEFAULT 'Unassigned'`) rather than recreating it, since it already held real racks/items from prior use — verified existing rows got the default, new racks require a real `aisle`, and the report/racks/items pages all render it correctly

---

## Phase 7: Edit Rack Number (Change Request)

**Purpose**: FR-001 update — let the Admin rename a rack's `rack_number` from
the Racks page, not just set it at creation

- [X] T032 Add `rack_number` to `RackUpdate` in `app/routers/racks.py`; in `update_rack`, if changing it, check for a conflicting rack (409, same rule as create) before applying, per the updated contracts/api.md
- [X] T033 [P] Update `app/templates/racks.html`: make the Rack Number cell an editable input (like aisle/capacity already are) and include it in the save request
- [X] T034 Manually verify: rename a rack to a free number (succeeds), rename a rack to another existing rack's number (rejected, both racks keep their original numbers), and confirm the report/items dropdown reflect the new number afterward — all verified against the running instance

**Checkpoint**: Rack number is editable from the Racks page, with the same uniqueness guarantee as creation

---

## Phase 8: Dispatch Items for Delivery (User Story 3, Priority: P3)

**Goal**: Admin can dispatch a quantity of an item out of the warehouse from
a dedicated Dispatch page; the item's quantity drops accordingly and the
Inventory Report reflects it immediately; over-quantity dispatches are
rejected with "Item out of quantity".

**Independent Test**: Dispatch a valid quantity of an existing item and
confirm its quantity drops and the report updates; attempt to dispatch more
than available and confirm it's rejected with no inventory change.

### Implementation for User Story 3

- [X] T035 Create `app/routers/dispatch.py` with `POST /dispatch` per contracts/api.md: validate `quantity` is a positive integer and `item_id` exists (422 otherwise); if `quantity` exceeds the item's current `quantity`, return 409 with `{"error": "Item out of quantity"}` (FR-014) and make no changes; otherwise subtract `quantity` from the item and return the updated item (FR-013)
- [X] T036 Register the dispatch router in `app/main.py` and add a `GET /ui/dispatch` page route (auth-gated like the other `/ui/*` pages) that lists current items for the dropdown
- [X] T037 [P] Build `app/templates/dispatch.html`: an item dropdown (name + rack number + available quantity, matching the items page's dropdown style), a quantity input, and a submit button wired via fetch to `POST /dispatch`, showing the exact error text "Item out of quantity" on a 409
- [X] T038 [P] Add a "Dispatch" link to the nav in `app/templates/base.html`, alongside Racks/Items/Report
- [X] T039 Manually verify against the running instance: dispatching a valid quantity reduces the item and shows up in `/report`; dispatching more than available is rejected with "Item out of quantity" and the report is unchanged; dispatching the exact remaining quantity zeroes the item out and frees its rack's capacity — all verified live

**Checkpoint**: User Story 3 is fully functional and independently testable

**Checkpoint**: Racks have an aisle, visible when creating/editing a rack and in the report

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion; reads `Rack`/`Item` data that User Story 1's endpoints create, but its own endpoint/template work has no code dependency on US1's router files
- **Polish (Phase 5)**: Depends on User Story 1 and User Story 2 both being complete

### Within Each User Story

- Router/endpoint logic before templates that call it
- `racks.py` capacity logic (T010) before endpoints that expose it (T011, T012)
- Both user stories depend on the Foundational models (T005-T007) and auth (T008)

### Parallel Opportunities

- T005, T006, T007 (the three ORM models) can run in parallel — different model classes, though same file `app/models.py` (coordinate if working in parallel to avoid merge conflicts)
- T016 and T017 (rack and item templates) can run in parallel — different files
- T020 (report template) can run in parallel with T018/T019 once the report route's response shape is agreed
- T022 and T023 in Polish can run in parallel — different files

---

## Parallel Example: User Story 1

```bash
# Once T010-T015 (racks.py / items.py logic) are done, templates can proceed together:
Task: "Build rack list/detail templates in app/templates/racks.html"
Task: "Build item add/edit forms in app/templates/items.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run quickstart.md scenarios 1-3 independently
5. Demo if ready — this alone answers "do I have space for more items?"

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Validate independently → Demo (MVP!)
3. Add User Story 2 → Validate independently → Demo
4. Polish → Full quickstart.md validation pass

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No test tasks were generated because tests were not explicitly requested in
  spec.md; `quickstart.md`'s scenarios serve as the validation pass instead (T024)
- Commit after each task or logical group
- Stop at each checkpoint to validate the story independently before moving on
