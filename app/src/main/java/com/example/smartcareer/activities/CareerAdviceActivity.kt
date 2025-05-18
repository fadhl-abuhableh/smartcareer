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

class CareerAdviceActivity : AppCompatActivity(), UserDataManager.UserDataCallback {

    private lateinit var tvCert: TextView
    private lateinit var tvSkills: TextView
    private lateinit var tvTips: TextView
    private lateinit var progressBar: ProgressBar
    private var email: String? = null
    private lateinit var sessionManager: SessionManager
    private lateinit var userDataManager: UserDataManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.careeradvice)

        // Initialize SessionManager
        sessionManager = SessionManager(this)
        userDataManager = UserDataManager(this)
        
        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("CareerAdviceActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("CareerAdviceActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("CareerAdviceActivity", "Email saved to SessionManager: $email")
        }

        tvCert = findViewById(R.id.tvCertAdvice)
        tvSkills = findViewById(R.id.tvSkillAdvice)
        tvTips = findViewById(R.id.tvJobAdvice)
        progressBar = findViewById(R.id.progressBar)
        
        progressBar.visibility = View.VISIBLE
        
        // Fetch user data first, then get AI advice
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
        Log.d("CareerAdviceActivity", "User data loaded: Internships: $internshipTitles, Skills: $skills")
        fetchCareerAdvice(internshipTitles, skills, milestones)
    }

    override fun onError(message: String) {
        progressBar.visibility = View.GONE
        Toast.makeText(this, "Error loading user data: $message", Toast.LENGTH_SHORT).show()
        // Load with default data as fallback
        fetchCareerAdvice("Software Development Intern", "Kotlin, Android, Java", "App Development Project")
    }

    private fun fetchCareerAdvice(internships: String, skills: String, goals: String) {
        val apiService = ApiClient.getClient().create(ApiService::class.java)

        val requestData = mapOf(
            "email" to (email ?: ""),
            "internships" to internships,
            "skills" to skills,
            "goals" to goals
        )

        Log.d("CareerAdviceActivity", "Requesting AI advice with data: $requestData")
        
        val call = apiService.getCareerAdvice(requestData)

        call.enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                progressBar.visibility = View.GONE
                
                if (response.isSuccessful && response.body() != null) {
                    val body = response.body()!!
                    tvCert.text = body["certifications"] ?: getSuggestedCertifications(skills)
                    tvSkills.text = body["skills"] ?: getSuggestedSkills(skills)
                    tvTips.text = body["tips"] ?: getCareerTips(internships)
                } else {
                    // Fallback content if API fails
                    provideFallbackContent(skills)
                    Toast.makeText(this@CareerAdviceActivity, "Couldn't load live advice. Showing sample advice.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                progressBar.visibility = View.GONE
                Log.e("CareerAdviceActivity", "API error: ${t.message}")
                // Fallback content if API fails
                provideFallbackContent(skills)
                Toast.makeText(this@CareerAdviceActivity, "Error: Showing sample advice", Toast.LENGTH_SHORT).show()
            }
        })
    }
    
    private fun provideFallbackContent(skills: String) {
        tvCert.text = getSuggestedCertifications(skills)
        tvSkills.text = getSuggestedSkills(skills)
        tvTips.text = "• Create a portfolio that showcases your projects\n" +
                      "• Network with professionals in your field\n" +
                      "• Contribute to open-source projects\n" +
                      "• Stay updated with industry trends\n" +
                      "• Practice technical and behavioral interview skills"
    }
    
    private fun getSuggestedCertifications(skills: String): String {
        return when {
            skills.contains("android", ignoreCase = true) -> 
                "• Google Associate Android Developer\n" +
                "• Android Certified Application Developer\n" +
                "• Kotlin Certified Developer\n" +
                "• Mobile App Security Certification"
            
            skills.contains("cloud", ignoreCase = true) || 
            skills.contains("aws", ignoreCase = true) || 
            skills.contains("azure", ignoreCase = true) -> 
                "• AWS Certified Solutions Architect\n" +
                "• Google Cloud Professional Cloud Architect\n" +
                "• Microsoft Azure Fundamentals\n" +
                "• CompTIA Cloud+"
                
            skills.contains("python", ignoreCase = true) || 
            skills.contains("ML", ignoreCase = true) || 
            skills.contains("AI", ignoreCase = true) ->
                "• TensorFlow Developer Certificate\n" +
                "• AWS Certified Machine Learning\n" +
                "• Microsoft Certified: Azure AI Engineer\n" +
                "• IBM AI Engineering Professional Certificate"
                
            else -> 
                "• CompTIA A+ Certification\n" +
                "• Microsoft Certified: Azure Fundamentals\n" +
                "• Certified Associate in Project Management\n" +
                "• Google IT Support Professional Certificate"
        }
    }
    
    private fun getSuggestedSkills(currentSkills: String): String {
        return when {
            currentSkills.contains("android", ignoreCase = true) -> 
                "• Jetpack Compose for modern UI\n" +
                "• Kotlin Coroutines and Flow\n" +
                "• CI/CD for mobile apps\n" +
                "• Firebase for backend services\n" +
                "• Mobile app security practices"
            
            currentSkills.contains("cloud", ignoreCase = true) -> 
                "• Containerization (Docker, Kubernetes)\n" +
                "• Infrastructure as Code (Terraform)\n" +
                "• Serverless architecture\n" +
                "• Cloud security best practices\n" +
                "• Multi-cloud strategies"
                
            currentSkills.contains("python", ignoreCase = true) -> 
                "• Data structures and algorithms\n" +
                "• Machine learning frameworks (TensorFlow, PyTorch)\n" +
                "• Data visualization\n" +
                "• API development with FastAPI\n" +
                "• Backend development with Django/Flask"
                
            else -> 
                "• Full-stack development fundamentals\n" +
                "• Version control (Git)\n" +
                "• Communication and collaboration\n" +
                "• Problem-solving and debugging\n" +
                "• Basic DevOps understanding"
        }
    }
    
    private fun getCareerTips(internships: String): String {
        return "• Create a portfolio that showcases your projects\n" +
               "• Network with professionals in your field\n" +
               "• Contribute to open-source projects\n" +
               "• Stay updated with industry trends\n" +
               "• Practice technical and behavioral interview skills"
    }
}
