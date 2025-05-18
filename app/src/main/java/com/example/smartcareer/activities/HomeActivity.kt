package com.example.smartcareer.activities

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import com.example.smartcareer.utils.SessionManager
import com.example.smartcareer.utils.UserDataManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import android.widget.ImageButton

class HomeActivity : AppCompatActivity(), UserDataManager.UserDataCallback {

    private var email: String? = null
    private lateinit var sessionManager: SessionManager
    private lateinit var userDataManager: UserDataManager
    
    // UI elements
    private lateinit var tvWelcome: TextView
    private lateinit var tvMilestoneCount: TextView
    private lateinit var tvInternshipCount: TextView
    private lateinit var tvRoadmapPreview: TextView
    private lateinit var tvAdvicePreview: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.homepage)
        
        // Initialize SessionManager and UserDataManager
        sessionManager = SessionManager(this)
        userDataManager = UserDataManager(this)
        
        // Initialize UI elements
        tvWelcome = findViewById(R.id.tvWelcome)
        tvMilestoneCount = findViewById(R.id.tvMilestoneCount)
        tvInternshipCount = findViewById(R.id.tvInternshipCount)
        tvRoadmapPreview = findViewById(R.id.tvRoadmapPreview)
        tvAdvicePreview = findViewById(R.id.tvAdvicePreview)
        
        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("HomeActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("HomeActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("HomeActivity", "Email saved to SessionManager: $email")
        }
        
        // Set welcome message
        tvWelcome.text = "Welcome back${getUserFirstName()}!"
        
        // Load user data
        if (!email.isNullOrEmpty()) {
            loadUserData()
        } else {
            // Set default values if no email
            setDefaultValues()
            Log.e("HomeActivity", "No email available")
        }

        // Set up button click listeners
        findViewById<Button>(R.id.btnMilestones).setOnClickListener {
            val intent = Intent(this, MilestoneActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnInternships).setOnClickListener {
            val intent = Intent(this, InternshipActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnRoadmap).setOnClickListener {
            val intent = Intent(this, RoadmapActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnResume).setOnClickListener {
            val intent = Intent(this, ResumeFeedbackActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnAdvice).setOnClickListener {
            val intent = Intent(this, CareerAdviceActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        // Set up bottom navigation
        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        val btnProfile = findViewById<ImageButton>(R.id.btnProfile)

        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.menu_home -> {
                    // Already on home
                    true
                }
                R.id.menu_internships -> {
                    startActivity(Intent(this, InternshipActivity::class.java))
                    true
                }
                R.id.menu_milestones -> {
                    startActivity(Intent(this, MilestoneActivity::class.java))
                    true
                }
                R.id.menu_insights -> {
                    startActivity(Intent(this, InsightsActivity::class.java))
                    true
                }
                else -> false
            }
        }

        // Set up profile button
        btnProfile.setOnClickListener {
            val intent = Intent(this, ProfileActivity::class.java)
            startActivity(intent)
        }
    }
    
    private fun loadUserData() {
        // Use UserDataManager to fetch data
        userDataManager.fetchAllUserData(email!!, this)
        
        // Load milestone and internship counts
        loadMilestoneCount()
        loadInternshipCount()
    }
    
    private fun loadMilestoneCount() {
        val apiService = ApiClient.getClient().create(ApiService::class.java)
        val call = apiService.getUserMilestones(email!!)
        
        call.enqueue(object : Callback<List<Map<String, String>>> {
            override fun onResponse(call: Call<List<Map<String, String>>>, response: Response<List<Map<String, String>>>) {
                if (response.isSuccessful && response.body() != null) {
                    val milestones = response.body()!!
                    tvMilestoneCount.text = milestones.size.toString()
                    Log.d("HomeActivity", "Loaded ${milestones.size} milestones")
                } else {
                    tvMilestoneCount.text = "0"
                    Log.e("HomeActivity", "Failed to load milestones: ${response.code()}")
                }
            }
            
            override fun onFailure(call: Call<List<Map<String, String>>>, t: Throwable) {
                tvMilestoneCount.text = "0"
                Log.e("HomeActivity", "Error loading milestones: ${t.message}")
            }
        })
    }
    
    private fun loadInternshipCount() {
        val apiService = ApiClient.getClient().create(ApiService::class.java)
        val call = apiService.getUserInternships(email!!)
        
        call.enqueue(object : Callback<List<Map<String, String>>> {
            override fun onResponse(call: Call<List<Map<String, String>>>, response: Response<List<Map<String, String>>>) {
                if (response.isSuccessful && response.body() != null) {
                    val internships = response.body()!!
                    tvInternshipCount.text = internships.size.toString()
                    Log.d("HomeActivity", "Loaded ${internships.size} internships")
                } else {
                    tvInternshipCount.text = "0"
                    Log.e("HomeActivity", "Failed to load internships: ${response.code()}")
                }
            }
            
            override fun onFailure(call: Call<List<Map<String, String>>>, t: Throwable) {
                tvInternshipCount.text = "0"
                Log.e("HomeActivity", "Error loading internships: ${t.message}")
            }
        })
    }
    
    private fun getUserFirstName(): String {
        val email = sessionManager.getEmail()
        return if (!email.isNullOrEmpty()) {
            val namePart = email.split("@").firstOrNull() ?: ""
            if (namePart.isNotEmpty()) {
                val name = namePart.split(".").firstOrNull() ?: namePart
                " ${name.replaceFirstChar { it.uppercase() }}"
            } else {
                ""
            }
        } else {
            ""
        }
    }
    
    private fun setDefaultValues() {
        tvMilestoneCount.text = "0"
        tvInternshipCount.text = "0"
        tvRoadmapPreview.text = "Add your experience details to get personalized career path recommendations."
        tvAdvicePreview.text = "Complete your profile to receive tailored skill recommendations and career advice."
    }
    
    // UserDataManager Callback
    override fun onDataReady(
        internshipTitles: String,
        skills: String,
        milestones: String,
        completionPercent: Int
    ) {
        // Set career insights based on user data
        if (skills.isNotEmpty()) {
            val roadmapText = generateRoadmapPreview(skills, internshipTitles)
            tvRoadmapPreview.text = roadmapText
            
            val adviceText = generateAdvicePreview(skills)
            tvAdvicePreview.text = adviceText
        }
    }
    
    override fun onError(message: String) {
        Log.e("HomeActivity", "Error loading user data: $message")
        setDefaultValues()
    }
    
    private fun generateRoadmapPreview(skills: String, internships: String): String {
        val skillList = skills.split(",").map { it.trim().lowercase() }
        
        return when {
            skillList.any { it.contains("android") || it.contains("kotlin") } -> 
                "Based on your mobile development skills, your career path may include Junior Android Developer → Senior Developer → Lead Developer roles."
                
            skillList.any { it.contains("web") || it.contains("javascript") || it.contains("react") } -> 
                "With your web development experience, consider a path from Frontend Developer → Full-Stack → Engineering Manager."
                
            skillList.any { it.contains("data") || it.contains("python") || it.contains("ml") } -> 
                "Your data-related skills suggest a path from Data Analyst → Data Scientist → AI/ML Specialist."
                
            else -> "Based on your ${skillList.firstOrNull() ?: "technical"} skills, a progressive path with increasing responsibilities is recommended."
        }
    }
    
    private fun generateAdvicePreview(skills: String): String {
        val skillList = skills.split(",").map { it.trim().lowercase() }
        
        return when {
            skillList.any { it.contains("android") || it.contains("kotlin") } -> 
                "Consider enhancing your Android skills with Jetpack Compose, Kotlin Coroutines, and architecture patterns like MVVM."
                
            skillList.any { it.contains("web") || it.contains("javascript") || it.contains("react") } -> 
                "For web development growth, focus on modern frameworks like React, TypeScript, and state management libraries."
                
            skillList.any { it.contains("data") || it.contains("python") || it.contains("ml") } -> 
                "To advance in data science, build skills in machine learning frameworks, data visualization, and cloud ML services."
                
            else -> "Consider expanding your technical portfolio with cloud services, DevOps practices, and software architecture knowledge."
        }
    }
    
    // Simple profile dialog as fallback if ProfileActivity fails
    private fun showSimpleProfileDialog() {
        try {
            val email = sessionManager.getEmail() ?: "Not logged in"
            val dialogBuilder = androidx.appcompat.app.AlertDialog.Builder(this)
            dialogBuilder.setTitle("Your Profile")
            dialogBuilder.setMessage("Email: $email\n\nProfile viewing is experiencing technical difficulties. Full profile editing will be available soon.")
            dialogBuilder.setPositiveButton("OK", null)
            dialogBuilder.show()
            
            // Log this fallback for debugging
            Log.d("HomeActivity", "Showed simple profile dialog as fallback")
        } catch (e: Exception) {
            Log.e("HomeActivity", "Error showing fallback dialog: ${e.message}")
            Toast.makeText(this, "Profile temporarily unavailable", Toast.LENGTH_SHORT).show()
        }
    }
}
