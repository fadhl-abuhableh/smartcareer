import requests
import json

# Test configuration - update as needed
BASE_URL = "http://localhost:5000"
USER_EMAIL = "fadil.12577@gmail.com"  # This user exists in the database

def test_add_internship():
    print("\n===== TESTING ADD INTERNSHIP =====")
    
    # Test data
    data = {
        'email': USER_EMAIL,
        'company': 'Test Company',
        'role': 'Developer',
        'dates': '2023-01-01 to 2023-06-30',
        'description': 'This is a test internship added from the Python test script.'
    }
    
    # Send request
    print(f"Sending request to add internship for {USER_EMAIL}...")
    response = requests.post(f"{BASE_URL}/add_internship", data=data)
    
    # Print results
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_add_milestone():
    print("\n===== TESTING ADD MILESTONE =====")
    
    # Test data
    data = {
        'email': USER_EMAIL,
        'title': 'Completed Python Project',
        'date': '2023-05-15',
        'description': 'Built a full-stack application using Python, Flask, and SQL'
    }
    
    # Send request
    print(f"Sending request to add milestone for {USER_EMAIL}...")
    response = requests.post(f"{BASE_URL}/add_milestone", data=data)
    
    # Print results
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_get_internships():
    print("\n===== TESTING GET INTERNSHIPS =====")
    
    # Send request
    print(f"Fetching internships for {USER_EMAIL}...")
    response = requests.get(f"{BASE_URL}/get_internships", params={'email': USER_EMAIL})
    
    # Print results
    print(f"Status code: {response.status_code}")
    print(f"Found {len(response.json())} internships")
    
    # Print each internship
    for idx, internship in enumerate(response.json(), 1):
        print(f"\nInternship #{idx}:")
        print(f"ID: {internship.get('id')}")
        print(f"Company: {internship.get('company')}")
        print(f"Role: {internship.get('role')}")
        print(f"Dates: {internship.get('dates')}")
    
    return response.json()

def test_get_milestones():
    print("\n===== TESTING GET MILESTONES =====")
    
    # Send request
    print(f"Fetching milestones for {USER_EMAIL}...")
    response = requests.get(f"{BASE_URL}/get_milestones", params={'email': USER_EMAIL})
    
    # Print results
    print(f"Status code: {response.status_code}")
    print(f"Found {len(response.json())} milestones")
    
    # Print each milestone
    for idx, milestone in enumerate(response.json(), 1):
        print(f"\nMilestone #{idx}:")
        print(f"ID: {milestone.get('id')}")
        print(f"Title: {milestone.get('title')}")
        print(f"Date: {milestone.get('date')}")
        print(f"Description: {milestone.get('description')}")
    
    return response.json()

if __name__ == "__main__":
    # Test the server is running
    try:
        response = requests.get(BASE_URL)
        print(f"Server status: {response.text}")
    except requests.ConnectionError:
        print("ERROR: Could not connect to server. Make sure the Flask app is running.")
        exit(1)
    
    # Choose which tests to run
    # test_add_internship()
    # test_add_milestone()
    test_get_internships()
    test_get_milestones() 