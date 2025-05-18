import requests
import json
import os
import sys
from io import BytesIO

def test_profile_image_upload():
    base_url = 'http://localhost:5000'
    test_email = 'testuser@example.com'
    
    print("TEST: Separate Profile Image Upload")
    
    # First create a test image file (simple text file to test rejection)
    print("\nTEST 1: Invalid image upload (text file)")
    with open('test_image.txt', 'w') as f:
        f.write('This is not an image file')
    
    try:
        with open('test_image.txt', 'rb') as f:
            files = {'profile_image': ('test_image.txt', f, 'text/plain')}
            
            response = requests.post(
                f'{base_url}/api/upload-profile-image',
                data={'email': test_email},
                files=files
            )
            
            print(f"Status code: {response.status_code}")
            
            try:
                json_response = response.json()
                print(f"Response: {json.dumps(json_response, indent=2)}")
                
                if response.status_code == 400 and not json_response.get('success', False):
                    print("Test 1 passed - Invalid image correctly rejected")
                
            except json.JSONDecodeError:
                print(f"Raw response (not JSON): {response.text}")
    
    except Exception as e:
        print(f"Error in test 1: {e}")
    
    # Create a simple dummy PNG image
    print("\nTEST 2: Valid image upload (using a dummy PNG)")
    try:
        # Create a very small valid PNG image
        # This is a 1x1 pixel transparent PNG
        dummy_png = BytesIO(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
            b'\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\n'
            b'IDAT\x08\x99c\x00\x00\x00\x02\x00\x01\xf4\x93\x00G\x00\x00'
            b'\x00\x00IEND\xaeB`\x82'
        )
        dummy_png.name = 'test_image.png'
        
        files = {'profile_image': ('test_image.png', dummy_png, 'image/png')}
        
        response = requests.post(
            f'{base_url}/api/upload-profile-image',
            data={'email': test_email},
            files=files
        )
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            
            if response.status_code == 200 and json_response.get('success', True):
                print("Test 2 passed - Valid image successfully uploaded")
                print(f"Profile image URL: {json_response.get('profile_image_url')}")
            
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {response.text}")
        
    except Exception as e:
        print(f"Error in test 2: {e}")
    
    # Clean up
    if os.path.exists('test_image.txt'):
        os.remove('test_image.txt')

if __name__ == '__main__':
    test_profile_image_upload() 