import os
import sqlite3
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
DEFAULT_DB_PATH = BASE_DIR / "todos.db"

app = FastAPI()

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

def get_db():
    db_path = os.getenv("DB_PATH", str(DEFAULT_DB_PATH))
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    return conn

@app.get("/", response_class=FileResponse)
def read_index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

@app.post("/todos/", response_model=Todo, status_code=201)
@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, 1 if todo.completed else 0)
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed
    }

@app.get("/todos/", response_model=List[Todo])
@app.get("/todos", response_model=List[Todo])
def list_todos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todos")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "completed": bool(row["completed"])
        }
        for row in rows
    ]

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"])
    }

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    new_title = todo_update.title if todo_update.title is not None else row["title"]
    new_description = todo_update.description if todo_update.description is not None else row["description"]
    new_completed = todo_update.completed if todo_update.completed is not None else bool(row["completed"])

    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (new_title, new_description, 1 if new_completed else 0, todo_id)
    )
    conn.commit()
    conn.close()

    return {
        "id": todo_id,
        "title": new_title,
        "description": new_description,
        "completed": new_completed
    }

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()

    return {
        "message": "Todo deleted",
        "todo": {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "completed": bool(row["completed"])
        }
    }

@app.patch("/todos/{todo_id}/toggle", response_model=Todo)
def toggle_todo(todo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    new_completed = not bool(row["completed"])
    cursor.execute("UPDATE todos SET completed = ? WHERE id = ?", (1 if new_completed else 0, todo_id))
    conn.commit()
    conn.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": new_completed
    }
