package com.example.smartcareer.utils

import android.content.Context
import android.util.Log
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

/**
 * UserDataManager collects and aggregates user data from different sources (internships, milestones)
 * to provide comprehensive information for AI-powered features
 */
class UserDataManager(private val context: Context) {
    
    private val apiService: ApiService = ApiClient.getClient().create(ApiService::class.java)
    private val sessionManager = SessionManager(context)
    
    private var userInternships: List<Map<String, String>> = emptyList()
    private var userMilestones: List<Map<String, String>> = emptyList()
    
    // Callback for when user data is ready
    interface UserDataCallback {
        fun onDataReady(
            internshipTitles: String,
            skills: String,
            milestones: String,
            completionPercent: Int
        )
        fun onError(message: String)
    }
    
    /**
     * Fetch all user data asynchronously
     */
    fun fetchAllUserData(email: String, callback: UserDataCallback) {
        // Load internships and milestones in parallel
        var internshipsLoaded = false
        var milestonesLoaded = false
        
        // Load internships
        val internshipsCall = apiService.getUserInternships(email)
        internshipsCall.enqueue(object : Callback<List<Map<String, String>>> {
            override fun onResponse(call: Call<List<Map<String, String>>>, response: Response<List<Map<String, String>>>) {
                if (response.isSuccessful) {
                    val internships = response.body()
                    if (internships != null) {
                        userInternships = internships
                        Log.d("UserDataManager", "Loaded ${internships.size} internships")
                    }
                } else {
                    Log.e("UserDataManager", "Failed to load internships: ${response.code()}")
                }
                
                internshipsLoaded = true
                if (milestonesLoaded) processData(callback)
            }
            
            override fun onFailure(call: Call<List<Map<String, String>>>, t: Throwable) {
                Log.e("UserDataManager", "Error loading internships: ${t.message}")
                internshipsLoaded = true
                if (milestonesLoaded) processData(callback)
            }
        })
        
        // Load milestones
        val milestonesCall = apiService.getUserMilestones(email)
        milestonesCall.enqueue(object : Callback<List<Map<String, String>>> {
            override fun onResponse(call: Call<List<Map<String, String>>>, response: Response<List<Map<String, String>>>) {
                if (response.isSuccessful) {
                    val milestones = response.body()
                    if (milestones != null) {
                        userMilestones = milestones
                        Log.d("UserDataManager", "Loaded ${milestones.size} milestones")
                    }
                } else {
                    Log.e("UserDataManager", "Failed to load milestones: ${response.code()}")
                }
                
                milestonesLoaded = true
                if (internshipsLoaded) processData(callback)
            }
            
            override fun onFailure(call: Call<List<Map<String, String>>>, t: Throwable) {
                Log.e("UserDataManager", "Error loading milestones: ${t.message}")
                milestonesLoaded = true
                if (internshipsLoaded) processData(callback)
            }
        })
    }
    
    /**
     * Process and extract relevant data for AI insights
     */
    private fun processData(callback: UserDataCallback) {
        try {
            // Extract internship companies and roles
            val internshipTitles = userInternships.mapNotNull { 
                val company = it["company"] ?: return@mapNotNull null
                val role = it["role"] ?: return@mapNotNull null
                "$role at $company"
            }.joinToString(", ")
            
            // Extract milestone titles
            val milestones = userMilestones.mapNotNull { 
                it["title"] 
            }.joinToString(", ")
            
            // Extract potential skills from internships and milestones
            val skills = extractSkills()
            
            // Calculate profile completion percentage
            val completionPercent = calculateCompletionPercentage()
            
            // Return data through callback
            callback.onDataReady(
                internshipTitles,
                skills,
                milestones,
                completionPercent
            )
            
        } catch (e: Exception) {
            Log.e("UserDataManager", "Error processing user data: ${e.message}")
            callback.onError("Error processing your data: ${e.message}")
        }
    }
    
    /**
     * Extract skills from internships and milestones
     */
    private fun extractSkills(): String {
        val skillsSet = mutableSetOf<String>()
        
        // Try to extract skills from internship descriptions
        userInternships.forEach { internship ->
            internship["description"]?.let { description ->
                // Common tech skills to look for in descriptions
                val techKeywords = listOf(
                    "Java", "Kotlin", "Android", "iOS", "Swift", "Python", "JavaScript", 
                    "TypeScript", "React", "Angular", "Vue", "Node.js", "AWS", "Azure", 
                    "GCP", "Cloud", "DevOps", "CI/CD", "Git", "Docker", "Kubernetes", 
                    "Machine Learning", "AI", "Deep Learning", "SQL", "NoSQL", "MongoDB", 
                    "Firebase", "REST API", "GraphQL", "Agile", "Scrum"
                )
                
                techKeywords.forEach { keyword ->
                    if (description.contains(keyword, ignoreCase = true)) {
                        skillsSet.add(keyword)
                    }
                }
            }
        }
        
        // If no skills found from descriptions, use default skills
        if (skillsSet.isEmpty()) {
            skillsSet.addAll(listOf("Android", "Kotlin", "Mobile Development", "UI/UX"))
        }
        
        return skillsSet.joinToString(", ")
    }
    
    /**
     * Calculate profile completion percentage
     */
    private fun calculateCompletionPercentage(): Int {
        var total = 0
        var completed = 0
        
        // Check for internships
        total += 30
        if (userInternships.isNotEmpty()) {
            completed += 30
        }
        
        // Check for milestones
        total += 30
        if (userMilestones.isNotEmpty()) {
            completed += 30
        }
        
        // Basic profile is always there
        total += 40
        completed += 40
        
        return (completed * 100) / total
    }
} 