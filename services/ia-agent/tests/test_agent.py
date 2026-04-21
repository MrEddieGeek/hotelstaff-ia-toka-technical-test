from __future__ import annotations


def _index(client, doc_id: str, text: str, metadata: dict | None = None) -> None:
    response = client.post(
        "/agent/index",
        json={"doc_id": doc_id, "text": text, "metadata": metadata or {}},
    )
    assert response.status_code in (200, 202), response.text


def test_ask_without_documents_returns_fallback(client) -> None:
    response = client.post("/agent/ask", json={"question": "¿Quién es recepcionista?"})
    assert response.status_code == 200
    data = response.json()
    assert "No encontré" in data["answer"] or data["answer"]
    assert data["sources"] == []


def test_index_and_ask_returns_sources(client) -> None:
    _index(
        client,
        "user-1",
        "Ana García es recepcionista del turno matutino en el hotel.",
        {"user_id": "user-1", "position": "recepcionista"},
    )
    _index(
        client,
        "user-2",
        "Luis Pérez trabaja como chef ejecutivo del restaurante.",
        {"user_id": "user-2", "position": "chef"},
    )

    response = client.post(
        "/agent/ask",
        json={"question": "¿Quién es recepcionista?", "top_k": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sources"], "esperaba al menos una fuente recuperada"
    top_ids = [s["doc_id"] for s in data["sources"]]
    assert "user-1" in top_ids


def test_bulk_index(client) -> None:
    response = client.post(
        "/agent/index/bulk",
        json=[
            {"doc_id": "u-10", "text": "María es housekeeping senior.", "metadata": {}},
            {"doc_id": "u-11", "text": "Carlos es supervisor de mantenimiento.", "metadata": {}},
        ],
    )
    assert response.status_code in (200, 202)
    assert response.json()["count"] == 2
