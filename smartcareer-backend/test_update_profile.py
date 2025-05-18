import requests
import json
import os
import sys

def test_update_profile():
    base_url = 'http://localhost:5000'
    
    # First test update without an image
    print("TEST 1: Update profile without image")
    try:
        response = requests.post(
            f'{base_url}/api/update-profile',
            data={
                'email': 'test@example.com',
                'name': 'Test User',
                'bio': 'This is a test bio',
                'phone': '123-456-7890'
            }
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
            
        print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"Error in test 1: {e}")
    
    # Test update with a simple text file as profile image
    print("TEST 2: Update profile with invalid image (text file)")
    
    # Create a simple text file
    with open('test_image.txt', 'w') as f:
        f.write('This is not an image file')
    
    try:
        with open('test_image.txt', 'rb') as f:
            files = {'profile_image': ('test_image.txt', f, 'text/plain')}
            
            response = requests.post(
                f'{base_url}/api/update-profile',
                data={
                    'email': 'test@example.com',
                    'name': 'Test User Updated',
                    'bio': 'This is an updated test bio',
                    'phone': '123-456-7890'
                },
                files=files
            )
            
            print(f"Status code: {response.status_code}")
            
            try:
                json_response = response.json()
                print(f"Response: {json.dumps(json_response, indent=2)}")
                
            except json.JSONDecodeError:
                print(f"Raw response (not JSON): {response.text}")
                
            print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"Error in test 2: {e}")
    
    # Let's test even simpler with just email parameter, which is the only required field
    print("TEST 3: Update profile with only email (minimum requirement)")
    try:
        response = requests.post(
            f'{base_url}/api/update-profile',
            data={'email': 'test@example.com'}
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
    
    except Exception as e:
        print(f"Error in test 3: {e}")
    
    # Clean up
    if os.path.exists('test_image.txt'):
        os.remove('test_image.txt')

if __name__ == "__main__":
    test_update_profile() 