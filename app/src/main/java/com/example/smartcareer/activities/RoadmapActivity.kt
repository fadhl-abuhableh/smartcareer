package com.example.smartcareer.activities

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.utils.SessionManager
import com.example.smartcareer.utils.UserDataManager
import com.google.android.material.card.MaterialCardView
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class RoadmapActivity : AppCompatActivity(), UserDataManager.UserDataCallback {

    private lateinit var jobContainer: LinearLayout
    private lateinit var progressBar: ProgressBar
    private var email: String? = null
    private lateinit var sessionManager: SessionManager
    private lateinit var userDataManager: UserDataManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.roadmap)

        // Initialize SessionManager
        sessionManager = SessionManager(this)
        userDataManager = UserDataManager(this)
        
        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("RoadmapActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("RoadmapActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("RoadmapActivity", "Email saved to SessionManager: $email")
        }

        jobContainer = findViewById(R.id.jobContainer)
        progressBar = findViewById(R.id.progressBar)
        
        progressBar.visibility = View.VISIBLE
        
        // Fetch user data first, then get AI roadmap
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
        Log.d("RoadmapActivity", "User data loaded: Internships: $internshipTitles, Skills: $skills")
        fetchRoadmap(skills, determineCareerGoal(internshipTitles, skills))
    }

    override fun onError(message: String) {
        progressBar.visibility = View.GONE
        Toast.makeText(this, "Error loading user data: $message", Toast.LENGTH_SHORT).show()
        // Load with default data as fallback
        fetchRoadmap("Kotlin, Android, Java", "Mobile App Developer")
    }

    private fun fetchRoadmap(skills: String, goal: String) {
        val apiService = ApiClient.getClient().create(ApiService::class.java)

        val requestData = mapOf(
            "email" to (email ?: ""),
            "skills" to skills,
            "goals" to goal
        )
        
        Log.d("RoadmapActivity", "Requesting AI roadmap with data: $requestData")

        val call = apiService.getDetailedRoadmap(requestData)

        call.enqueue(object : Callback<List<Map<String, String>>> {
            override fun onResponse(
                call: Call<List<Map<String, String>>>,
                response: Response<List<Map<String, String>>>
            ) {
                progressBar.visibility = View.GONE
                
                if (response.isSuccessful && response.body() != null) {
                    val jobs = response.body()!!
                    if (jobs.isNotEmpty()) {
                        displayJobs(jobs)
                    } else {
                        // If API returns empty list, use fallback
                        displayFallbackRoadmap(skills, goal)
                    }
                } else {
                    Log.e("RoadmapActivity", "API error: ${response.code()}")
                    displayFallbackRoadmap(skills, goal)
                    Toast.makeText(this@RoadmapActivity, "Couldn't load live roadmap. Showing sample roadmap.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<Map<String, String>>>, t: Throwable) {
                progressBar.visibility = View.GONE
                Log.e("RoadmapActivity", "API error: ${t.message}")
                displayFallbackRoadmap(skills, goal)
                Toast.makeText(this@RoadmapActivity, "Error: Showing sample roadmap", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun displayJobs(jobs: List<Map<String, String>>) {
        jobContainer.removeAllViews()
        val inflater = LayoutInflater.from(this)

        for (job in jobs) {
            val cardView = inflater.inflate(R.layout.job_detail_item, jobContainer, false) as MaterialCardView
            val tvTitle = cardView.findViewById<TextView>(R.id.tvJobTitle)
            val tvDescription = cardView.findViewById<TextView>(R.id.tvJobDescription)

            tvTitle.text = job["title"]
            tvDescription.text = job["description"]

            jobContainer.addView(cardView)
        }
    }
    
    private fun displayFallbackRoadmap(skills: String, goal: String) {
        jobContainer.removeAllViews()
        
        // Create fallback roadmap based on skills and goal
        val roadmapItems = when {
            goal.contains("mobile", ignoreCase = true) || 
            skills.contains("android", ignoreCase = true) -> createMobileRoadmap()
            
            goal.contains("web", ignoreCase = true) || 
            skills.contains("javascript", ignoreCase = true) -> createWebRoadmap()
            
            goal.contains("data", ignoreCase = true) || 
            skills.contains("python", ignoreCase = true) -> createDataRoadmap()
            
            else -> createDefaultRoadmap()
        }
        
        // Display the fallback roadmap
        val inflater = LayoutInflater.from(this)
        for (item in roadmapItems) {
            val cardView = inflater.inflate(R.layout.job_detail_item, jobContainer, false) as MaterialCardView
            val tvTitle = cardView.findViewById<TextView>(R.id.tvJobTitle)
            val tvDescription = cardView.findViewById<TextView>(R.id.tvJobDescription)

            tvTitle.text = item.first
            tvDescription.text = item.second

            jobContainer.addView(cardView)
        }
    }
    
    private fun determineCareerGoal(internships: String, skills: String): String {
        return when {
            internships.contains("mobile", ignoreCase = true) || 
            internships.contains("android", ignoreCase = true) || 
            skills.contains("android", ignoreCase = true) -> "Mobile App Developer"
            
            skills.contains("web", ignoreCase = true) || 
            skills.contains("javascript", ignoreCase = true) || 
            skills.contains("frontend", ignoreCase = true) -> "Web Developer"
            
            skills.contains("data", ignoreCase = true) || 
            skills.contains("ai", ignoreCase = true) || 
            skills.contains("machine learning", ignoreCase = true) -> "Data Scientist"
            
            else -> "Software Engineer"
        }
    }
    
    private fun createMobileRoadmap(): List<Pair<String, String>> {
        return listOf(
            Pair("Junior Mobile Developer", 
                "Focus on mastering fundamental Android development with Kotlin, XML layouts, and basic UI components. Build small personal projects to demonstrate your skills. Learn about MVVM, Activity/Fragment lifecycle, and RecyclerView."),
            
            Pair("Mid-Level Mobile Developer",
                "Expand your knowledge to include Jetpack components, advanced UI with Compose, concurrency with Coroutines, and dependency injection. Work on apps with complex features like offline caching, multimedia, and location services."),
            
            Pair("Senior Mobile Developer",
                "Master system architecture, performance optimization, and CI/CD for mobile apps. Contribute to open-source projects, mentor junior developers, and lead feature teams. Develop expertise in cross-platform development or app security."),
            
            Pair("Mobile Lead / Architect",
                "Define technical direction for mobile applications, create coding standards, and lead architecture decisions. Mentor teams, collaborate with product managers, and ensure code quality through code reviews and technical specifications.")
        )
    }
    
    private fun createWebRoadmap(): List<Pair<String, String>> {
        return listOf(
            Pair("Junior Web Developer", 
                "Focus on HTML, CSS, JavaScript fundamentals and popular frameworks like React or Vue. Build responsive UIs, work with APIs, and understand browser compatibility issues. Create small projects that showcase your ability."),
            
            Pair("Mid-Level Web Developer",
                "Develop expertise in state management, advanced component patterns, and performance optimization. Learn backend technologies like Node.js or understand how to integrate with existing APIs. Master Git workflows and automated testing."),
            
            Pair("Senior Web Developer / Engineer",
                "Architect complex web applications, implement design systems, and lead feature development. Develop deep expertise in accessibility, internationalization, and web security. Mentor junior developers and influence technical decisions."),
            
            Pair("Lead Frontend Engineer / Web Architect",
                "Define frontend architecture, establish best practices, and lead development teams. Work closely with design, product, and backend teams to create seamless user experiences. Make high-level technical decisions and mentor team members.")
        )
    }
    
    private fun createDataRoadmap(): List<Pair<String, String>> {
        return listOf(
            Pair("Junior Data Analyst", 
                "Learn data manipulation with Python (Pandas), SQL basics, and data visualization. Work on exploratory data analysis tasks, create simple dashboards, and understand basic statistical concepts. Build a portfolio of data projects."),
            
            Pair("Data Scientist / ML Engineer",
                "Master advanced statistics, machine learning algorithms, and deep learning frameworks. Work on end-to-end ML projects from data collection to deployment. Develop expertise in a specific domain like NLP, computer vision, or recommendation systems."),
            
            Pair("Senior Data Scientist",
                "Lead complex data science projects, design ML systems, and work on model optimization. Collaborate with product and engineering teams to integrate ML solutions. Develop expertise in advanced topics like reinforcement learning or AI ethics."),
            
            Pair("Lead Data Scientist / ML Architect",
                "Architect machine learning systems, develop ML strategies, and lead data science teams. Define technical roadmaps, establish best practices, and mentor team members. Work closely with leadership to align data science initiatives with business goals.")
        )
    }
    
    private fun createDefaultRoadmap(): List<Pair<String, String>> {
        return listOf(
            Pair("Junior Software Engineer", 
                "Focus on mastering programming fundamentals, version control, and basic software development processes. Work on small features under guidance and learn from code reviews. Build a portfolio of projects showcasing your skills."),
            
            Pair("Mid-Level Software Engineer",
                "Take ownership of medium-sized features and components. Develop expertise in software design patterns, automated testing, and DevOps practices. Mentor junior developers and contribute to technical discussions."),
            
            Pair("Senior Software Engineer",
                "Lead the development of complex features and systems. Make architectural decisions, perform code reviews, and mentor other engineers. Develop deep expertise in system design, performance optimization, and engineering best practices."),
            
            Pair("Tech Lead / Software Architect",
                "Define technical vision, architect complex systems, and lead engineering teams. Balance technical excellence with business requirements. Mentor engineers, establish best practices, and collaborate with product and leadership teams.")
        )
    }
}
