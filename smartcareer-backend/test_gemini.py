import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from .env - we'll need to update the .env file with a Gemini API key
api_key = os.getenv('GEMINI_API_KEY')
print(f"Gemini API Key available: {'Yes' if api_key else 'No'}")

# Configure the Gemini API
if api_key:
    genai.configure(api_key=api_key)
else:
    print("No API key found. Please add GEMINI_API_KEY to your .env file.")
    exit(1)

try:
    # List available models
    print("\nAvailable models:")
    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(f"- {model.name}")
    
    # Get the Gemini model
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    
    # Generate a response
    response = model.generate_content("Provide a brief career tip for software developers")
    
    # Print the response
    print("\nGemini response:")
    print(response.text)
    print("\nGemini API is working correctly!")
    
except Exception as e:
    print(f"\nError with Gemini API: {e}")
    print("API key might be invalid or there might be connection issues.") 