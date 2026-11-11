def test_create_task_returns_201_and_defaults_to_todo(client):
    response = client.post("/tasks", json={"title": "Escriure la lab"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["status"] == "todo"


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_list_tasks_returns_created_tasks(client):
    client.post("/tasks", json={"title": "A"})
    client.post("/tasks", json={"title": "B"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert [t["title"] for t in response.json()] == ["A", "B"]


def test_get_task_404_when_missing(client):
    assert client.get("/tasks/99").status_code == 404


def test_delete_task(client):
    client.post("/tasks", json={"title": "A"})

    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404
