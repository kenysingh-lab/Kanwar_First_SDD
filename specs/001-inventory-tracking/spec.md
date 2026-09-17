# Feature Specification: Warehouse Inventory Tracking

**Feature Branch**: `001-inventory-tracking`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "As an Admin, I want to build a web app that tracks warehouse inventory, so that I can see if I have space for more items in my racks. As an Admin, I want a report in that web app that shows: 1. Item name, 2. Rack number, 3. Quantity."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Track Inventory and Rack Space (Priority: P1)

As the Admin, I want to record which items are stored in which racks and in what
quantities, so that I can tell at a glance whether a rack still has room for
more items before I try to put something new on it.

**Why this priority**: This is the foundational capability. Without recorded
inventory and rack capacity, there is nothing to report on and no way to answer
the core question ("do I have space?"). It delivers value on its own: even a
simple running total per rack is immediately useful on the warehouse floor.

**Independent Test**: Can be fully tested by adding a rack with a defined
capacity, assigning items and quantities to it, and confirming the app
correctly shows remaining space — without any reporting UI built yet.

**Acceptance Scenarios**:

1. **Given** a rack with a defined maximum capacity and no items assigned,
   **When** the Admin views that rack, **Then** the app shows the rack as
   having its full capacity available.
2. **Given** a rack with some capacity already used by assigned items,
   **When** the Admin adds another item to that rack, **Then** the app
   updates the rack's used and remaining capacity to reflect the new item.
3. **Given** a rack that is at full capacity, **When** the Admin attempts to
   assign an additional item to it, **Then** the app warns the Admin that the
   rack has no remaining space before the assignment is confirmed.
4. **Given** items are assigned to a rack, **When** the Admin views the Racks
   page, **Then** each rack shows which items (and their quantities) are
   currently on it, so the Admin doesn't have to cross-reference the Items
   page to know what's where.

---

### User Story 2 - View Inventory Report (Priority: P2)

As the Admin, I want a report listing every item's name, the rack it's stored
in, and its quantity, so that I can review the whole warehouse's contents at a
glance instead of checking racks one by one.

**Why this priority**: This builds directly on User Story 1's data and turns
it into the consolidated view the Admin actually wants to consult day-to-day.
It is not independently useful without inventory data existing first, which is
why it is P2.

**Independent Test**: Can be fully tested by populating a few items across
multiple racks (via User Story 1) and confirming the report lists item name,
rack number, aisle, and quantity for each, matching what was entered.

**Acceptance Scenarios**:

1. **Given** inventory items have been assigned to racks with quantities,
   **When** the Admin opens the report, **Then** every item appears as a row
   showing its name, rack number, aisle, and quantity.
2. **Given** an item's quantity is updated, **When** the Admin re-opens the
   report, **Then** the report reflects the updated quantity without further
   manual action.
3. **Given** no items have been added yet, **When** the Admin opens the
   report, **Then** the report displays an empty state rather than an error.

---

### User Story 3 - Dispatch Items for Delivery (Priority: P3)

As the Admin, I want to dispatch items out of the warehouse, so that a
trucker can deliver them to my customer and the inventory reflects what's
actually still on the shelf.

**Why this priority**: This builds on User Story 1's inventory data and
depends on it existing first, which is why it's P3. It's the action that
actually moves goods out the door, so it matters once there's inventory to
dispatch, but tracking and reporting (P1/P2) have to exist before it does.

**Independent Test**: Can be fully tested by dispatching a valid quantity of
an existing item and confirming its recorded quantity drops accordingly, and
by attempting to dispatch more than is available and confirming it's
rejected with no change to inventory.

**Acceptance Scenarios**:

1. **Given** an item with available quantity, **When** the Admin dispatches
   a quantity at or below what's available, **Then** the item's quantity is
   reduced by that amount and the change is reflected in the Inventory
   Report.
2. **Given** an item with limited quantity, **When** the Admin attempts to
   dispatch more than is currently available, **Then** the app shows the
   error "Item out of quantity" and does not change any inventory data.
3. **Given** a successful dispatch, **When** the Admin opens the Dispatch
   page again, **Then** the item selection reflects the item's updated
   available quantity.

---

### Edge Cases

- What happens when the Admin tries to assign an item to a rack that is
  already at full capacity? (See Acceptance Scenario 3 under User Story 1 —
  the assignment is blocked/warned, not silently allowed to overflow.)
- What happens when an item's quantity is reduced to zero? The item should no
  longer count against its rack's used capacity, but its history of having
  existed is not required to be preserved in this version.
- What happens if the same item name is stored across more than one rack
  (e.g., overflow from a full rack to another)? Each item+rack combination is
  tracked as its own row in the report, so quantities are per-rack, not
  merged across racks.
- What happens when a rack's total capacity is edited after items are already
  assigned to it? The app should recompute remaining space using the new
  capacity and the existing assigned quantity.
- What happens when the Admin renames a rack's number to one that's already
  in use by another rack? The rename is rejected (same uniqueness rule as
  creating a rack, FR-001) rather than silently overwriting the other rack.
- What happens when the Admin tries to dispatch more of an item than is
  currently available? The dispatch is rejected with the error "Item out of
  quantity" and no inventory data changes (no partial dispatch).
- What happens when the Admin dispatches exactly an item's remaining
  quantity? The item's quantity becomes zero (per the existing "quantity
  reduced to zero" edge case above) and the rack capacity it used is freed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow the Admin to create and edit racks, each
  identified by a unique rack number and a maximum capacity (a count of units
  it can hold). Editing includes changing the rack number itself, subject to
  the same uniqueness rule as creating a rack.
- **FR-011**: The system MUST allow the Admin to record which aisle each rack
  belongs to, and to edit that assignment.
- **FR-002**: The system MUST allow the Admin to create and edit inventory
  items, each with a name, a quantity, and an assigned rack.
- **FR-003**: The system MUST allow the Admin to update an item's quantity
  (e.g., when stock is received or shipped out).
- **FR-004**: The system MUST calculate and display, for each rack, the
  capacity currently used and the capacity remaining, based on the quantities
  of items assigned to it.
- **FR-005**: The system MUST warn the Admin when assigning or increasing an
  item's quantity would exceed a rack's remaining capacity.
- **FR-006**: The system MUST prevent item quantities and rack used-capacity
  from going negative.
- **FR-007**: The system MUST provide a report view listing every inventory
  item with its item name, rack number, aisle, and quantity, with one row per
  item-and-rack combination.
- **FR-008**: The report MUST reflect the current state of the inventory at
  the time it is viewed (no manual refresh/export step required to see
  up-to-date data).
- **FR-009**: The system MUST restrict access to inventory data and the
  report to authenticated Admin users.
- **FR-010**: The system MUST allow the Admin to remove an item entirely
  (e.g., a discontinued item), freeing the rack capacity it used.
- **FR-012**: The system MUST provide a Dispatch page where the Admin
  selects an item and a quantity to dispatch out of the warehouse.
- **FR-013**: The system MUST subtract the dispatched quantity from the
  selected item's quantity upon a successful dispatch, and this change MUST
  be reflected in the Inventory Report (FR-007/FR-008).
- **FR-014**: The system MUST reject a dispatch and display the error "Item
  out of quantity" when the requested quantity exceeds the item's currently
  available quantity, making no change to any inventory data.
- **FR-015**: The system MUST show, on the Racks page, which items (name and
  quantity) are currently assigned to each rack.

### Key Entities

- **Rack**: A physical storage location in the warehouse. Key attributes:
  rack number (unique identifier), the aisle it belongs to, maximum capacity,
  and current used capacity (derived from the items assigned to it).
- **Item**: A stock entry stored on a rack. Key attributes: item name,
  quantity, and the rack it is assigned to.
- **Admin**: The authenticated user who manages racks and items and views the
  report. Only one role is in scope for this version.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An Admin can determine whether a given rack has available
  space in under 5 seconds by viewing the app, with no manual counting.
- **SC-002**: The inventory report displays item name, rack number, aisle,
  and quantity for all items, and loads within 3 seconds for a warehouse of
  up to 1,000 tracked items.
- **SC-003**: 100% of quantity or rack-assignment changes made by the Admin
  are reflected the next time the report or rack view is opened.
- **SC-004**: An Admin can identify which racks are at or near full capacity
  without physically inspecting the rack, for 100% of racks recorded in the
  system.
- **SC-005**: 100% of successful dispatches are reflected in the item's
  quantity and the Inventory Report immediately, with no separate refresh
  step, and 100% of over-quantity dispatch attempts are rejected with no
  change to inventory data.

## Assumptions

- A single "Admin" role covers all users of this app in this version; no
  separate warehouse-staff or read-only viewer roles are required yet.
- Rack capacity is tracked as a simple unit count (how many item-units a rack
  can hold), not physical volume, weight, or dimensions.
- Rack numbers/identifiers already exist in the physical warehouse; the app
  records and references them rather than generating or laying out a physical
  floor plan.
- Items are counted in whole units (no fractional/partial quantities).
- The warehouse is small enough for one Admin to manage without needing
  multi-user concurrent-editing controls in this version.
- Aisle is a simple label recorded on each rack (e.g., "Aisle 3"), not a
  separately managed entity with its own capacity or attributes — there is
  no requirement yet for aisle-level rollups, listing, or constraints beyond
  recording which aisle a rack is in.
- Dispatch is a one-time inventory-reducing action; this version does not
  keep a persisted history/log of past dispatches — only the resulting
  change to the item's quantity is retained. A dispatch history/audit trail
  can be added later if that becomes a requirement.
- Dispatch does not capture customer or trucker identifying details in this
  version — only which item and how much quantity left the warehouse.
- Since the same item name can exist as separate rows across different
  racks (per the earlier "same item name across racks" edge case), the
  Dispatch page's item selection operates at that same per-rack row
  granularity, not by item name alone.
