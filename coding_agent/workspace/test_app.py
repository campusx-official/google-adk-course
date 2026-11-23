import os
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_todos.db"
    monkeypatch.setenv("DB_PATH", str(db_file))

def test_create_todo():
    response = client.post("/todos", json={"title": "Test Todo", "description": "A test description"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Todo"
    assert data["description"] == "A test description"
    assert data["completed"] is False

def test_create_todo_default_completed():
    response = client.post("/todos", json={"title": "Buy groceries"})
    assert response.status_code == 201
    data = response.json()
    assert data["completed"] is False
    assert data["description"] is None

def test_list_todos():
    client.post("/todos", json={"title": "Todo 1"})
    client.post("/todos", json={"title": "Todo 2"})
    
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Todo 1"
    assert data[1]["title"] == "Todo 2"

def test_get_todo_success():
    create_res = client.post("/todos", json={"title": "Sample Todo", "description": "Details"})
    todo_id = create_res.json()["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Sample Todo"

def test_get_todo_not_found():
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_update_todo_success():
    create_res = client.post("/todos", json={"title": "Old Title", "completed": False})
    todo_id = create_res.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={"title": "New Title", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["completed"] is True

def test_update_todo_not_found():
    response = client.put("/todos/999", json={"title": "New Title"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_delete_todo_success():
    create_res = client.post("/todos", json={"title": "To be deleted"})
    todo_id = create_res.json()["id"]

    delete_res = client.delete(f"/todos/{todo_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/todos/{todo_id}")
    assert get_res.status_code == 404

def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_db_isolation_between_tests():
    # Verify that each test receives an isolated fresh database
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_toggle_todo_false_to_true():
    create_res = client.post("/todos", json={"title": "Toggle Task", "completed": False})
    todo_id = create_res.json()["id"]

    toggle_res = client.patch(f"/todos/{todo_id}/toggle")
    assert toggle_res.status_code == 200
    data = toggle_res.json()
    assert data["id"] == todo_id
    assert data["completed"] is True

def test_toggle_todo_true_to_false():
    create_res = client.post("/todos", json={"title": "Completed Task", "completed": True})
    todo_id = create_res.json()["id"]

    toggle_res = client.patch(f"/todos/{todo_id}/toggle")
    assert toggle_res.status_code == 200
    data = toggle_res.json()
    assert data["id"] == todo_id
    assert data["completed"] is False

def test_toggle_todo_not_found():
    response = client.patch("/todos/999/toggle")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_root_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text
    assert "<title>Todo App</title>" in response.text
