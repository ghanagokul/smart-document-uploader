from dotenv import load_dotenv
load_dotenv()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies import get_current_user
from app.main import app
from app.models.document import Document
from app.models.user import User
from app.utils.auth import hash_password

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_tables():
    with engine.begin() as conn:
        conn.execute(Document.__table__.delete())
        conn.execute(User.__table__.delete())
    yield


def create_test_user(db, email="ghanagokul@example.com", password="password123", full_name="Test User"):
    user = User(email=email, full_name=full_name, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

test_user_holder = {"user": None}


def override_current_user():
    return test_user_holder["user"]


@pytest.fixture
def auth_user():
    with TestingSessionLocal() as db:
        user = create_test_user(db)
    test_user_holder["user"] = user
    app.dependency_overrides[get_current_user] = override_current_user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def no_auth():
    app.dependency_overrides.pop(get_current_user, None)
    yield