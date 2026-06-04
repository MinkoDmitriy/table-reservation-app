# Project Overview: Table Reservation & Food Ordering App

This is a FastAPI-based backend application for managing table reservations and pre-ordering food in various food places (restaurants, cafes, etc.). The project follows a modular architecture and supports a complete flow from browsing menu items to placing reservations and food orders.

## Core Technologies
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **ORM:** [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) (Asynchronous)
- **Database:** [PostgreSQL](https://www.postgresql.org/) (via `asyncpg`)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Validation & Settings:** [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Authentication:** JWT (JSON Web Tokens) with `pyjwt` and `passlib` (bcrypt)
- **Testing:** `pytest` with `pytest-asyncio`

## Key Functionality
- **User Management:** Registration, authentication, and role-based access (admin/user).
- **Location & Food Places:** Management of geographical locations and the food places within them.
- **Menu Management:** Detailed menu items associated with specific food places.
- **Food Basket & Ordering:**
    - Users can add items from a specific food place to their basket.
    - Baskets are per-user and per-food-place.
    - Ability to "order" a basket, which marks it as finalized with a timestamp.
- **Table Reservations:** Management of tables within food places and handling reservation requests.

## Project Structure
```text
src/
├── api_routers/    # API endpoints grouped by resource (auth, food_basket, reservation, etc.)
├── models/         # SQLAlchemy ORM models (User, FoodBasket, MenuItem, etc.)
├── schemas/        # Pydantic models for request/response validation
├── config.py       # Configuration and environment variables management
├── database.py     # Database engine and session factory setup
├── main.py         # Application entry point and router inclusion
├── security.py     # Authentication, JWT logic, and security dependencies
└── utils.py        # Shared utility functions
alembic/            # Database migration scripts and environment setup
```

## Setup and Installation

### 1. Environment Configuration
Create a `.env` file in the project root with the following variables:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_user
DB_PASS=your_password
DB_NAME=your_db_name

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Migrations
Apply migrations to the database:
```bash
alembic upgrade head
```

### 4. Running the Application
Start the development server:
```bash
uvicorn src.main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

## Development Conventions
- **Asynchronous Code:** All database operations and route handlers should be `async`.
- **Dependency Injection:** Use `Annotated` with `Depends` for database sessions (`db_dep`) and security (`actual_user_id_dep`, `only_admin_dep`).
- **Models & Schemas:** Maintain a strict separation between ORM models (`src/models/`) and Pydantic schemas (`src/schemas/`).
- **Migrations:** Any changes to ORM models must be accompanied by an Alembic migration script (`alembic revision --autogenerate -m "description"`).
- **Security:** Use the dependencies in `src/security.py` to protect routes. `only_admin_dep` ensures only administrative users can access specific endpoints.
