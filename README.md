# TaskHub API — Backend Service

A high-performance asynchronous REST API built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, and **Neon PostgreSQL**.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: Neon Serverless PostgreSQL
- **Async Driver**: `asyncpg`
- **ORM**: SQLAlchemy 2.0 (Async Session)
- **Validation**: Pydantic v2 + Pydantic Settings
- **HTTP Client**: `httpx` (for external API integration)
- **Server**: Uvicorn

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Neon PostgreSQL connection string

### 2. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env` and fill in your Neon DB connection string:
```bash
cp .env.example .env
```

### 5. Run the Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📖 API Documentation

Once the server is running, visit:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── core/           # Config, database engine, exception handlers
│   ├── models/         # SQLAlchemy models (User, Task, Comment)
│   ├── schemas/        # Pydantic schemas for request/response validation
│   ├── repositories/   # Data access layer (CRUD, filtering, sorting, pagination)
│   ├── services/       # Business logic layer
│   ├── routes/         # API endpoints (users, tasks, dashboard, external)
│   ├── utils/          # Database seeder
│   └── main.py         # Application entry point
├── requirements.txt
├── .env.example
└── .gitignore
```
