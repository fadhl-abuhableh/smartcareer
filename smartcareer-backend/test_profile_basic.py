import requests
import json
import os
import sys

def register_user(base_url, email, password):
    """Register a test user"""
    print(f"Registering user: {email}")
    
    try:
        register_response = requests.post(
            f'{base_url}/register',
            data={
                'email': email,
                'password': password
            }
        )
        
        if register_response.status_code == 409:
            print("User already exists, continuing with tests...")
            return True
        elif register_response.status_code == 201:
            print("User registered successfully.")
            return True
        else:
            print(f"Registration failed: {register_response.status_code}")
            print(register_response.text)
            return False
            
    except Exception as e:
        print(f"Error in registration: {e}")
        return False

def test_update_profile(base_url, email):
    """Test profile update with a registered user"""
    
    # Test: Basic update without image
    print("\nTEST: Update basic profile data")
    try:
        response = requests.post(
            f'{base_url}/api/update-profile',
            data={
                'email': email,
                'name': 'Test User',
                'bio': 'This is a test bio',
                'phone': '123-456-7890'
            }
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            if response.status_code == 200 and json_response.get('success', False):
                print("Test passed - Profile updated successfully")
            else:
                print("Test failed - Could not update profile")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
            
    except Exception as e:
        print(f"Error in test: {e}")
    
    # Verify profile was updated by getting it
    print("\nVerifying profile was updated...")
    try:
        response = requests.get(
            f'{base_url}/api/user-profile',
            params={'email': email}
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            if response.status_code == 200 and json_response.get('success', False):
                print("Profile retrieved successfully")
                
                # Check if the name was updated correctly
                if json_response.get('name') == 'Test User':
                    print("Name was updated correctly")
                else:
                    print(f"Warning: Name doesn't match what we set. Actual: {json_response.get('name')}")
                
                # Check if the bio was updated correctly
                if json_response.get('bio') == 'This is a test bio':
                    print("Bio was updated correctly")
                else:
                    print(f"Warning: Bio doesn't match what we set. Actual: {json_response.get('bio')}")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
    
    except Exception as e:
        print(f"Error when verifying profile: {e}")

def main():
    base_url = 'http://localhost:5000'
    test_email = 'testuser@example.com'
    test_password = 'password123'
    
    # First register/verify the test user exists
    if not register_user(base_url, test_email, test_password):
        print("Could not register test user. Exiting.")
        sys.exit(1)
    
    # Then test the profile update functionality
    test_update_profile(base_url, test_email)

if __name__ == "__main__":
    main() 