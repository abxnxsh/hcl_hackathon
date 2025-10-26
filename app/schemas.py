from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date
from app.auth import validate_password_strength

class UserBase(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    date_of_birth: str 
    address: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        birth_date = date.fromisoformat(v)
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise ValueError('Must be at least 18 years old')
        return v

class UserResponse(UserBase):
    id: str
    is_verified: bool
    is_active: bool
    created_at: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class KYCSubmit(BaseModel):
    document_type: str
    document_number: str
    document_issued_date: str
    document_expiry_date: str
    
    @validator('document_type')
    def validate_document_type(cls, v):
        if v not in ['passport', 'driving_license', 'national_id']:
            raise ValueError('Document type must be passport, driving_license, or national_id')
        return v
    
    @validator('document_expiry_date')
    def validate_dates(cls, v, values):
        if 'document_issued_date' in values:
            issue_date = date.fromisoformat(values['document_issued_date'])
            expiry_date = date.fromisoformat(v)
            if expiry_date <= issue_date:
                raise ValueError('Expiry date must be after issue date')
            if expiry_date <= date.today():
                raise ValueError('Document has expired')
        return v

class KYCResponse(BaseModel):
    id: str
    user_id: str
    document_type: str
    document_number: str
    status: str
    submitted_at: str
    
    front_filename: Optional[str] = None
    back_filename: Optional[str] = None

class KYCStatusResponse(BaseModel):
    kyc_status: str
    submitted_at: Optional[str]
    verified_at: Optional[str]
    document_type: str
    document_number: str  