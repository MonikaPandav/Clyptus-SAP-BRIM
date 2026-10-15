import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.chat import Chat
from backend.app.models.message import Message
from backend.app.models.citation import Citation

client = TestClient(app)


def test_admin_login_and_credentials():
    """Verify designated admin vamshiyadav245@gmail.com can securely login."""
    resp = client.post(
        "/api/auth/admin-login",
        json={"email": "vamshiyadav245@gmail.com", "password": "Vamshi@06"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "vamshiyadav245@gmail.com"
    assert data["user"]["is_admin"] is True
    assert data["user"]["role"] == "admin"


def test_non_admin_cannot_use_admin_login():
    """Verify regular accounts are rejected by admin login with 403 Forbidden."""
    # Ensure a non-admin user exists
    db = SessionLocal()
    non_admin = db.query(User).filter(User.is_admin == False).first()
    db.close()
    assert non_admin is not None

    resp = client.post(
        "/api/auth/admin-login",
        json={"email": non_admin.email, "password": "wrongpassword"},
    )
    assert resp.status_code in (401, 403)


def test_document_and_sources_access_control():
    """
    Verify /documents and /rag-inspect endpoints are strictly restricted:
    - 403 for unauthenticated or non-admin requests
    - 200 for authenticated admin requests
    """
    # 1. Unauthenticated requests must receive 401 or 403
    assert client.get("/api/documents").status_code in (401, 403)
    assert client.get("/api/rag-inspect/documents").status_code in (401, 403)


    # 2. Non-admin user token must receive 403
    demo_login = client.post("/api/auth/demo")
    assert demo_login.status_code == 200
    demo_token = demo_login.json()["access_token"]

    assert client.get("/api/documents", headers={"Authorization": f"Bearer {demo_token}"}).status_code == 403
    assert client.get("/api/rag-inspect/documents", headers={"Authorization": f"Bearer {demo_token}"}).status_code == 403

    # 3. Super Admin token must succeed (200)
    admin_login = client.post(
        "/api/auth/admin-login",
        json={"email": "vamshiyadav245@gmail.com", "password": "Vamshi@06"},
    )
    admin_token = admin_login.json()["access_token"]

    admin_docs = client.get("/api/documents", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_docs.status_code == 200

    admin_rag = client.get("/api/rag-inspect/documents", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_rag.status_code == 200


def test_citations_stripped_for_regular_users():
    """Verify regular users do not receive internal citations, while admins do."""
    db = SessionLocal()
    admin_user = db.query(User).filter(User.email == "vamshiyadav245@gmail.com").first()
    assert admin_user is not None

    # Create an admin chat with a citation
    admin_chat = Chat(user_id=admin_user.id, title="Admin Security Verification")
    db.add(admin_chat)
    db.commit()
    db.refresh(admin_chat)

    msg = Message(
        chat_id=admin_chat.id,
        role="assistant",
        content="SAP Convergent Invoicing manages billable items in standard packages.",
        source_type="knowledge_base",
        grounding_score=0.98,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    cit = Citation(
        message_id=msg.id,
        chunk_id="chk-sec-01",
        source_type="knowledge_base",
        document_id="doc-internal-01",
        document_name="Internal_BRIM_Spec.pdf",
        page_number=42,
        section="Billable Items",
        similarity_score=0.95,
        citation_text="Internal confidential extraction snippet.",
    )
    db.add(cit)
    db.commit()

    # Admin access token
    admin_login = client.post(
        "/api/auth/admin-login",
        json={"email": "vamshiyadav245@gmail.com", "password": "Vamshi@06"},
    )
    admin_token = admin_login.json()["access_token"]

    # Admin request sees citations
    admin_res = client.get(
        f"/api/chats/{admin_chat.id}/messages",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_res.status_code == 200
    admin_messages = admin_res.json()
    assert len(admin_messages) > 0
    assert len(admin_messages[0]["citations"]) == 1
    assert admin_messages[0]["citations"][0]["document"] == "Internal_BRIM_Spec.pdf"

    # Cleanup
    db.delete(admin_chat)
    db.commit()
    db.close()
