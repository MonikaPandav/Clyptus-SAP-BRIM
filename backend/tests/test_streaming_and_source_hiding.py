import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal, init_db
from backend.app.models.user import User
from backend.app.models.chat import Chat
from backend.app.security.auth import hash_password

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_streaming_sanitizes_status_and_hides_sources_for_regular_user(client):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test_streaming_user@clyptus.ai").first()
        if not user:
            user = User(
                email="test_streaming_user@clyptus.ai",
                name="Standard User",
                password_hash=hash_password("UserPass123!"),
                is_admin=False,
                role="consultant"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.is_admin = False
            db.commit()

        # Create a chat for this user
        chat = Chat(user_id=user.id, title="Stream Test Chat")
        db.add(chat)
        db.commit()
        db.refresh(chat)
        chat_id = chat.id
    finally:
        db.close()

    # Login as regular user
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "test_streaming_user@clyptus.ai", "password": "UserPass123!"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Query with streaming
    stream_resp = client.post(
        f"/api/chats/{chat_id}/messages?stream=true",
        headers=headers,
        json={"content": "What is SAP BRIM?"}
    )
    assert stream_resp.status_code == 200

    raw_lines = stream_resp.text.strip().split("\n\n")
    events = []
    for line in raw_lines:
        line = line.strip()
        if line.startswith("data:"):
            events.append(json.loads(line[5:].strip()))

    event_types = [e.get("type") for e in events]
    assert "token" in event_types, f"Expected tokens in stream, got types: {event_types}"
    assert "done" in event_types, f"Expected done in stream, got types: {event_types}"

    # Verify that status events NEVER contain internal retrieval names for regular user
    status_events = [e for e in events if e.get("type") == "status"]
    for se in status_events:
        msg = se.get("message", "")
        assert "Searching internal" not in msg
        assert "help.sap.com" not in msg
        assert "GitHub" not in msg
        assert "Comparing document" not in msg

    # Verify done event strips all sources and grounding for non-admin user
    done_event = next(e for e in events if e.get("type") == "done")
    assert done_event.get("citations") == []
    assert done_event.get("web_sources") == []
    assert done_event.get("source_type") is None
    assert done_event.get("grounding_score") is None
    assert done_event.get("winning_score") is None
    assert done_event.get("kb_score") is None
    assert done_event.get("web_score") is None
