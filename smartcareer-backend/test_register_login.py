import requests
import json
import sys

def test_register_login():
    base_url = 'http://localhost:5000'
    test_email = 'testuser@example.com'
    test_password = 'password123'
    
    # Step 1: Register a new user
    print("STEP 1: Register new user")
    try:
        register_response = requests.post(
            f'{base_url}/register',
            data={
                'email': test_email,
                'password': test_password
            }
        )
        
        print(f"Status code: {register_response.status_code}")
        
        try:
            json_response = register_response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            # If we get a 409, it means the user already exists, which is fine
            if register_response.status_code == 409:
                print("User already exists, continuing with login...")
            elif register_response.status_code not in [200, 201]:
                print("Registration failed with an unexpected error.")
                sys.exit(1)
                
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {register_response.text}")
            sys.exit(1)
            
        print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"Error in registration: {e}")
        sys.exit(1)
    
    # Step 2: Login with the registered user
    print("STEP 2: Login with registered user")
    try:
        login_response = requests.post(
            f'{base_url}/login',
            data={
                'email': test_email,
                'password': test_password
            }
        )
        
        print(f"Status code: {login_response.status_code}")
        
        try:
            json_response = login_response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            if login_response.status_code != 200:
                print("Login failed.")
                sys.exit(1)
                
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {login_response.text}")
            sys.exit(1)
            
        print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"Error in login: {e}")
        sys.exit(1)
    
    # Step 3: Get the user profile
    print("STEP 3: Get user profile")
    try:
        profile_response = requests.get(
            f'{base_url}/api/user-profile',
            params={'email': test_email}
        )
        
        print(f"Status code: {profile_response.status_code}")
        
        try:
            json_response = profile_response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
                
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {profile_response.text}")
            
        print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"Error getting profile: {e}")
    
    return test_email, test_password

if __name__ == "__main__":
    test_register_login() 