import pytest
from app.models import User, KYCDocument
from datetime import datetime

class TestModels:
    def test_user_creation(self, db_session):
        """Test User model creation"""
        user = User(
            email="test@example.com",
            phone_number="+1234567890",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            address="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            country="US"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_verified is False
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_kyc_document_creation(self, db_session):
        """Test KYCDocument model creation"""

        user = User(
            email="test@example.com",
            phone_number="+1234567890",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            address="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            country="US"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        

        kyc_doc = KYCDocument(
            user_id=user.id,
            document_type="passport",
            document_number="AB1234567",
            document_issued_date="2020-01-01",
            document_expiry_date="2030-01-01",
            front_filename="front.jpg",
            back_filename="back.jpg"
        )
        
        db_session.add(kyc_doc)
        db_session.commit()
        db_session.refresh(kyc_doc)
        
        assert kyc_doc.id is not None
        assert kyc_doc.user_id == user.id
        assert kyc_doc.status == "pending"
        assert kyc_doc.submitted_at is not None