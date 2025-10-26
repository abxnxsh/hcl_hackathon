import pytest
from fastapi import status
from app.models import User, KYCDocument
from app.auth import get_password_hash, create_access_token

class TestAuthEndpoints:
    def test_register_success(self, client, db_session, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert "password" not in data
        assert "password_hash" not in data
        
 
        user = db_session.query(User).filter(User.email == sample_user_data["email"]).first()
        assert user is not None
        assert user.is_verified is False
    
    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email"""
       
        response1 = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
  
        response2 = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response2.json()["detail"]
    
    def test_register_weak_password(self, client, sample_user_data):
        """Test registration with weak password"""
        weak_user_data = sample_user_data.copy()
        weak_user_data["password"] = "weak"
        
        response = client.post("/api/v1/auth/register", json=weak_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_underage(self, client, sample_user_data):
        """Test registration for underage user"""
        underage_data = sample_user_data.copy()
        underage_data["date_of_birth"] = "2010-01-01"
        
        response = client.post("/api/v1/auth/register", json=underage_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, db_session, sample_user_data):
        """Test successful login"""
       
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials"""
        login_data = {
            "email": sample_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authentication"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_profile_authorized(self, client, db_session, sample_user_data):
        """Test getting profile with authentication"""
       
        user = User(
            email=sample_user_data["email"],
            phone_number=sample_user_data["phone_number"],
            password_hash=get_password_hash(sample_user_data["password"]),
            first_name=sample_user_data["first_name"],
            last_name=sample_user_data["last_name"],
            date_of_birth=sample_user_data["date_of_birth"],
            address=sample_user_data["address"],
            city=sample_user_data["city"],
            state=sample_user_data["state"],
            zip_code=sample_user_data["zip_code"],
            country=sample_user_data["country"]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        
        token = create_access_token({"sub": user.id})
    
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]

class TestKYCEndpoints:
    def test_submit_kyc_success(self, client, db_session, sample_user_data, sample_kyc_data):
        """Test successful KYC submission"""

        user = User(
            email=sample_user_data["email"],
            phone_number=sample_user_data["phone_number"],
            password_hash=get_password_hash(sample_user_data["password"]),
            first_name=sample_user_data["first_name"],
            last_name=sample_user_data["last_name"],
            date_of_birth=sample_user_data["date_of_birth"],
            address=sample_user_data["address"],
            city=sample_user_data["city"],
            state=sample_user_data["state"],
            zip_code=sample_user_data["zip_code"],
            country=sample_user_data["country"]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        token = create_access_token({"sub": user.id})
        
    
        files = {
            "document_front": ("front.jpg", b"fake image content", "image/jpeg"),
            "document_back": ("back.jpg", b"fake back image content", "image/jpeg")
        }
        
        data = sample_kyc_data.copy()
        
        response = client.post(
            "/api/v1/users/me/kyc",
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files=files
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["document_type"] == sample_kyc_data["document_type"]
        assert response_data["status"] == "pending"
        

        kyc_doc = db_session.query(KYCDocument).filter(
            KYCDocument.user_id == user.id
        ).first()
        assert kyc_doc is not None
        assert kyc_doc.document_number == sample_kyc_data["document_number"]
    
    def test_get_kyc_status_not_submitted(self, client, db_session, sample_user_data):
        """Test getting KYC status when not submitted"""
        user = User(
            email=sample_user_data["email"],
            phone_number=sample_user_data["phone_number"],
            password_hash=get_password_hash(sample_user_data["password"]),
            first_name=sample_user_data["first_name"],
            last_name=sample_user_data["last_name"],
            date_of_birth=sample_user_data["date_of_birth"],
            address=sample_user_data["address"],
            city=sample_user_data["city"],
            state=sample_user_data["state"],
            zip_code=sample_user_data["zip_code"],
            country=sample_user_data["country"]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        token = create_access_token({"sub": user.id})
        
        response = client.get(
            "/api/v1/users/me/kyc/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["kyc_status"] == "not_submitted"
        assert data["submitted_at"] is None
    
    def test_get_kyc_status_submitted(self, client, db_session, sample_user_data, sample_kyc_data):
        """Test getting KYC status when submitted"""
        user = User(
            email=sample_user_data["email"],
            phone_number=sample_user_data["phone_number"],
            password_hash=get_password_hash(sample_user_data["password"]),
            first_name=sample_user_data["first_name"],
            last_name=sample_user_data["last_name"],
            date_of_birth=sample_user_data["date_of_birth"],
            address=sample_user_data["address"],
            city=sample_user_data["city"],
            state=sample_user_data["state"],
            zip_code=sample_user_data["zip_code"],
            country=sample_user_data["country"]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
       
        kyc_doc = KYCDocument(
            user_id=user.id,
            **sample_kyc_data,
            front_filename="front.jpg"
        )
        db_session.add(kyc_doc)
        db_session.commit()
        db_session.refresh(kyc_doc)
        
        token = create_access_token({"sub": user.id})
        
        response = client.get(
            "/api/v1/users/me/kyc/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["kyc_status"] == "pending"
        assert data["document_type"] == sample_kyc_data["document_type"]
        # Check that document number is masked
        assert "****" in data["document_number"] or data["document_number"].count('*') > 0

class TestHealthEndpoints:
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"