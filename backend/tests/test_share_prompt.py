import pytest
from fastapi.testclient import TestClient

from backend.app.database import SessionLocal, init_db
from backend.app.main import app
from backend.app.models.message import Message

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def _schema():
    # A module-level TestClient skips the app lifespan, so create the shared_prompts table here.
    init_db()


def _login(email: str) -> dict:
    client.post("/api/auth/register", json={"email": email, "name": "Prompt Sharer", "password": "Password123!"})
    token = client.post("/api/auth/login", json={"email": email, "password": "Password123!"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_message(chat_id: str, role: str, content: str) -> str:
    db = SessionLocal()
    try:
        msg = Message(chat_id=chat_id, role=role, content=content)
        db.add(msg)
        db.commit()
        return msg.id
    finally:
        db.close()


def test_shared_prompt_is_public_and_hides_attachment_names():
    headers = _login("prompt_sharer@sap.com")
    chat_id = client.post("/api/chats", json={"title": "Share test"}, headers=headers).json()["id"]
    msg_id = _add_message(chat_id, "user", "[Attached: payroll_2026.pdf (3 pages)]\n\nHow do I reverse a billing document?")

    first = client.post(f"/api/chats/{chat_id}/messages/{msg_id}/share", headers=headers)
    assert first.status_code == 200, first.text
    token = first.json()["token"]
    assert len(token) >= 16

    # Sharing the same prompt again keeps the same link.
    assert client.post(f"/api/chats/{chat_id}/messages/{msg_id}/share", headers=headers).json()["token"] == token

    public = client.get(f"/api/shared/prompts/{token}")  # no auth header
    assert public.status_code == 200
    assert public.json()["content"] == "How do I reverse a billing document?"
    assert "payroll_2026" not in public.text


def test_share_prompt_rejects_other_users_assistant_messages_and_unknown_tokens():
    owner = _login("share_owner@sap.com")
    intruder = _login("share_intruder@sap.com")
    chat_id = client.post("/api/chats", json={"title": "Owned"}, headers=owner).json()["id"]
    user_id = _add_message(chat_id, "user", "Private question")
    answer_id = _add_message(chat_id, "assistant", "Private answer")

    assert client.post(f"/api/chats/{chat_id}/messages/{user_id}/share", headers=intruder).status_code == 404
    assert client.post(f"/api/chats/{chat_id}/messages/{answer_id}/share", headers=owner).status_code == 404
    assert client.get("/api/shared/prompts/not-a-real-token").status_code == 404
