import time
import logging
import json
import requests
from functools import wraps
import os
from dotenv import load_dotenv
import config

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_service_hf')

# Load environment variables
load_dotenv()

# Initialize Hugging Face API credentials
try:
    hf_api_key = os.getenv('HF_API_KEY')
    if not hf_api_key:
        logger.error("Hugging Face API key not found in environment variables")
        raise ValueError("Hugging Face API key not found")
    
    logger.info("Hugging Face API credentials loaded successfully")
except Exception as e:
    logger.error(f"Failed to initialize Hugging Face API: {e}")

# Simple in-memory cache
cache = {}

# Rate limiting setup
request_timestamps = []
MAX_REQUESTS = config.MAX_REQUESTS_PER_MINUTE
REQUEST_WINDOW = 60  # 1 minute in seconds

def rate_limited(func):
    """Decorator to apply rate limiting to a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global request_timestamps
        
        current_time = time.time()
        # Clean up old timestamps
        request_timestamps = [ts for ts in request_timestamps if current_time - ts < REQUEST_WINDOW]
        
        # Check if we're over the limit
        if len(request_timestamps) >= MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded ({MAX_REQUESTS} requests per minute)")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Add current timestamp
        request_timestamps.append(current_time)
        
        # Call the actual function
        return func(*args, **kwargs)
    
    return wrapper

def get_cache_key(prompt, model_name):
    """Generate a cache key based on request parameters"""
    return f"{hash(prompt)}:{model_name}"

@rate_limited
def generate_completion(prompt, model_name='google/flan-t5-xxl'):
    """
    Send a request to Hugging Face API and handle caching, rate limiting, and errors
    """
    # Check cache first
    cache_key = get_cache_key(prompt, model_name)
    if cache_key in cache:
        logger.info("Cache hit - returning cached response")
        return cache[cache_key]
    
    api_key = os.getenv('HF_API_KEY')
    if not api_key:
        logger.error("Hugging Face API key not properly initialized or missing")
        raise Exception("Hugging Face integration is not properly configured")
    
    try:
        logger.info(f"Sending request to Hugging Face API with model: {model_name}")
        
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 1024,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        # Send request to Hugging Face API
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Check response status
        if response.status_code == 200:
            # Parse response based on model output format
            result = response.json()
            
            # Different models return different response structures
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    # Text generation models
                    response_text = result[0]["generated_text"]
                else:
                    # Other response formats
                    response_text = str(result)
            else:
                response_text = str(result)
            
            logger.info("Successfully received response from Hugging Face API")
            
            # Cache the result
            cache[cache_key] = response_text
            
            return response_text
        else:
            # If we got a model loading error, wait and retry
            if response.status_code == 503 and "Loading" in response.text:
                logger.info("Model is loading, waiting for 10 seconds and retrying...")
                time.sleep(10)
                return generate_completion(prompt, model_name)
            
            # Handle error responses
            error_msg = f"Hugging Face API Error: Status {response.status_code} - {response.text}"
            logger.error(error_msg)
            # Fall back to default responses rather than raising an exception
            logger.info("Using fallback response due to API error")
            return None
        
    except Exception as e:
        logger.error(f"Hugging Face API Error: {e}")
        # Fall back to default responses rather than raising an exception
        logger.info("Using fallback response due to exception")
        return None

def generate_resume_feedback(user_data):
    """Generate resume feedback based on user data"""
    try:
        # Construct a detailed prompt for resume feedback
        prompt = f"""
        Based on the following user information, provide professional resume feedback:
        
        USER PROFILE:
        Email: {user_data.get('email', 'Not provided')}
        
        INTERNSHIPS:
        {format_experiences(user_data.get('internships', []))}
        
        SKILLS:
        {', '.join(user_data.get('skills', ['Not provided']))}
        
        MILESTONES:
        {format_experiences(user_data.get('milestones', []))}
        
        Please provide feedback in JSON format with the following structure:
        {{
            "general": "Overall assessment of the resume",
            "strengths": "Bullet points listing strengths (use • as bullet character)",
            "improvements": "Bullet points listing areas for improvement (use • as bullet character)"
        }}
        
        Make the feedback specific, actionable, and focused on helping the user improve their resume for job applications.
        Respond ONLY with the JSON, no additional text.
        """
        
        response_text = generate_completion(prompt)
        
        # If API call failed and returned None, use fallback response
        if response_text is None:
            logger.info("Using fallback response for resume feedback")
            return config.FALLBACK_RESPONSES['resume_feedback']
        
        # Parse the JSON response
        try:
            # First try to parse the entire response as JSON
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract the JSON part from the text response
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    raise Exception("Could not find valid JSON in response")
            except Exception as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                # Fall back to the default response
                return config.FALLBACK_RESPONSES['resume_feedback']
        
        # Validate that the result has the expected structure
        required_fields = ["general", "strengths", "improvements"]
        for field in required_fields:
            if field not in result:
                result[field] = config.FALLBACK_RESPONSES['resume_feedback'][field]
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating resume feedback: {e}")
        return config.FALLBACK_RESPONSES['resume_feedback']

def generate_career_advice(user_data):
    """Generate career advice based on user data"""
    try:
        # Construct a detailed prompt for career advice
        prompt = f"""
        Based on the following user information, provide career advice tailored to their profile:
        
        USER PROFILE:
        Email: {user_data.get('email', 'Not provided')}
        
        INTERNSHIPS:
        {format_experiences(user_data.get('internships', []))}
        
        SKILLS:
        {', '.join(user_data.get('skills', ['Not provided']))}
        
        MILESTONES:
        {format_experiences(user_data.get('milestones', []))}
        
        Please provide career advice in JSON format with the following structure:
        {{
            "certifications": "Recommended certifications that would enhance their profile",
            "skills": "Skills they should develop to advance their career",
            "tips": "Practical tips for job applications and interviews"
        }}
        
        Make the advice practical, specific to their field, and actionable.
        Respond ONLY with the JSON, no additional text.
        """
        
        response_text = generate_completion(prompt)
        
        # If API call failed and returned None, use fallback response
        if response_text is None:
            logger.info("Using fallback response for career advice")
            return config.FALLBACK_RESPONSES['career_advice']
        
        # Parse the JSON response
        try:
            # First try to parse the entire response as JSON
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract the JSON part from the text response
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    raise Exception("Could not find valid JSON in response")
            except Exception as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                # Fall back to the default response
                return config.FALLBACK_RESPONSES['career_advice']
        
        # Validate that the result has the expected structure
        required_fields = ["certifications", "skills", "tips"]
        for field in required_fields:
            if field not in result:
                result[field] = config.FALLBACK_RESPONSES['career_advice'][field]
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating career advice: {e}")
        return config.FALLBACK_RESPONSES['career_advice']

def generate_detailed_roadmap(user_data):
    """Generate a detailed career roadmap based on user data"""
    try:
        # Construct a detailed prompt for a career roadmap
        prompt = f"""
        Based on the following user information, provide a detailed career roadmap:
        
        USER PROFILE:
        Email: {user_data.get('email', 'Not provided')}
        
        INTERNSHIPS:
        {format_experiences(user_data.get('internships', []))}
        
        SKILLS:
        {', '.join(user_data.get('skills', ['Not provided']))}
        
        MILESTONES:
        {format_experiences(user_data.get('milestones', []))}
        
        Please provide a career roadmap in JSON format as an array of objects with the following structure:
        [
            {{
                "title": "Job title or position",
                "description": "Detailed description of the role, skills needed, and how to achieve it"
            }},
            // More steps in the roadmap...
        ]
        
        Provide 3-5 steps that form a clear progression path based on their current skills and experience.
        For each step, include actionable advice on how to reach that position.
        Respond ONLY with the JSON array, no additional text.
        """
        
        response_text = generate_completion(prompt)
        
        # If API call failed and returned None, use fallback response
        if response_text is None:
            logger.info("Using fallback response for detailed roadmap")
            return config.FALLBACK_RESPONSES['detailed_roadmap']
        
        # Parse the JSON response
        try:
            # First try to parse the entire response as JSON
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract the JSON part from the text response
            try:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    raise Exception("Could not find valid JSON array in response")
            except Exception as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                # Fall back to the default response
                return config.FALLBACK_RESPONSES['detailed_roadmap']
        
        # Validate that the result has the expected structure
        if not isinstance(result, list) or len(result) == 0:
            return config.FALLBACK_RESPONSES['detailed_roadmap']
            
        for item in result:
            if not isinstance(item, dict) or 'title' not in item or 'description' not in item:
                return config.FALLBACK_RESPONSES['detailed_roadmap']
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating detailed roadmap: {e}")
        return config.FALLBACK_RESPONSES['detailed_roadmap']

def format_experiences(experiences):
    """Format a list of experiences (internships or milestones) into a string"""
    if not experiences or len(experiences) == 0:
        return "None"
    
    formatted = []
    for idx, exp in enumerate(experiences, 1):
        if isinstance(exp, dict):
            if 'company' in exp:  # It's an internship
                company = exp.get('company', 'Unknown')
                role = exp.get('role', 'Unknown')
                dates = exp.get('dates', 'Unknown')
                description = exp.get('description', 'No description provided')
                formatted.append(f"{idx}. {role} at {company} ({dates}): {description}")
            elif 'title' in exp:  # It's a milestone
                title = exp.get('title', 'Unknown')
                date = exp.get('date', 'Unknown')
                description = exp.get('description', 'No description provided')
                formatted.append(f"{idx}. {title} ({date}): {description}")
    
    return "\n".join(formatted) if formatted else "None" 