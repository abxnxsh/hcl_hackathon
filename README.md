# HCL Hackathon

## Actors & Responsibilities
## 1.Customer
Responsibilities:

    Register account with personal information

    Submit KYC documents for verification

    Check KYC status

    View own profile
Permissions:

     Register themselves

     Submit their own KYC

     View their own profile/KYC status

     Cannot view other users' data

     Cannot approve/reject KYC

## System
Responsibilities:

    Validate input data
    Hash passwords securely
    Generate JWT tokens
    Maintain audit logs
    Enforce rate limiting

### Auth Flow

```
1. User Registration → Input Validation → Password Hashing → User Created
2. User Login → Credential Verification → JWT Token Generation
3. Protected Endpoints → JWT Verification → Access Control
```
### KYC Verification Flow

```
1. KYC Submission → Document Validation → Status: Pending
2. Admin Review → Manual Verification → Status: Approved/Rejected
3. Status Update → User Notification → Audit Log
```


## Edge Cases & Error Handling

### Registration Issues
- **Duplicate Email** → `EMAIL_EXISTS` (400)
- **Duplicate Phone** → `PHONE_EXISTS` (400)
- **Weak Password** → `VALIDATION_ERROR` (422)
- **Underage User** (<18 years) → `UNDERAGE_USER` (422)
- **Invalid Email Format** → `VALIDATION_ERROR` (422)

### KYC Issues
- **Duplicate KYC Submission** → `KYC_ALREADY_SUBMITTED` (400)
- **Invalid Document Type** → `VALIDATION_ERROR` (422)
- **Expired Document** → `DOCUMENT_EXPIRED` (422)
- **Invalid Date Sequence** → `INVALID_DATE_RANGE` (422)
- **Large File Size** → `FILE_TOO_LARGE` (400)
- **Invalid File Type** → `INVALID_FILE_TYPE` (400)

### System Issues
- **Database Connection Failure** → `INTERNAL_SERVER_ERROR` (500)
- **JWT Token Expired** → `TOKEN_EXPIRED` (401)
- **Invalid Authorization** → `UNAUTHORIZED` (401)
- **Missing Token** → `MISSING_AUTH_HEADER` (401)

## API Endpoints

### 1. Register User
**Endpoint:** `POST /api/v1/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "phone_number": "+1234567890",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "country": "US"
}
```
**Success Response**
```
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

Error
```
{
  "status": "error",
  "message": "Registration failed",
  "error": {
    "code": "EMAIL_EXISTS",
    "detail": "Email already registered"
  }
}
```
Error(422)
```
{
  "status": "error",
  "message": "Validation failed",
  "error": {
    "code": "VALIDATION_ERROR",
    "detail": "Password must contain at least one uppercase letter, one lowercase letter, one digit and one special character",
    "fields": {
      "password": "Password must contain at least one uppercase letter","Password must contain at least one special character"
    }
  }
}
```

## KYC

**POST** `/users/me/kyc`

Header- Authorization: Bearer <jwt_token>
```

{
  "document_type": "passport",
  "document_number": "A12345678",
  "document_issued_date": "2020-01-15",
  "document_expiry_date": "2030-01-15"
}
```

**Response**
```
{
  "status": "success",
  "message": "KYC documents submitted for verification",
  "data": {
    "kyc_status": "pending",
    "submitted_at": "2024-01-15T12:00:00Z",
    "document_type": "passport",
    "document_number": "A12345678"
  }
}

```
