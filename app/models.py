from sqlalchemy import create_engine, Column, String, Boolean, Date, Text, TIMESTAMP, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import VARCHAR
import uuid
from datetime import datetime


SQLALCHEMY_DATABASE_URL = "sqlite:///./smartbank.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(String(10), nullable=False)  
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="US")
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    document_type = Column(String(20), nullable=False)  
    document_number = Column(String(100), nullable=False)
    document_issued_date = Column(String(10), nullable=False)  
    document_expiry_date = Column(String(10), nullable=False)  
    status = Column(String(20), default='pending') 
    rejection_reason = Column(Text, nullable=True)
    submitted_at = Column(String(30), default=lambda: datetime.utcnow().isoformat())
    verified_at = Column(String(30), nullable=True)
    
    front_filename = Column(String(255), nullable=True)
    back_filename = Column(String(255), nullable=True)


Base.metadata.create_all(bind=engine)