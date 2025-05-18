# SmartCareer Backend

A Flask-based backend for the SmartCareer app, providing career management features and AI-powered career insights using Google's Gemini API.

## Features

- User registration and authentication
- Internship and milestone tracking
- Resume feedback using Gemini AI
- Career advice recommendations
- Detailed career roadmap generation
- RESTful API for Android clients

## Setup Instructions

### Prerequisites

- Python 3.9+ 
- MySQL (via XAMPP or standalone)
- Google Gemini API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smartcareer-backend.git
   cd smartcareer-backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=models/gemini-1.5-pro
   CACHE_TIMEOUT=86400
   MAX_REQUESTS_PER_MINUTE=60
   
   # Optional database config (defaults are set for XAMPP)
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=smartcareer_db
   ```

5. Set up the database:
   - Start your MySQL server (e.g., via XAMPP)
   - Create a database named `smartcareer_db`
   - Create the required tables:

   ```sql
   CREATE TABLE users (
     id INT AUTO_INCREMENT PRIMARY KEY,
     email VARCHAR(255) UNIQUE NOT NULL,
     password_hash VARCHAR(255) NOT NULL
   );

   CREATE TABLE internships (
     id INT AUTO_INCREMENT PRIMARY KEY,
     user_id INT NOT NULL,
     company VARCHAR(255) NOT NULL,
     role VARCHAR(255) NOT NULL,
     dates VARCHAR(255) NOT NULL,
     description TEXT,
     filename VARCHAR(255),
     FOREIGN KEY (user_id) REFERENCES users(id)
   );

   CREATE TABLE milestones (
     id INT AUTO_INCREMENT PRIMARY KEY,
     user_id INT NOT NULL,
     title VARCHAR(255) NOT NULL,
     date DATE NOT NULL,
     description TEXT,
     filename VARCHAR(255),
     FOREIGN KEY (user_id) REFERENCES users(id)
   );
   ```

6. Run the server:
   ```
   python app.py
   ```

The server will start at `http://localhost:5000`.

## API Endpoints

### Authentication

- **POST /register**: Register a new user
  - Parameters: `email`, `password`
  - Returns: User registration status

- **POST /login**: Authenticate a user
  - Parameters: `email`, `password`
  - Returns: Authentication status and user ID

### Internships

- **POST /add_internship**: Add a new internship
  - Parameters: `email`, `company`, `role`, `dates`, `description`, `attachment` (optional)
  - Returns: Internship submission status

- **GET /get_internships**: Get internships for a user
  - Parameters: `email`
  - Returns: List of internships

### Milestones

- **POST /add_milestone**: Add a new milestone
  - Parameters: `email`, `title`, `date`, `description`, `attachment` (optional)
  - Returns: Milestone submission status

- **GET /get_milestones**: Get milestones for a user
  - Parameters: `email`
  - Returns: List of milestones

### AI-Powered Career Insights

- **POST /api/resume-feedback**: Get AI-generated resume feedback
  - Body: JSON with `email`, `internships` (optional), `milestones` (optional), `skills` (optional)
  - Returns: Resume feedback with general assessment, strengths, and improvement areas

- **POST /api/career-advice**: Get AI-generated career advice
  - Body: JSON with `email`, `internships` (optional), `milestones` (optional), `skills` (optional)
  - Returns: Career advice with certification recommendations, skill suggestions, and tips

- **POST /api/detailed-roadmap**: Get AI-generated career roadmap
  - Body: JSON with `email`, `internships` (optional), `milestones` (optional), `skills` (optional)
  - Returns: Detailed career roadmap with job titles and descriptions

## Using with Android

In your Android app, use Retrofit to connect to these endpoints. For emulator testing, use `10.0.2.2:5000` instead of `localhost:5000`.

Example Retrofit interface:

```kotlin
interface ApiService {
    @POST("/login")
    @FormUrlEncoded
    fun loginUser(
        @Field("email") email: String,
        @Field("password") password: String
    ): Call<LoginResponse>

    @GET("/get_internships")
    fun getUserInternships(
        @Query("email") email: String
    ): Call<List<Map<String, String>>>

    @POST("/api/resume-feedback")
    fun getResumeFeedback(
        @Body userData: Map<String, Any>
    ): Call<ResumeFeedback>
}
```

## Testing

Run the test scripts to verify functionality:

```
python test_api.py            # Test basic endpoints
python test_gemini_integration.py   # Test Gemini-powered endpoints
```

## Error Handling

The API includes comprehensive error handling and logging. Check the console output for diagnostic information.

## Caching and Rate Limiting

Gemini API requests are cached to minimize API calls and costs. Rate limiting is applied to prevent exceeding Google's rate limits.

## License

MIT 