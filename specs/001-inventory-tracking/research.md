# Phase 0 Research: Warehouse Inventory Tracking

All Technical Context items were resolved via direct decisions with the user
(tech stack + deployment target); this document records the resulting choices
and rejected alternatives rather than open-ended research.

## Backend framework

- **Decision**: Python 3.11+ with FastAPI
- **Rationale**: Minimal boilerplate for CRUD-style endpoints, built-in
  request validation via type hints, good docs, easy to run locally with
  Uvicorn — matches the "simple and modern" stack choice with the lowest
  operational overhead.
- **Alternatives considered**: Flask (would require adding a validation
  library separately); Django (bundles an admin/ORM/templating stack heavier
  than a single-admin, single-machine tool needs).

## Storage

- **Decision**: SQLite, accessed via SQLAlchemy
- **Rationale**: File-based, zero setup or separate server process — fits a
  single-machine, single-Admin deployment. Backups are just a file copy.
- **Alternatives considered**: PostgreSQL/MySQL (would require running and
  maintaining a separate database server for no concurrency benefit at this
  scale).

## Frontend approach

- **Decision**: Server-rendered pages via Jinja2 templates, with minimal
  vanilla JS where needed (e.g., inline validation feedback)
- **Rationale**: The app is a handful of CRUD forms and one report table — a
  full SPA framework and build pipeline (React/Vue) would add complexity with
  no corresponding benefit for a single-user local tool.
- **Alternatives considered**: React/Vue SPA (rejected — extra build
  tooling, bundlers, and a separate frontend/backend split not justified by
  the feature's scope).

## Testing approach

- **Decision**: pytest + FastAPI's `TestClient`
- **Rationale**: Standard for FastAPI projects; `TestClient` allows
  HTTP-level contract tests without a running server process.
- **Alternatives considered**: `unittest` (more boilerplate, no material
  benefit here).

## Deployment target

- **Decision**: Single local machine in the warehouse office, run via
  `uvicorn`, reached over the local network (LAN) by browser
- **Rationale**: User explicitly chose this over cloud hosting to avoid
  hosting cost/complexity for a single-admin internal tool.
- **Alternatives considered**: Cloud hosting (rejected by user — not needed
  for this scope, adds cost and operational surface area).

## Outcome

No `NEEDS CLARIFICATION` items remain in the Technical Context — all were
resolved by the two decisions above (stack choice, deployment target).
