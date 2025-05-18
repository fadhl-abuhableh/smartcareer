import requests
import json

# For Android emulator, local host on development machine is 10.0.2.2
EMULATOR_BASE_URL = "http://10.0.2.2:5000"  # This is how Android emulator accesses localhost
USER_EMAIL = "fadil.12577@gmail.com"  # This user exists in the database

def test_android_login():
    """Test the login endpoint"""
    print("\n===== TESTING ANDROID LOGIN =====")
    print(f"URL: {EMULATOR_BASE_URL}/login")
    
    data = {
        'email': USER_EMAIL,
        'password': 'testpassword'  # Use an actual password that exists in your DB
    }
    
    try:
        response = requests.post(f"{EMULATOR_BASE_URL}/login", data=data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_android_get_internships():
    """
    This simulates what your Android app would be doing when fetching internships.
    When testing on an Android emulator, you'd use 10.0.2.2 instead of localhost.
    """
    print("\n===== TESTING ANDROID GET INTERNSHIPS =====")
    print(f"URL: {EMULATOR_BASE_URL}/get_internships?email={USER_EMAIL}")
    
    try:
        # This is how your Android app would call the API
        response = requests.get(f"{EMULATOR_BASE_URL}/get_internships", params={'email': USER_EMAIL})
        
        # Check if the request was successful
        if response.status_code == 200:
            internships = response.json()
            print(f"✅ Success! Found {len(internships)} internships")
            
            # Print a sample of the data
            if internships:
                print("\nSample internship data (first item):")
                print(json.dumps(internships[0], indent=2))
            
            # This is the kind of data your Android app would receive
            return internships
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server at 10.0.2.2:5000")
        print("Make sure:")
        print("1. Your Flask server is running")
        print("2. Your emulator has network access")
        print("3. You've allowed network access in your app's permissions")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def test_android_get_milestones():
    """Test the get_milestones endpoint"""
    print("\n===== TESTING ANDROID GET MILESTONES =====")
    print(f"URL: {EMULATOR_BASE_URL}/get_milestones?email={USER_EMAIL}")
    
    try:
        response = requests.get(f"{EMULATOR_BASE_URL}/get_milestones", params={'email': USER_EMAIL})
        
        if response.status_code == 200:
            milestones = response.json()
            print(f"✅ Success! Found {len(milestones)} milestones")
            
            if milestones:
                print("\nSample milestone data (first item):")
                print(json.dumps(milestones[0], indent=2))
            
            return milestones
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def test_android_resume_feedback():
    """Test the resume feedback endpoint"""
    print("\n===== TESTING ANDROID RESUME FEEDBACK =====")
    print(f"URL: {EMULATOR_BASE_URL}/api/resume-feedback")
    
    # Prepare test data similar to what your Android app would send
    data = {
        "email": USER_EMAIL,
        "skills": ["Python", "Flask", "SQL", "RESTful API", "Android Development"]
    }
    
    try:
        response = requests.post(f"{EMULATOR_BASE_URL}/api/resume-feedback", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Got resume feedback")
            print("\nFeedback summary:")
            print(f"General: {result.get('general', '')[:50]}...")
            print(f"Strengths: {result.get('strengths', '')[:50]}...")
            return result
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def test_android_career_advice():
    """Test the career advice endpoint"""
    print("\n===== TESTING ANDROID CAREER ADVICE =====")
    print(f"URL: {EMULATOR_BASE_URL}/api/career-advice")
    
    # Prepare test data
    data = {
        "email": USER_EMAIL,
        "skills": ["Python", "Flask", "SQL", "RESTful API", "Android Development"]
    }
    
    try:
        response = requests.post(f"{EMULATOR_BASE_URL}/api/career-advice", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Got career advice")
            print("\nAdvice summary:")
            print(f"Certifications: {result.get('certifications', '')[:50]}...")
            return result
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def test_android_detailed_roadmap():
    """Test the detailed roadmap endpoint"""
    print("\n===== TESTING ANDROID DETAILED ROADMAP =====")
    print(f"URL: {EMULATOR_BASE_URL}/api/detailed-roadmap")
    
    # Prepare test data
    data = {
        "email": USER_EMAIL,
        "skills": ["Python", "Flask", "SQL", "RESTful API", "Android Development"]
    }
    
    try:
        response = requests.post(f"{EMULATOR_BASE_URL}/api/detailed-roadmap", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Got detailed roadmap with {len(result)} steps")
            if result and len(result) > 0:
                print(f"\nFirst step: {result[0].get('title', '')}")
            return result
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def print_retrofit_examples():
    """Print examples of Retrofit implementations for all endpoints"""
    print("\n===== ANDROID RETROFIT IMPLEMENTATION EXAMPLES =====")
    print("""
// In your ApiService.kt interface:

// 1. Login
@POST("/login")
@FormUrlEncoded
fun loginUser(
    @Field("email") email: String,
    @Field("password") password: String
): Call<LoginResponse>

// 2. Get Internships
@GET("/get_internships")
fun getUserInternships(
    @Query("email") email: String
): Call<List<Map<String, String>>>

// 3. Get Milestones
@GET("/get_milestones")
fun getUserMilestones(
    @Query("email") email: String
): Call<List<Map<String, String>>>

// 4. Resume Feedback
@POST("/api/resume-feedback")
fun getResumeFeedback(
    @Body userData: Map<String, Any>
): Call<ResumeFeedbackResponse>

// 5. Career Advice
@POST("/api/career-advice")
fun getCareerAdvice(
    @Body userData: Map<String, Any>
): Call<CareerAdviceResponse>

// 6. Detailed Roadmap
@POST("/api/detailed-roadmap")
fun getDetailedRoadmap(
    @Body userData: Map<String, Any>
): Call<List<RoadmapStep>>

// Example response models:
data class LoginResponse(
    val message: String,
    val user_id: Int,
    val email: String
)

data class ResumeFeedbackResponse(
    val general: String,
    val strengths: String,
    val improvements: String
)

data class CareerAdviceResponse(
    val certifications: String,
    val skills: String,
    val tips: String
)

data class RoadmapStep(
    val title: String,
    val description: String
)
    """)

if __name__ == "__main__":
    # Note: This won't actually connect to 10.0.2.2 unless run from an Android emulator
    # For testing, change EMULATOR_BASE_URL to "http://localhost:5000" if running on your dev machine
    
    print("Note: This script simulates how an Android emulator would access your API.")
    print("When running on your development machine, it will likely fail to connect to 10.0.2.2")
    print("To test locally, change EMULATOR_BASE_URL to 'http://localhost:5000'\n")
    
    # For local testing only:
    EMULATOR_BASE_URL = "http://localhost:5000"  # Override for local testing
    
    # Run tests for all endpoints
    print("Testing all endpoints that your Android app expects...")
    
    try:
        # Test connection to server
        response = requests.get(EMULATOR_BASE_URL)
        print(f"Server status: {response.text}")
        
        # Test all endpoints
        test_android_login()
        test_android_get_internships()
        test_android_get_milestones()
        test_android_resume_feedback()
        test_android_career_advice()
        test_android_detailed_roadmap()
        
        # Print Retrofit implementation examples
        print_retrofit_examples()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {str(e)}") 