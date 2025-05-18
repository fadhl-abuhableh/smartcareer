import requests
import json

def test_alias_routes():
    base_url = 'http://localhost:5000'
    test_email = 'testuser@example.com'
    
    print("TESTING ALIAS ROUTES")
    
    # Test 1: Get user profile with alias route
    print("\nTEST 1: Get user profile with alias route (/user-profile)")
    try:
        response = requests.get(
            f'{base_url}/user-profile',
            params={'email': test_email}
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            if response.status_code == 200 and json_response.get('success', False):
                print("Test 1 passed - Profile retrieved successfully")
            else:
                print("Test 1 failed - Could not retrieve profile")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
            
    except Exception as e:
        print(f"Error in test 1: {e}")
    
    # Test 2: Update profile with alias route
    print("\nTEST 2: Update profile with alias route (/update-profile)")
    try:
        response = requests.post(
            f'{base_url}/update-profile',
            data={
                'email': test_email,
                'name': 'Test User - Alias Route',
                'bio': 'This is a test bio updated via alias route',
                'phone': '987-654-3210'
            }
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            if response.status_code == 200 and json_response.get('success', False):
                print("Test 2 passed - Profile updated successfully via alias route")
            else:
                print("Test 2 failed - Could not update profile via alias route")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
            
    except Exception as e:
        print(f"Error in test 2: {e}")
    
    # Test 3: Verify the profile was updated
    print("\nTEST 3: Verify profile was updated (via original /api/user-profile route)")
    try:
        response = requests.get(
            f'{base_url}/api/user-profile',
            params={'email': test_email}
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            if response.status_code == 200 and json_response.get('success', False):
                print("Test 3 passed - Profile retrieved successfully")
                
                # Check if the name was updated correctly
                if json_response.get('name') == 'Test User - Alias Route':
                    print("Name was updated correctly")
                else:
                    print(f"Warning: Name doesn't match what we set. Actual: {json_response.get('name')}")
                
                # Check if the bio was updated correctly
                if json_response.get('bio') == 'This is a test bio updated via alias route':
                    print("Bio was updated correctly")
                else:
                    print(f"Warning: Bio doesn't match what we set. Actual: {json_response.get('bio')}")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
    
    except Exception as e:
        print(f"Error in test 3: {e}")

if __name__ == "__main__":
    test_alias_routes() 