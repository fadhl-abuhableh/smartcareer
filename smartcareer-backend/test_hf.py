import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from .env
api_key = os.getenv('HF_API_KEY')
print(f"Hugging Face API Key available: {'Yes' if api_key else 'No'}")

# Default model to test
MODEL = "google/flan-t5-xxl"  # A more accessible model

# Test with API directly before integrating
def test_huggingface_api():
    if not api_key:
        print("No API key found. Please add HF_API_KEY to your .env file.")
        return False
    
    try:
        # Set up the API call
        API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple test prompt
        payload = {
            "inputs": "Provide a brief career tip for software developers. Keep it concise and practical.",
            "parameters": {
                "max_length": 100,  # Use max_length instead of max_new_tokens for T5 models
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        print(f"\nTesting connection to Hugging Face API with model: {MODEL}")
        
        # Make the request
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            
            print("\nResponse from Hugging Face API:")
            
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    print(result[0]["generated_text"])
                else:
                    print(result)
            else:
                print(result)
                
            print("\nHugging Face API is working correctly!")
            return True
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\nError connecting to Hugging Face API: {e}")
        return False

# Test JSON structure
def test_json_generation():
    if not api_key:
        print("No API key found. Please add HF_API_KEY to your .env file.")
        return False
    
    try:
        # Set up the API call
        API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test prompt for JSON response
        json_prompt = """
        Generate a resume feedback in JSON format with the following structure:
        {
            "general": "Overall assessment of the resume",
            "strengths": "Bullet points listing strengths (use • as bullet character)",
            "improvements": "Bullet points listing areas for improvement (use • as bullet character)"
        }
        
        Make the feedback specific, actionable, and focused on a software developer.
        Respond ONLY with the JSON, no additional text.
        """
        
        payload = {
            "inputs": json_prompt,
            "parameters": {
                "max_length": 500,  # Use max_length instead of max_new_tokens for T5 models
                "temperature": 0.3,  # Lower temperature for more structured output
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        print(f"\nTesting JSON generation with Hugging Face API")
        
        # Make the request
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            
            print("\nJSON Response:")
            
            # Extract the generated text
            generated_text = ""
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    generated_text = result[0]["generated_text"]
                else:
                    generated_text = str(result)
            else:
                generated_text = str(result)
            
            print(generated_text)
            
            # Try to parse JSON from the response
            try:
                # First try to parse the entire response as JSON
                json_data = json.loads(generated_text)
                print("\nSuccessfully parsed JSON response!")
                return True
            except json.JSONDecodeError:
                # If that fails, try to extract the JSON part from the text response
                try:
                    json_start = generated_text.find('{')
                    json_end = generated_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = generated_text[json_start:json_end]
                        json_data = json.loads(json_str)
                        print("\nSuccessfully extracted and parsed JSON from response!")
                        return True
                    else:
                        print("\nCould not find valid JSON in response.")
                        return False
                except Exception as e:
                    print(f"\nError parsing JSON: {e}")
                    return False
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\nError in JSON test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Hugging Face API Tests")
    
    # First test the basic API connection
    api_test_result = test_huggingface_api()
    
    # Then test JSON generation specifically
    json_test_result = test_json_generation()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"Basic API Connection: {'✅ Passed' if api_test_result else '❌ Failed'}")
    print(f"JSON Response Generation: {'✅ Passed' if json_test_result else '❌ Failed'}")
    
    if api_test_result and json_test_result:
        print("\n🎉 All tests passed! The Hugging Face API is ready to use.")
        print("You can now update your .env file with:")
        print(f"HF_API_KEY={api_key}")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.") 