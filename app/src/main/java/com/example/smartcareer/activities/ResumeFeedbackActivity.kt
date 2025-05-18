package com.example.smartcareer.activities

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import com.example.smartcareer.utils.SessionManager
import com.example.smartcareer.utils.UserDataManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ResumeFeedbackActivity : AppCompatActivity(), UserDataManager.UserDataCallback {

    private lateinit var tvGeneral: TextView
    private lateinit var tvStrengths: TextView
    private lateinit var tvImprovements: TextView
    private lateinit var progressBar: ProgressBar
    private var email: String? = null
    private lateinit var sessionManager: SessionManager
    private lateinit var userDataManager: UserDataManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.resumefeedback)

        // Initialize SessionManager
        sessionManager = SessionManager(this)
        userDataManager = UserDataManager(this)
        
        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("ResumeFeedbackActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("ResumeFeedbackActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("ResumeFeedbackActivity", "Email saved to SessionManager: $email")
        }

        tvGeneral = findViewById(R.id.tvGeneral)
        tvStrengths = findViewById(R.id.tvStrengths)
        tvImprovements = findViewById(R.id.tvImprovements)
        progressBar = findViewById(R.id.progressBar)
        
        progressBar.visibility = View.VISIBLE
        
        // Fetch user data first, then get AI feedback
        if (!email.isNullOrEmpty()) {
            userDataManager.fetchAllUserData(email!!, this)
        } else {
            Toast.makeText(this, "Unable to identify user. Please login again.", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    override fun onDataReady(
        internshipTitles: String,
        skills: String,
        milestones: String,
        completionPercent: Int
    ) {
        Log.d("ResumeFeedbackActivity", "User data loaded: Internships: $internshipTitles, Skills: $skills")
        fetchAIFeedback(internshipTitles, skills, milestones)
    }

    override fun onError(message: String) {
        progressBar.visibility = View.GONE
        Toast.makeText(this, "Error loading user data: $message", Toast.LENGTH_SHORT).show()
        // Load with default data as fallback
        fetchAIFeedback("Software Engineering Intern at Tech Corp", 
                        "Kotlin, Android, Java", 
                        "App Development Project")
    }

    private fun fetchAIFeedback(internships: String, skills: String, milestones: String) {
        val apiService = ApiClient.getClient().create(ApiService::class.java)

        val requestData = mapOf(
            "email" to (email ?: ""),
            "internships" to internships,
            "skills" to skills,
            "milestones" to milestones
        )
        
        Log.d("ResumeFeedbackActivity", "Requesting AI feedback with data: $requestData")

        val call = apiService.getResumeFeedback(requestData)

        call.enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                progressBar.visibility = View.GONE
                
                if (response.isSuccessful && response.body() != null) {
                    val body = response.body()!!
                    tvGeneral.text = body["general"] ?: "Your resume shows a good start in your career journey."
                    tvStrengths.text = body["strengths"] ?: "Experience with $skills is valuable in the current market."
                    tvImprovements.text = body["improvements"] ?: "Consider adding more quantifiable achievements to your internships."
                } else {
                    // Fallback content if API fails
                    provideFallbackContent(skills, internships)
                    Toast.makeText(this@ResumeFeedbackActivity, "Couldn't load live feedback. Showing sample feedback.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                progressBar.visibility = View.GONE
                Log.e("ResumeFeedbackActivity", "API error: ${t.message}")
                // Fallback content if API fails
                provideFallbackContent(skills, internships)
                Toast.makeText(this@ResumeFeedbackActivity, "Error: Showing sample feedback", Toast.LENGTH_SHORT).show()
            }
        })
    }
    
    private fun provideFallbackContent(skills: String, internships: String) {
        tvGeneral.text = "Your resume is starting to take shape nicely. You have some relevant experience that can be highlighted better."
        
        tvStrengths.text = "• Your experience with $skills is highly relevant in today's job market\n" +
                          "• Your internship as $internships gives you practical industry exposure\n" +
                          "• You've shown initiative through your projects and milestones"
                          
        tvImprovements.text = "• Add more quantifiable achievements to your internship descriptions\n" +
                             "• Consider expanding your skills section with more specific technologies\n" +
                             "• Add a professional summary at the top of your resume\n" +
                             "• Make sure each experience has 3-5 bullet points with action verbs"
    }
}
