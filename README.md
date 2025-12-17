# FastAPI DDD/CQRS/ES Template

This project is a production-ready backend template using FastAPI, Domain-Driven Design (DDD), CQRS, and Event Sourcing.

## Tech Stack

- **Framework**: FastAPI (Async)
- **Database**: PostgreSQL (Async SQLAlchemy 2.0)
- **Migrations**: Alembic
- **Caching**: Redis
- **Tasks**: Celery
- **Auth**: JWT + RLAC
- **Dependency Management**: Poetry

## Project Structure

- `src/core`: Configuration, Database, Security.
- `src/modules`: Domain modules (e.g., `orders`).
  - `domain`: Pure business logic (Aggregates, Events).
  - `application`: Use cases (Commands, Queries, Handlers).
  - `infrastructure`: Database implementation, External adapters.
  - `presentation`: API Routers, Schemas.

## Architecture Patterns

### Domain-Driven Design (DDD)

The core logic resides in `domain/`. It does not depend on frameworks.
Aggregates like `Order` control consistency.

### CQRS (Command Query Responsibility Segregation)

- **Commands**: Modify state (`CreateOrderCommand`). Handled by `CreateOrderHandler`.
- **Queries**: Read state (`GetOrderQuery`). Handled by `GetOrderHandler`.

### Event Sourcing (Basics)

State changes emit events (`OrderCreated`).
The `Order` aggregate records events.
Infrastructure persists these events (Currently `InMemoryEventStore`, extensible to DB).

## How to Run

### Using Docker (Recommended)

```bash
docker-compose up --build
```

### Local Development

1. Install dependencies:
   ```bash
   poetry install
   ```
2. Run database (e.g. via Docker):
   ```bash
   docker-compose up -d db redis
   ```
3. Run app:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```

## Adding a New Module

1. Create `src/modules/<module_name>`.
2. Replicate `domain`, `application`, `infrastructure`, `presentation` structure.
3. Register router in `src/main.py`.
