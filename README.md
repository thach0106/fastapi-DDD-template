# FastAPI DDD/CQRS/ES Template

This project is a production-ready backend template using FastAPI, Domain-Driven Design (DDD), CQRS, and Event Sourcing.

## Refactor & Enhancements (v2)

1. **Clean Architecture Enforcement**:

   - Routers now decoupled from Application Handlers via `CommandBus` and `QueryBus`.
   - Domain layer strictly isolated.

2. **Event Sourcing (Postgres)**:

   - Events persisted to `domain_events` table (PostgreSQL JSONB).
   - Alembic migrations included.

3. **Core Abstractions**:

   - `CommandBus` / `QueryBus`: With middleware support (Logging).
   - `BaseRepository`: Shared logic for RLAC (`owner_id`) and Multi-tenancy (`tenant_id`).

4. **Authentication Module**:

   - Full JWT implementation (Login, Refresh).
   - `User` Aggregate and Repository.
   - Role-Based Access Control (`src/core/permissions.py`).

5. **DevOps & Testing**:
   - Async Pytest fixtures (`conftest.py`).
   - Celery Task Routing for Domain Events.
   - Pre-start scripts for auto-migration.

## Usage

### 1. Start Services

```bash
docker-compose up -d
```

### 2. Manual Setup (Dev)

```bash
poetry install
bash scripts/prestart.sh  # Runs migrations
poetry run uvicorn src.main:app --reload
```

### 3. Running Tests

```bash
poetry run pytest
```

## Structure

- `src/core/bus.py`: Command/Query Bus implementation.
- `src/core/repository.py`: Base Repository with RLAC.
- `src/modules/auth`: Authentication logic (Tokens, Login).
- `src/modules/users`: User Identity & Profile Management (User Aggregate, Repositories).
- `src/modules/orders`: Orders module using Bus/CQRS.

## Developer Tools

- `make install`: Install dependencies.
- `make dev`: Start dev server.
- `make test`: Run tests.
- `make migrate`: Run alembic migrations.
- `make lint`: Run linters.
