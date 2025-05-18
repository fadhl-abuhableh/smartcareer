package com.example.smartcareer.activities

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import com.example.smartcareer.utils.SessionManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MilestoneActivity : AppCompatActivity() {

    private lateinit var milestoneContainer: LinearLayout
    private lateinit var btnAddMilestone: Button
    private var email: String? = null
    private lateinit var sessionManager: SessionManager
    private lateinit var apiService: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.milesonestracker)

        // Initialize SessionManager
        sessionManager = SessionManager(this)
        
        // Initialize API service
        apiService = ApiClient.getClient().create(ApiService::class.java)

        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("MilestoneActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("MilestoneActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("MilestoneActivity", "Email saved to SessionManager: $email")
        }

        milestoneContainer = findViewById(R.id.milestoneContainer)
        btnAddMilestone = findViewById(R.id.btnAddMilestone)

        btnAddMilestone.setOnClickListener {
            val intent = Intent(this, AddMilestoneActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        // Load milestones from API
        loadMilestones()

        val navView = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        navView.selectedItemId = R.id.menu_milestones
        navView.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.menu_home -> {
                    val intent = Intent(this, HomeActivity::class.java)
                    intent.putExtra("email", email)
                    startActivity(intent)
                    true
                }
                R.id.menu_internships -> {
                    val intent = Intent(this, InternshipActivity::class.java)
                    intent.putExtra("email", email)
                    startActivity(intent)
                    true
                }
                R.id.menu_insights -> {
                    val intent = Intent(this, InsightsActivity::class.java)
                    intent.putExtra("email", email)
                    startActivity(intent)
                    true
                }
                else -> false
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        // Refresh milestones when returning to this activity
        loadMilestones()
    }
    
    private fun loadMilestones() {
        Log.d("MilestoneActivity", "Loading milestones for email: $email")
        if (email.isNullOrEmpty()) {
            Toast.makeText(this, "Email not found", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Clear existing milestones
        milestoneContainer.removeAllViews()
        
        // Call the API to get user milestones
        val call = apiService.getUserMilestones(email!!)
        call.enqueue(object : Callback<List<Map<String, String>>> {
            override fun onResponse(call: Call<List<Map<String, String>>>, response: Response<List<Map<String, String>>>) {
                if (response.isSuccessful) {
                    val milestones = response.body()
                    if (milestones != null && milestones.isNotEmpty()) {
                        // Clear container again just to be sure
                        milestoneContainer.removeAllViews()
                        
                        for (milestoneData in milestones) {
                            val title = milestoneData["title"] ?: ""
                            val date = milestoneData["date"] ?: ""
                            val description = milestoneData["description"] ?: ""
                            val filename = milestoneData["filename"]
                            val id = milestoneData["id"]
                            
                            Log.d("MilestoneActivity", "Adding milestone - Title: $title, Date: $date, Description: $description")
                            addMilestoneCard(title, date, description, filename, id)
                        }
                    } else {
                        // No milestones found, show message
                        Log.d("MilestoneActivity", "No milestones found for user")
                        addNoMilestonesMessage()
                    }
                } else {
                    Log.e("MilestoneActivity", "Failed to load milestones: ${response.code()}")
                    Toast.makeText(this@MilestoneActivity, "Failed to load milestones", Toast.LENGTH_SHORT).show()
                    // Add dummy data as fallback
                    addDummyMilestoneData()
                }
            }

            override fun onFailure(call: Call<List<Map<String, String>>>, t: Throwable) {
                Log.e("MilestoneActivity", "Error loading milestones: ${t.message}")
                Toast.makeText(this@MilestoneActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                // Add dummy data as fallback
                addDummyMilestoneData()
            }
        })
    }
    
    private fun addNoMilestonesMessage() {
        val inflater = LayoutInflater.from(this)
        val card = inflater.inflate(R.layout.milestone_card, milestoneContainer, false)
        
        card.findViewById<TextView>(R.id.tvMilestoneTitle).text = "No milestones found"
        card.findViewById<TextView>(R.id.tvMilestoneDate).text = "Add your first milestone"
        card.findViewById<TextView>(R.id.tvMilestoneDescription).text = ""
        
        milestoneContainer.addView(card)
    }

    private fun addDummyMilestoneData() {
        // Add dummy data when API fails
        addMilestoneCard("Smart Bin Project", "18/10/2024", "Created a smart bin that automatically sorts recyclable materials using computer vision.", null, null)
        addMilestoneCard("UX/UI Certificate", "06/05/2024", "Completed a comprehensive course on UX/UI design principles and best practices.", null, null)
    }

    private fun addMilestoneCard(title: String, date: String, description: String = "", filename: String? = null, id: String? = null) {
        val inflater = LayoutInflater.from(this)
        val card = inflater.inflate(R.layout.milestone_card, milestoneContainer, false)

        card.findViewById<TextView>(R.id.tvMilestoneTitle).text = title
        card.findViewById<TextView>(R.id.tvMilestoneDate).text = date
        card.findViewById<TextView>(R.id.tvMilestoneDescription).text = description

        // Configure View Attachment button
        val btnViewAttachment = card.findViewById<Button>(R.id.btnViewAttachment)
        if (filename.isNullOrEmpty()) {
            btnViewAttachment.isEnabled = false
            btnViewAttachment.alpha = 0.5f
        } else {
            btnViewAttachment.isEnabled = true
            btnViewAttachment.alpha = 1.0f
            btnViewAttachment.setOnClickListener {
                openAttachment(filename)
            }
        }

        // Configure Delete button
        val btnDelete = card.findViewById<Button>(R.id.btnDeleteMilestone)
        btnDelete.setOnClickListener {
            if (id != null) {
                deleteMilestone(id, card)
            } else {
                // For dummy data without ID, just remove from UI
                milestoneContainer.removeView(card)
                Toast.makeText(this, "Milestone deleted", Toast.LENGTH_SHORT).show()
            }
        }

        milestoneContainer.addView(card)
    }

    private fun openAttachment(filename: String) {
        // Build the URL to the attachment
        val baseUrl = ApiClient.getBaseUrl()
        val attachmentUrl = "$baseUrl/attachments/$filename"
        
        try {
            // Create a dialog to show the attachment in a WebView
            val dialog = android.app.Dialog(this, android.R.style.Theme_Material_Light_NoActionBar_Fullscreen)
            dialog.setContentView(R.layout.dialog_webview)
            
            val webView = dialog.findViewById<android.webkit.WebView>(R.id.webView)
            val progressBar = dialog.findViewById<android.widget.ProgressBar>(R.id.progressBar)
            val btnClose = dialog.findViewById<android.widget.ImageButton>(R.id.btnClose)
            
            // Configure WebView settings with safeguards
            try {
                webView.settings.apply {
                    javaScriptEnabled = true
                    loadWithOverviewMode = true
                    useWideViewPort = true
                    builtInZoomControls = true
                    displayZoomControls = false
                    // Add cache mode to prevent issues
                    cacheMode = android.webkit.WebSettings.LOAD_NO_CACHE
                    // Disable some features that might cause crashes
                    javaScriptCanOpenWindowsAutomatically = false
                    allowFileAccess = false
                    domStorageEnabled = true
                    // Set timeout to prevent hangs
                    setGeolocationEnabled(false)
                }
            } catch (e: Exception) {
                Log.e("MilestoneActivity", "Error configuring WebView: ${e.message}")
            }
            
            // Set WebViewClient to handle loading events with safeguards for cancellation
            webView.webViewClient = object : android.webkit.WebViewClient() {
                override fun onPageStarted(view: android.webkit.WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                    if (!isFinishing) {
                        try {
                            super.onPageStarted(view, url, favicon)
                            progressBar.visibility = android.view.View.VISIBLE
                        } catch (e: Exception) {
                            Log.e("MilestoneActivity", "Error in onPageStarted: ${e.message}")
                        }
                    }
                }
                
                override fun onPageFinished(view: android.webkit.WebView?, url: String?) {
                    if (!isFinishing) {
                        try {
                            super.onPageFinished(view, url)
                            progressBar.visibility = android.view.View.GONE
                        } catch (e: Exception) {
                            Log.e("MilestoneActivity", "Error in onPageFinished: ${e.message}")
                        }
                    }
                }
                
                override fun onReceivedError(view: android.webkit.WebView?, request: android.webkit.WebResourceRequest?, error: android.webkit.WebResourceError?) {
                    if (!isFinishing) {
                        try {
                            super.onReceivedError(view, request, error)
                            progressBar.visibility = android.view.View.GONE
                            Toast.makeText(this@MilestoneActivity, "Error loading attachment", Toast.LENGTH_SHORT).show()
                        } catch (e: Exception) {
                            Log.e("MilestoneActivity", "Error in onReceivedError: ${e.message}")
                        }
                    }
                }
                
                // Handle SSL errors
                override fun onReceivedSslError(view: android.webkit.WebView?, handler: android.webkit.SslErrorHandler?, error: android.net.http.SslError?) {
                    Toast.makeText(this@MilestoneActivity, "SSL Certificate Error", Toast.LENGTH_SHORT).show()
                    handler?.cancel()
                }
            }
            
            // Set chrome client to handle crashes
            webView.webChromeClient = object : android.webkit.WebChromeClient() {
                override fun onProgressChanged(view: android.webkit.WebView?, newProgress: Int) {
                    if (!isFinishing && progressBar != null) {
                        if (newProgress < 100) {
                            progressBar.visibility = android.view.View.VISIBLE
                        } else {
                            progressBar.visibility = android.view.View.GONE
                        }
                    }
                }
            }
            
            // Close button
            btnClose.setOnClickListener {
                try {
                    webView.stopLoading()
                    webView.clearCache(true)
                    dialog.dismiss()
                } catch (e: Exception) {
                    Log.e("MilestoneActivity", "Error closing dialog: ${e.message}")
                }
            }
            
            // Load the URL with a timeout and fallback
            webView.loadUrl(attachmentUrl)
            
            // Add a timeout handler
            android.os.Handler(mainLooper).postDelayed({
                if (progressBar.visibility == android.view.View.VISIBLE) {
                    progressBar.visibility = android.view.View.GONE
                    Toast.makeText(this@MilestoneActivity, "Loading attachment is taking too long", Toast.LENGTH_SHORT).show()
                }
            }, 30000) // 30 seconds timeout
            
            dialog.setOnDismissListener {
                try {
                    webView.stopLoading()
                    webView.clearCache(true)
                } catch (e: Exception) {
                    Log.e("MilestoneActivity", "Error in dialog dismiss: ${e.message}")
                }
            }
            
            dialog.show()
        } catch (e: Exception) {
            Toast.makeText(this, "Cannot open attachment: ${e.message}", Toast.LENGTH_SHORT).show()
            Log.e("MilestoneActivity", "Error opening attachment: ${e.message}")
        }
    }
    
    private fun deleteMilestone(id: String, cardView: View) {
        // Show confirmation dialog
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Delete Milestone")
            .setMessage("Are you sure you want to delete this milestone? This action cannot be undone.")
            .setPositiveButton("Delete") { _, _ ->
                // First remove from UI for better user experience
                milestoneContainer.removeView(cardView)
                Toast.makeText(this@MilestoneActivity, "Milestone deleted", Toast.LENGTH_SHORT).show()
                
                // Then try to delete from backend
                try {
                // Call API to delete milestone
                val call = apiService.deleteMilestone(id, email ?: "")
                call.enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                        if (response.isSuccessful) {
                                Log.d("MilestoneActivity", "Milestone deleted successfully on server")
                        } else {
                                Log.e("MilestoneActivity", "Failed to delete milestone on server: ${response.code()}")
                        }
                    }
                    
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                            Log.e("MilestoneActivity", "Error deleting milestone on server: ${t.message}")
                    }
                })
                } catch (e: Exception) {
                    Log.e("MilestoneActivity", "Exception deleting milestone: ${e.message}")
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
