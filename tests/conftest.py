import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base, get_db
from app.auth import get_password_hash, create_access_token


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_smartbank.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():

    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "US"
    }

@pytest.fixture
def sample_kyc_data():
    return {
        "document_type": "passport",
        "document_number": "AB1234567",
        "document_issued_date": "2020-01-01",
        "document_expiry_date": "2030-01-01"
    }