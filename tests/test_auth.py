import pytest
from app.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    verify_token,
    validate_password_strength
)
from app.models import User
from fastapi import HTTPException

class TestAuth:
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_password_strength_valid(self):
        """Test valid password strength"""
        valid_passwords = [
            "SecurePass123!",
            "Another$Pass99",
            "Test@123456"
        ]
        
        for password in valid_passwords:
            errors = validate_password_strength(password)
            assert len(errors) == 0, f"Password {password} failed: {errors}"
    
    def test_password_strength_invalid(self):
        """Test invalid password strength"""
        test_cases = [
     
            ("short", ["Password must be at least 8 characters"]),
            ("nouppercase123!", ["Password must contain at least one uppercase letter"]),
            ("NOLOWERCASE123!", ["Password must contain at least one lowercase letter"]),
            ("NoDigits!", ["Password must contain at least one digit"]),
            ("NoSpecial123", ["Password must contain at least one special character (!@#$%^&*)"]),
        ]
        
        for password, expected_minimum_errors in test_cases:
            errors = validate_password_strength(password)
            
          
            for expected_error in expected_minimum_errors:
                assert expected_error in errors, f"Expected error '{expected_error}' not found in {errors} for password '{password}'"
    
    def test_password_strength_multiple_errors(self):
        """Test passwords that violate multiple rules"""
        test_cases = [
            ("short", [
                "Password must be at least 8 characters",
                "Password must contain at least one uppercase letter",
                "Password must contain at least one digit",
                "Password must contain at least one special character (!@#$%^&*)"
            ]),
            ("abc", [
                "Password must be at least 8 characters", 
                "Password must contain at least one uppercase letter",
                "Password must contain at least one digit",
                "Password must contain at least one special character (!@#$%^&*)"
            ]),
            ("lowercaseonly", [
                "Password must contain at least one uppercase letter",
                "Password must contain at least one digit", 
                "Password must contain at least one special character (!@#$%^&*)"
            ]),
        ]
        
        for password, expected_errors in test_cases:
            errors = validate_password_strength(password)
            assert set(expected_errors) == set(errors), f"Password '{password}': expected {expected_errors}, got {errors}"
    
    def test_create_and_verify_token(self):
        """Test JWT token creation and verification"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        user_id = verify_token(token)
        assert user_id == "user123"
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.here")
        assert exc_info.value.status_code == 401
    
    def test_verify_token_missing_sub(self):
        """Test verification of token without subject"""
        from jose import jwt
        from app.auth import SECRET_KEY, ALGORITHM
      
        token = jwt.encode({"exp": 1234567890}, SECRET_KEY, algorithm=ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401