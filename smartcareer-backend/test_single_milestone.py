import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
USER_EMAIL = "fadil.12577@gmail.com"  # This user exists in the database

def test_milestone_with_description():
    print("\n===== ADDING MILESTONE WITH DESCRIPTION =====")
    
    # Test data
    data = {
        'email': USER_EMAIL,
        'title': 'Completed Android Project',
        'date': '2023-08-10',
        'description': 'Built a native Android application with Kotlin and integrated with RESTful API.'
    }
    
    # Send request to add the milestone
    print(f"Sending request to add milestone for {USER_EMAIL}...")
    response = requests.post(f"{BASE_URL}/add_milestone", data=data)
    
    # Print results
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    milestone_id = response.json().get('milestone_id')
    
    if milestone_id:
        print("\n===== FETCHING ADDED MILESTONE =====")
        # Now fetch the milestone to verify it was added with the description
        response = requests.get(f"{BASE_URL}/get_milestones", params={'email': USER_EMAIL})
        
        if response.status_code == 200:
            milestones = response.json()
            print(f"Found {len(milestones)} milestones")
            
            # Look for our new milestone
            found = False
            for milestone in milestones:
                if str(milestone.get('id')) == str(milestone_id):
                    found = True
                    print("\nNewly added milestone:")
                    print(f"ID: {milestone.get('id')}")
                    print(f"Title: {milestone.get('title')}")
                    print(f"Date: {milestone.get('date')}")
                    print(f"Description: {milestone.get('description')}")
                    break
            
            if not found:
                print(f"❌ Could not find newly added milestone with ID {milestone_id}")
        else:
            print(f"❌ Error fetching milestones: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    # Test the server is running
    try:
        response = requests.get(BASE_URL)
        print(f"Server status: {response.text}")
    except requests.ConnectionError:
        print("ERROR: Could not connect to server. Make sure the Flask app is running.")
        exit(1)
    
    # Run the test
    test_milestone_with_description() 