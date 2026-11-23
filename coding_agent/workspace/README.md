# FastAPI Todo App

A simple, lightweight Todo Web Application built with **FastAPI** and **SQLite**, with a responsive single-page user interface built using plain JavaScript.

## Features

- **Full CRUD operations**: Create, list, retrieve, update, and delete todos.
- **Toggle Completion**: Patch endpoint to toggle completed status with visual strikethrough indication in the UI.
- **SQLite Persistence**: Stores todos in SQLite, configurable via the `DB_PATH` environment variable (defaults to `todos.db`).
- **Path-independent execution**: Relative path resolution using `Path(__file__).parent`.
- **Vanilla JS UI**: Served at `/` with no external frontend dependencies.
- **Automated Tests**: Unit and integration test suite using `pytest` and FastAPI's `TestClient` with per-test database isolation.

---

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Serves the single-page frontend application (`static/index.html`). |
| `GET` | `/todos` | List all todos. |
| `POST` | `/todos` | Create a new todo (`title`, optional `description`, default `completed: false`). |
| `GET` | `/todos/{id}` | Retrieve a specific todo by ID (404 if missing). |
| `PUT` | `/todos/{id}` | Update todo title, description, or completed status (404 if missing). |
| `DELETE` | `/todos/{id}` | Delete a specific todo by ID (404 if missing). |
| `PATCH` | `/todos/{id}/toggle` | Toggle the completion state of a todo (404 if missing). |

---

## Setup

1. **Clone the repository** and navigate to the project directory:
   ```bash
   cd workspace
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the App

Start the application with Uvicorn:

```bash
uvicorn app:app --port 8001 --reload
```

Open your browser and navigate to:
[http://127.0.0.1:8001](http://127.0.0.1:8001)

---

## Running the Tests

Execute the test suite with `pytest`:

```bash
pytest
```

Each test runs in complete database isolation using pytest's `tmp_path` and `monkeypatch`.
