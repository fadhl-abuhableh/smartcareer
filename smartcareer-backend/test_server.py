import requests
import sys

try:
    # Test basic connectivity
    response = requests.get('http://localhost:5000/')
    print(f"Server connection: Status {response.status_code}")
    print(f"Response: {response.text}")
    
    # Try the test endpoint
    test_response = requests.post(
        'http://localhost:5000/api/test-form-upload', 
        data={'email': 'test@example.com', 'name': 'Test User'}
    )
    print(f"\nTest form endpoint: Status {test_response.status_code}")
    print(f"Response: {test_response.text}")
    
except requests.exceptions.ConnectionError:
    print("CONNECTION ERROR: Cannot connect to the server. Make sure Flask is running.")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1) 