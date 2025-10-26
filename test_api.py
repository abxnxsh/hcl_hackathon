import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

def test_api():
    print("Testing SmartBank API...\n")
    
    # Test data
    test_user = {
        "email": "john.doe@example2.com",
        "phone_number": "+1234567892",
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
    
    kyc_data = {
        "document_type": "passport",
        "document_number": "A12345678",
        "document_issued_date": "2020-01-15",
        "document_expiry_date": "2030-01-15"
    }
    
    # 1. Test Registration
    print("1. Testing User Registration...")
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    if response.status_code == 201:
        print("Registration successful!")
        user_data = response.json()
        print(f"   User ID: {user_data['id']}")
    else:
        print(f" Registration failed: {response.text}") 
        return
    
    # 2. Test Login
    print("\n2. Testing User Login...")
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        print("Login successful!")
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"   Token: {access_token[:20]}...")
    else:
        print(f"Login failed: {response.text}")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 3. Test Get Profile
    print("\n3. Testing Get Profile...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        print("Profile retrieved successfully!")
        profile = response.json()
        print(f"   Name: {profile['first_name']} {profile['last_name']}")
    else:
        print(f"Profile retrieval failed: {response.text}")
    
    # 4. Test KYC Submission
    print("\n4. Testing KYC Submission...")
    response = requests.post(f"{BASE_URL}/users/me/kyc", headers=headers, json=kyc_data)
    if response.status_code == 201:
        print("KYC submitted successfully!")
        kyc_response = response.json()
        print(f"   KYC Status: {kyc_response['status']}")
    else:
        print(f"KYC submission failed: {response.text}")
    
    # 5. Test KYC Status
    print("\n5. Testing KYC Status...")
    response = requests.get(f"{BASE_URL}/users/me/kyc/status", headers=headers)
    if response.status_code == 200:
        print("KYC status retrieved!")
        status_data = response.json()
        print(f"   Status: {status_data['kyc_status']}")
        print(f"   Document: {status_data['document_number']}")
    else:
        print(f"KYC status failed: {response.text}")
    
    print("\n All tests completed!")

if __name__ == "__main__":
    test_api()