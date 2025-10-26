from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
from app.models import get_db, User, KYCDocument
from app.schemas import *
from app.auth import get_password_hash, verify_password, create_access_token, verify_token
from typing import Optional
import os

app = FastAPI(title="SmartBank API", version="1.0.0")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        user_id = verify_token(token)
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

# Auth Endpoints 
@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(User).filter(User.phone_number == user_data.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    user = User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        date_of_birth=user_data.date_of_birth,
        address=user_data.address,
        city=user_data.city,
        state=user_data.state,
        zip_code=user_data.zip_code,
        country=user_data.country
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/v1/auth/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/v1/users/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user



@app.post("/api/v1/users/me/kyc", response_model=KYCResponse, status_code=201)
async def submit_kyc_with_files(
    document_type: str = Form(...),
    document_number: str = Form(...),
    document_issued_date: str = Form(...),
    document_expiry_date: str = Form(...),
    document_front: UploadFile = File(...),
    document_back: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    existing_kyc = db.query(KYCDocument).filter(
        KYCDocument.user_id == current_user.id,
        KYCDocument.status.in_(['pending', 'verified'])
    ).first()
    
    if existing_kyc:
        raise HTTPException(status_code=400, detail="KYC already submitted")
    
    
    allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
    if document_front.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Front document must be JPG, PNG, or PDF")
    

    front_content = await document_front.read()
    if len(front_content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Front document too large (max 2MB)")
    
    back_filename = None
    if document_back:
        if document_back.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Back document must be JPG, PNG, or PDF")
        
        back_content = await document_back.read()
        if len(back_content) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Back document too large (max 2MB)")
        back_filename = document_back.filename
    
   
    kyc_doc = KYCDocument(
        user_id=current_user.id,
        document_type=document_type,
        document_number=document_number,
        document_issued_date=document_issued_date,
        document_expiry_date=document_expiry_date,
        front_filename=document_front.filename,
        back_filename=back_filename
    )
    
    db.add(kyc_doc)
    db.commit()
    db.refresh(kyc_doc)
    
    return kyc_doc

@app.get("/api/v1/users/me/kyc/status", response_model=KYCStatusResponse)
def get_kyc_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    kyc_doc = db.query(KYCDocument).filter(
        KYCDocument.user_id == current_user.id
    ).order_by(KYCDocument.submitted_at.desc()).first()
    
    if not kyc_doc:
        return {
            "kyc_status": "not_submitted",
            "submitted_at": None,
            "verified_at": None,
            "document_type": None,
            "document_number": None
        }
    
    
    doc_num = kyc_doc.document_number
    if len(doc_num) > 4:
        masked_num = doc_num[:2] + '*' * (len(doc_num) - 4) + doc_num[-2:]
    else:
        masked_num = '****'
    
    return {
        "kyc_status": kyc_doc.status,
        "submitted_at": kyc_doc.submitted_at,
        "verified_at": kyc_doc.verified_at,
        "document_type": kyc_doc.document_type,
        "document_number": masked_num
    }

@app.get("/")
def root():
    return {"message": "SmartBank API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)