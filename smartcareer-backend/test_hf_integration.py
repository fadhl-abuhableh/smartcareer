import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server URL - change this to your actual server URL if different
SERVER_URL = "http://127.0.0.1:5000"

# Test user data
test_user = {
    "email": "test@example.com",
    "skills": ["Python", "Flask", "Android Development", "Java", "Kotlin"],
    "internships": [
        {
            "company": "Tech Solutions Inc.",
            "role": "Software Developer Intern",
            "dates": "Jun 2023 - Aug 2023",
            "description": "Worked on backend APIs and implemented new features for the company's mobile app"
        }
    ],
    "milestones": [
        {
            "title": "Completed Android Development Course",
            "date": "May 2023",
            "description": "Learned Android app development using Kotlin and Java"
        }
    ]
}

def test_resume_feedback():
    print("\n🧾 Testing Resume Feedback Endpoint...")
    try:
        response = requests.post(
            f"{SERVER_URL}/api/resume-feedback",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Resume Feedback API call successful!")
            data = response.json()
            print("\nResponse:")
            print(f"General Feedback: {data.get('general', 'No general feedback')}")
            print("\nStrengths:")
            print(data.get('strengths', 'No strengths listed'))
            print("\nAreas for Improvement:")
            print(data.get('improvements', 'No improvements listed'))
            return True
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_career_advice():
    print("\n💼 Testing Career Advice Endpoint...")
    try:
        response = requests.post(
            f"{SERVER_URL}/api/career-advice",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Career Advice API call successful!")
            data = response.json()
            print("\nResponse:")
            print(f"Recommended Certifications: {data.get('certifications', 'No certifications recommended')}")
            print(f"\nSkills to Develop: {data.get('skills', 'No skills listed')}")
            print(f"\nPractical Tips: {data.get('tips', 'No tips provided')}")
            return True
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_detailed_roadmap():
    print("\n🗺️ Testing Detailed Roadmap Endpoint...")
    try:
        response = requests.post(
            f"{SERVER_URL}/api/detailed-roadmap",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Detailed Roadmap API call successful!")
            data = response.json()
            print("\nCareer Roadmap:")
            for i, step in enumerate(data, 1):
                print(f"\nStep {i}: {step.get('title', 'No title')}")
                print(f"Description: {step.get('description', 'No description')}")
            return True
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Hugging Face Integration Tests")
    
    # Check if the API key is set
    api_key = os.getenv('HF_API_KEY')
    if not api_key:
        print("⚠️ Warning: HF_API_KEY not found in .env file. Tests will use fallback responses.")
    else:
        print(f"✅ HF_API_KEY found (length: {len(api_key)})")
    
    print("\n📋 Note: Due to API permission issues, the system will likely use fallback responses")
    print("   This test is to verify the API endpoints work correctly even with fallback logic")
    
    # Run the tests
    resume_result = test_resume_feedback()
    career_result = test_career_advice()
    roadmap_result = test_detailed_roadmap()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"Resume Feedback: {'✅ Passed' if resume_result else '❌ Failed'}")
    print(f"Career Advice: {'✅ Passed' if career_result else '❌ Failed'}")
    print(f"Detailed Roadmap: {'✅ Passed' if roadmap_result else '❌ Failed'}")
    
    if resume_result and career_result and roadmap_result:
        print("\n🎉 All tests passed! The API endpoints are working correctly with fallback responses.")
        print("You can upgrade your Hugging Face account to get Inference API access,")
        print("or keep using the fallback responses for now.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above for details.") 