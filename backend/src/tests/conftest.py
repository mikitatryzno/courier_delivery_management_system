import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.core.database import get_db, Base
from src.models.user import User, UserRole
from src.core.security import get_password_hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("testpass"),
        role=UserRole.SENDER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, db_session):
    # Create an admin user and return auth headers
    admin = User(
        email="admin@example.com",
        name="Admin User",
        hashed_password=get_password_hash("adminpass"),
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    response = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass"
    })
    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}