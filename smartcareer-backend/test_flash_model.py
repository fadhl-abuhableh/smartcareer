import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv('GEMINI_API_KEY')
print(f"API key available: {'Yes' if api_key else 'No'}")

# Configure Gemini
genai.configure(api_key=api_key)

try:
    # Try using a smaller model (gemini-1.5-flash-8b)
    model = genai.GenerativeModel('models/gemini-1.5-flash-8b')
    print(f"Using model: models/gemini-1.5-flash-8b")
    
    # Generate a simple response
    response = model.generate_content('Hello, how are you?')
    
    # Print the response
    print("\nResponse from model:")
    print(response.text)
    print("\nTest successful! The smaller Gemini model is working.")
    
except Exception as e:
    print(f"\nError: {e}")
    print("The model is still having quota issues or other errors.") 