import requests
import json

def test_detailed_roadmap():
    url = "http://localhost:5000/api/detailed-roadmap"
    headers = {"Content-Type": "application/json"}
    data = {
        "email": "test@example.com",
        "skills": ["Python", "Flask", "SQL"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print("\nResponse:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_detailed_roadmap() 