import time
import logging
import json
from functools import wraps
import google.generativeai as genai
import os
from dotenv import load_dotenv
import config

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_service_gemini')

# Load environment variables
load_dotenv()

# Initialize Gemini client
try:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("Gemini API key not found in environment variables")
        raise ValueError("Missing GEMINI_API_KEY in .env file")
    elif api_key == 'your_api_key_here':
        logger.error("Default API key detected. Please update with actual Gemini API key")
        raise ValueError("Please update GEMINI_API_KEY in .env file with your actual API key")
    
    genai.configure(api_key=api_key)
    
    # Test the API key by making a simple request
    model = genai.GenerativeModel('models/gemini-1.5-flash-8b')
    test_response = model.generate_content("Test")
    if test_response and test_response.text:
        logger.info("Gemini client initialized and tested successfully")
    else:
        raise ValueError("API key validation failed")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    raise

# Simple in-memory cache
cache = {}
cache_timestamps = {}  # To track when entries were added

# Rate limiting setup
request_timestamps = []
MAX_REQUESTS = config.MAX_REQUESTS_PER_MINUTE
REQUEST_WINDOW = 60  # 1 minute in seconds
CACHE_TIMEOUT = config.CACHE_TIMEOUT  # Cache timeout in seconds

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
    # Use a more robust hashing method
    import hashlib
    key_string = f"{prompt}:{model_name}"
    return hashlib.md5(key_string.encode()).hexdigest()

@rate_limited
def generate_completion(prompt, model_name='models/gemini-1.5-flash-8b', validate_json=True):
    """
    Send a request to Gemini API and handle caching, rate limiting, and errors
    """
    try:
        logger.info(f"Sending request to Gemini API with model: {model_name}")
        
        # Create a generative model
        model = genai.GenerativeModel(model_name)
        
        # Generate content with safety settings and specific parameters
        generation_config = {
            "temperature": 0.7,  # Lower temperature for more structured output
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Extract response text
        if not response or not response.text:
            logger.error("Empty response received from Gemini API")
            raise Exception("Empty response from AI service")
            
        response_text = response.text.strip()
        if not response_text:
            logger.error("Empty text in response")
            raise Exception("Empty text in AI response")
            
        # Log the raw response for debugging
        logger.debug(f"Raw response from Gemini API: {response_text}")
        
        # Try to clean the response text
        # Remove any potential markdown formatting
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "")
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "")
            
        response_text = response_text.strip()
        
        # Only validate JSON if required
        if validate_json:
            try:
                json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Response is not valid JSON, attempting repair")
                # Try to extract JSON structure
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    response_text = response_text[json_start:json_end]
                    # Validate the extracted JSON
                    try:
                        json.loads(response_text)
                    except json.JSONDecodeError:
                        raise Exception("Could not repair JSON response")
                else:
                    raise Exception("Could not find JSON structure in response")
        
        logger.info("Successfully received response from Gemini API")
        return response_text
        
    except Exception as e:
        logger.error(f"Gemini API Error with model {model_name}: {e}")
        raise

def generate_resume_feedback(user_data):
    """Generate resume feedback based on user data"""
    try:
        # Construct a detailed prompt for resume feedback
        prompt = f"""You are a professional resume reviewer. Your task is to provide resume feedback in JSON format.

USER PROFILE:
Email: {user_data.get('email', 'Not provided')}

INTERNSHIPS:
{format_experiences(user_data.get('internships', []))}

SKILLS:
{', '.join(user_data.get('skills', ['Not provided']))}

MILESTONES:
{format_experiences(user_data.get('milestones', []))}

INSTRUCTIONS:
1. Analyze the information above
2. Respond with ONLY a JSON object
3. Do not include any other text, markdown, or formatting
4. Use exactly this format:

{{
    "general": "Write a detailed paragraph about overall assessment",
    "strengths": "• First strength\\n• Second strength\\n• Third strength",
    "improvements": "• First improvement\\n• Second improvement\\n• Third improvement"
}}

Remember:
- Only output valid JSON
- No text before or after the JSON
- Use proper escaping for newlines (\\n)
- Start each bullet point with •
"""
        
        response_text = generate_completion(prompt)
        
        # Log the response we're trying to parse
        logger.debug(f"Attempting to parse JSON from: {response_text}")
        
        try:
            # First try to parse the entire response as JSON
            result = json.loads(response_text)
            logger.info("Successfully parsed JSON response")
            
            # Validate the structure and content
            if not isinstance(result, dict):
                raise ValueError("Response is not a JSON object")
                
            required_fields = ["general", "strengths", "improvements"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
                if not isinstance(result[field], str) or not result[field].strip():
                    raise ValueError(f"Invalid or empty content for field: {field}")
            
            # Ensure bullet points are properly formatted
            for field in ["strengths", "improvements"]:
                if not result[field].startswith("•"):
                    result[field] = "• " + result[field].replace("\n", "\n• ")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Failed to parse JSON: {str(e)}")
            
            # Try to extract and clean JSON
            try:
                # Find JSON-like structure
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    
                    # Clean up the JSON string
                    json_str = (
                        json_str
                        .replace('\n', ' ')  # Remove newlines
                        .replace('\\n', '\\\\n')  # Properly escape \n
                        .replace('\\', '\\\\')  # Escape backslashes
                        .replace('"', '\\"')  # Escape quotes
                        .replace("'", '"')  # Replace single quotes with double quotes
                    )
                    
                    # Ensure proper JSON structure
                    if not json_str.startswith('{'): json_str = '{' + json_str
                    if not json_str.endswith('}'): json_str = json_str + '}'
                    
                    # Log the cleaned JSON string
                    logger.debug(f"Cleaned JSON string: {json_str}")
                    
                    # Try parsing the cleaned JSON
                    result = json.loads(json_str)
                    
                    # Validate and format the result
                    for field in required_fields:
                        if field not in result or not result[field].strip():
                            result[field] = config.FALLBACK_RESPONSES['resume_feedback'][field]
                    
                    return result
                    
                else:
                    logger.error("Could not find valid JSON structure in response")
                    raise Exception("Could not find valid JSON in response")
                    
            except Exception as e:
                logger.error(f"Failed to repair JSON: {e}")
                return config.FALLBACK_RESPONSES['resume_feedback']
                
    except Exception as e:
        logger.error(f"Error generating resume feedback: {e}")
        return config.FALLBACK_RESPONSES['resume_feedback']

def generate_career_advice(user_data):
    """Generate career advice based on user data"""
    try:
        # Construct a detailed prompt for career advice with strict formatting
        prompt = f"""You are a career advisor. Based on the following user information, provide CONCISE career advice in EXACTLY the requested JSON format.

USER PROFILE:
Email: {user_data.get('email', 'Not provided')}

INTERNSHIPS:
{format_experiences(user_data.get('internships', []))}

SKILLS:
{', '.join(user_data.get('skills', ['Not provided']))}

MILESTONES:
{format_experiences(user_data.get('milestones', []))}

INSTRUCTIONS:
1. Analyze the information above
2. Provide advice in EXACTLY this JSON format, with no other text:
{{
    "certifications": "2-3 specific certification recommendations, max 100 chars",
    "skills": "3-4 specific skills to develop, max 100 chars",
    "tips": "3 bullet points for job success, use • for bullets, max 150 chars"
}}

REQUIREMENTS:
- Response must be ONLY valid JSON
- No markdown, no extra text
- Keep each field under the specified length
- For 'tips' field, use bullet points with • symbol
- Be specific and actionable
- Focus on user's field/experience"""

        # Try up to 3 times to get a valid response
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response_text = generate_completion(prompt)
                result = json.loads(response_text)
                
                # Validate and format the response
                required_fields = ["certifications", "skills", "tips"]
                
                # Ensure all required fields exist and are properly formatted
                for field in required_fields:
                    if field not in result or not isinstance(result[field], str):
                        raise ValueError(f"Missing or invalid field: {field}")
                    
                    # Trim responses to max length
                    if field == "tips":
                        if not result[field].startswith("•"):
                            result[field] = "• " + result[field].replace("\n", "\n• ")
                        result[field] = result[field][:150]
                    else:
                        result[field] = result[field][:100]
                
                logger.info(f"Successfully generated career advice on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("All attempts to generate career advice failed")
                    return config.FALLBACK_RESPONSES['career_advice']
                
    except Exception as e:
        logger.error(f"Error generating career advice: {e}")
        return config.FALLBACK_RESPONSES['career_advice']

def generate_detailed_roadmap(user_data):
    """Generate a detailed career roadmap based on user data"""
    try:
        # Construct a detailed prompt with exact format requirements
        prompt = f"""You are a career advisor. Based on the following user information, generate THREE career roadmap steps showing a clear progression path.

USER PROFILE:
Email: {user_data.get('email', 'Not provided')}

INTERNSHIPS:
{format_experiences(user_data.get('internships', []))}

SKILLS:
{', '.join(user_data.get('skills', ['Not provided']))}

MILESTONES:
{format_experiences(user_data.get('milestones', []))}

INSTRUCTIONS:
Generate THREE career steps in this format:
[Job Title 1]

[Brief description of key skills and steps for this role - max 150 chars]

[Job Title 2]

[Brief description of key skills and steps for this role - max 150 chars]

[Job Title 3]

[Brief description of key skills and steps for this role - max 150 chars]

Example format for each step:
Junior Data Analyst

Learn Python, SQL, and data visualization. Build dashboards and analyze data. Create a portfolio with 2-3 data analysis projects.

REQUIREMENTS:
- Generate exactly 3 job titles with descriptions
- Each job title must be max 50 chars
- Each description must be max 150 chars
- Show a clear progression path from entry to advanced level
- Be specific and actionable
- Focus on user's current experience level
- No bullet points or special formatting
- Do not include any instructions or user profile in the response
- ONLY output the job titles and descriptions, nothing else"""

        # Try up to 3 times to get a valid response
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use validate_json=False since we want plain text
                response_text = generate_completion(prompt, validate_json=False)
                
                # Split response into sections (job entries)
                sections = [section.strip() for section in response_text.split('\n\n') if section.strip()]
                
                # Group sections into pairs of title and description
                roadmap = []
                for i in range(0, len(sections), 2):
                    if i + 1 < len(sections):
                        title = sections[i].strip()
                        description = sections[i + 1].strip()
                        
                        # Clean up the description to remove any prompt/instruction text
                        description = description.replace('USER PROFILE:', '').replace('INTERNSHIPS:', '')
                        description = description.replace('SKILLS:', '').replace('MILESTONES:', '')
                        description = description.replace('INSTRUCTIONS:', '').replace('REQUIREMENTS:', '')
                        description = description.replace('EXAMPLE FORMAT:', '').replace('Example format:', '')
                        
                        # Validate content length
                        if len(title) > 50:
                            title = title[:50]
                        if len(description) > 150:
                            description = description[:147] + "..."
                        
                        roadmap.append({
                            "title": title,
                            "description": description.strip()
                        })
                
                # Ensure we have exactly 3 steps
                if len(roadmap) >= 3:
                    roadmap = roadmap[:3]  # Take only first 3 if we got more
                    logger.info(f"Successfully generated roadmap with {len(roadmap)} steps on attempt {attempt + 1}")
                    return roadmap
                else:
                    raise ValueError(f"Generated only {len(roadmap)} steps, need exactly 3")
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("All attempts to generate roadmap failed")
                    return config.FALLBACK_RESPONSES['detailed_roadmap']
                
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

def clean_cache():
    """Clean expired entries from the cache"""
    current_time = time.time()
    expired_keys = [
        key for key, timestamp in cache_timestamps.items()
        if current_time - timestamp > CACHE_TIMEOUT
    ]
    
    for key in expired_keys:
        del cache[key]
        del cache_timestamps[key]
    
    # If cache is still too large, remove oldest entries
    if len(cache) > config.MAX_CACHE_SIZE:
        sorted_entries = sorted(cache_timestamps.items(), key=lambda x: x[1])
        entries_to_remove = sorted_entries[:len(cache) - config.MAX_CACHE_SIZE]
        
        for key, _ in entries_to_remove:
            del cache[key]
            del cache_timestamps[key]
    
    logger.info(f"Cache cleaned. Current size: {len(cache)} entries")

def clear_invalid_cache_entries():
    """Remove any invalid entries from the cache"""
    invalid_keys = []
    
    for key, value in cache.items():
        try:
            # Try to parse the cached value as JSON
            json.loads(value)
        except json.JSONDecodeError:
            invalid_keys.append(key)
    
    for key in invalid_keys:
        del cache[key]
        if key in cache_timestamps:
            del cache_timestamps[key]
    
    if invalid_keys:
        logger.info(f"Removed {len(invalid_keys)} invalid cache entries")

# Clear any invalid cache entries on module load
clear_invalid_cache_entries() 