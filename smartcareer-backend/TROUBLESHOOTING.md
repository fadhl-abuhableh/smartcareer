# SmartCareer Android App Troubleshooting Guide

## Profile Page Crash Issue

If the app crashes when accessing the profile page, follow these troubleshooting steps:

### 1. Check Backend Logs

First, check your backend logs for errors related to the profile API endpoints. Look for:
- 401 Unauthorized errors
- 500 Server errors
- Missing or malformed response data

### 2. Test the Debug API Endpoint

We've added a special debug endpoint to help isolate backend vs. frontend issues:

```
GET /api/debug-profile?email=user@example.com
```

Try accessing this endpoint from a web browser or tool like Postman. This endpoint returns a valid profile without hitting the database, which helps determine if the issue is with:
- Database access
- JSON serialization
- Network connectivity

### 3. Common Issues & Solutions

#### Backend Issues:

1. **Missing User Profile Record**
   - Problem: User has an account but no profile record
   - Solution: Manually create a profile record or use the update endpoint

2. **Password Authentication Issues**
   - Problem: Password hashing implementation causing login failures
   - Solution: Run the `migrate_passwords.py` script to update all passwords

3. **Database Connection Problems**
   - Problem: Database connection errors
   - Solution: Check database credentials and make sure the server is running

#### Android App Issues:

1. **JSON Parsing Errors**
   - Problem: App expecting different field names or structure
   - Solution: Make sure the app's data models match the API response format

2. **Null Object References**
   - Problem: App not handling null values properly
   - Solution: Add null checks for all profile fields in the app code

3. **Image Loading Errors**
   - Problem: Profile image URL is invalid or inaccessible
   - Solution: Check image URL format and that images are being stored correctly

### 4. Testing Solutions

1. **Test with a Clean Profile**
   - Create a new test user with a minimal profile
   - Try accessing the profile page with this test user

2. **Simplified API Test**
   - Use the `/api/debug-profile` endpoint to test with dummy data
   - If this works, the issue is likely with database data

3. **Step-by-Step Authentication**
   - Test login first, make sure it succeeds
   - Test profile retrieval as a separate step
   - Test profile update as a separate step

### 5. Specific Error Codes

- **401 Unauthorized**: Authentication issue, check login flow
- **404 Not Found**: User or profile doesn't exist
- **400 Bad Request**: Missing or invalid parameters
- **500 Server Error**: Server-side error, check backend logs

### Contact Support

If you continue to experience issues after trying these steps, please provide:
1. The exact steps that lead to the crash
2. The backend logs showing the API requests
3. The Android logcat output showing the crash stack trace 