# SmartCareer Deployment Guide

This document provides instructions for deploying the SmartCareer backend on various environments.

## Contents

1. [Local Deployment](#local-deployment)
2. [Production Deployment](#production-deployment)
   - [Heroku Deployment](#heroku-deployment)
   - [AWS Deployment](#aws-deployment)
3. [Environment Variables](#environment-variables)
4. [Database Setup](#database-setup)
5. [Security Considerations](#security-considerations)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)

## Local Deployment

For local development and testing:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smartcareer-backend.git
   cd smartcareer-backend
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Gemini API key and other configuration variables.

5. Start XAMPP or your MySQL server.

6. Run the application:
   ```
   python app.py
   ```

## Production Deployment

### Heroku Deployment

1. Create a Heroku account and install the Heroku CLI.

2. Create a new Heroku app:
   ```
   heroku create smartcareer-backend
   ```

3. Add a MySQL database add-on:
   ```
   heroku addons:create jawsdb:kitefin
   ```

4. Set environment variables:
   ```
   heroku config:set GEMINI_API_KEY=your_api_key_here
   heroku config:set GEMINI_MODEL=models/gemini-1.5-pro
   heroku config:set MAX_REQUESTS_PER_MINUTE=60
   heroku config:set CACHE_TIMEOUT=86400
   ```

5. Deploy the application:
   ```
   git push heroku main
   ```

6. Run database migrations:
   ```
   heroku run python update_db_schema.py
   ```

### AWS Deployment

1. Create an AWS account.

2. Set up an EC2 instance (Ubuntu recommended).

3. Install necessary packages:
   ```
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```

4. Clone the repository:
   ```
   git clone https://github.com/yourusername/smartcareer-backend.git
   cd smartcareer-backend
   ```

5. Set up a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

6. Create a `.env` file with necessary environment variables.

7. Set up Nginx as a reverse proxy.

8. Set up Gunicorn to run the Flask application:
   ```
   gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
   ```

9. Set up Supervisor to keep the application running.

## Environment Variables

Required environment variables:

| Variable | Description |
|----------|-------------|
| GEMINI_API_KEY | Your Google Gemini API key |
| GEMINI_MODEL | Gemini model to use (default: models/gemini-1.5-pro) |
| DB_HOST | Database host |
| DB_USER | Database username |
| DB_PASSWORD | Database password |
| DB_NAME | Database name |
| MAX_REQUESTS_PER_MINUTE | Rate limiting for API calls |
| CACHE_TIMEOUT | Cache timeout in seconds |

## Database Setup

1. Create the required tables in your MySQL database:

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

## Security Considerations

1. **API Key Protection**: Never expose your Gemini API key in client-side code. Always keep it on the server.

2. **Password Storage**: Currently using simple password storage. For production, implement proper password hashing with salt (e.g., using bcrypt).

3. **HTTPS**: Always use HTTPS in production. Set up SSL certificates with Let's Encrypt.

4. **Input Validation**: Implement thorough input validation for all API endpoints.

5. **Rate Limiting**: Implement IP-based rate limiting to prevent abuse.

## Maintenance

1. Regularly update dependencies to patch security vulnerabilities.

2. Monitor your API usage and costs with Google.

3. Implement a backup system for your database.

4. Set up logging to monitor application performance and errors.

## Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**: Verify your database credentials and ensure the MySQL server is running.

2. **File Upload Problems**: Check folder permissions for the uploads directory.

3. **Gemini API Issues**: Check your API key and make sure you have sufficient quota.

4. **Performance Issues**: Consider implementing additional caching or optimizing database queries.

5. **Memory Errors**: If deploying on a small instance, optimize your application's memory usage or upgrade your server.

For additional help, consult the SmartCareer development team or create an issue on GitHub. 