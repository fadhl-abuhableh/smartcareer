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
import com.example.smartcareer.models.Internship
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import com.example.smartcareer.utils.SessionManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class InternshipActivity : AppCompatActivity() {

    private lateinit var internshipContainer: LinearLayout
    private lateinit var addInternshipButton: Button
    private var email: String? = null
    private lateinit var apiService: ApiService
    private lateinit var sessionManager: SessionManager

    private companion object {
        const val ADD_INTERNSHIP_REQUEST_CODE = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.internships)
        
        // Initialize SessionManager
        sessionManager = SessionManager(this)
        
        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("InternshipActivity", "onCreate - Email from intent: $email")
        
        // If email is null, try to get it from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("InternshipActivity", "Email retrieved from SessionManager: $email")
        } else {
            // Save email to SessionManager for future use
            sessionManager.saveEmail(email!!)
            Log.d("InternshipActivity", "Email saved to SessionManager: $email")
        }

        internshipContainer = findViewById(R.id.internshipContainer)
        addInternshipButton = findViewById(R.id.btnAddInternship)
        
        apiService = ApiClient.getClient().create(ApiService::class.java)

        // Load internships from API
        loadInternships()

        addInternshipButton.setOnClickListener {
            val intent = Intent(this, AddInternshipActivity::class.java)
            intent.putExtra("email", email)
            startActivityForResult(intent, ADD_INTERNSHIP_REQUEST_CODE)
        }

        val navView = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        navView.selectedItemId = R.id.menu_internships
        navView.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.menu_home -> {
                    val intent = Intent(this, HomeActivity::class.java)
                    intent.putExtra("email", email)
                    startActivity(intent)
                    true
                }
                R.id.menu_milestones -> {
                    val intent = Intent(this, MilestoneActivity::class.java)
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
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        Log.d("InternshipActivity", "onActivityResult - Email: $email")
        if (requestCode == ADD_INTERNSHIP_REQUEST_CODE && resultCode == RESULT_OK) {
            // Refresh the internship list when a new internship is added
            loadInternships()
        }
    }
    
    override fun onResume() {
        super.onResume()
        Log.d("InternshipActivity", "onResume - Email: $email")
        // Refresh internships when returning to this activity from other sources
        // This is a fallback in case onActivityResult doesn't trigger
        loadInternships()
    }
    
    private fun loadInternships() {
        Log.d("InternshipActivity", "loadInternships - Email: $email")
        if (email.isNullOrEmpty()) {
            Toast.makeText(this, "Email not found", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Clear existing internships
        internshipContainer.removeAllViews()
        Log.d("InternshipActivity", "Cleared all internships from container")
        
        // Fetch internships from API
        val call = apiService.getUserInternships(email!!)
        call.enqueue(object : Callback<List<Map<String, String>>> {
            override fun onResponse(call: Call<List<Map<String, String>>>, response: Response<List<Map<String, String>>>) {
                Log.d("InternshipActivity", "API Response: ${response.code()}")
                
                if (response.isSuccessful) {
                    val internships = response.body()
                    Log.d("InternshipActivity", "Internships received: ${internships?.size ?: 0}")
                    
                    if (internships != null && internships.isNotEmpty()) {
                        // Clear container again just to be sure
                        internshipContainer.removeAllViews()
                        
                        for (internshipData in internships) {
                            val company = internshipData["company"] ?: ""
                            val role = internshipData["role"] ?: ""
                            val dates = internshipData["dates"] ?: ""
                            val description = internshipData["description"] ?: ""
                            val filename = internshipData["filename"]
                            val id = internshipData["id"]
                            
                            Log.d("InternshipActivity", "Adding internship - Company: $company, Role: $role, Description: $description")
                            addInternshipCard(company, role, dates, description, filename, id)
                        }
                    } else {
                        // No internships found, show message
                        Log.d("InternshipActivity", "No internships found for user")
                        addNoInternshipsMessage()
                    }
                } else {
                    Log.e("InternshipActivity", "Failed to load internships: ${response.code()}")
                    try {
                        val errorBody = response.errorBody()?.string()
                        Log.e("InternshipActivity", "Error response: $errorBody")
                    } catch (e: Exception) {
                        Log.e("InternshipActivity", "Error parsing error body: ${e.message}")
                    }
                    
                    Toast.makeText(this@InternshipActivity, "Failed to load internships", Toast.LENGTH_SHORT).show()
                    // Show dummy data as fallback
                    addDummyData()
                }
            }

            override fun onFailure(call: Call<List<Map<String, String>>>, t: Throwable) {
                Log.e("InternshipActivity", "Error loading internships: ${t.message}")
                Toast.makeText(this@InternshipActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                // Show dummy data as fallback
                addDummyData()
            }
        })
    }
    
    private fun addNoInternshipsMessage() {
        val inflater = LayoutInflater.from(this)
        val card = inflater.inflate(R.layout.internship_card, internshipContainer, false)
        
        card.findViewById<TextView>(R.id.tvCompany).text = "No internships found"
        card.findViewById<TextView>(R.id.tvRole).text = "Add your first internship"
        card.findViewById<TextView>(R.id.tvDates).text = ""
        card.findViewById<TextView>(R.id.tvDescription).text = ""
        
        internshipContainer.addView(card)
        Log.d("InternshipActivity", "Added 'no internships' message to container")
    }
    
    private fun addDummyData() {
        // Make sure the container is empty
        internshipContainer.removeAllViews()
        Log.d("InternshipActivity", "Adding dummy data")
        
        // Add dummy data when API fails
        addInternshipCard("Microsoft", "Cloud Intern", "May 2024 – August 2024", "Worked on Azure cloud infrastructure and deployment pipelines.", null, null)
        addInternshipCard("Cisco", "Network Intern", "Jan 2024 – Jun 2024", "Helped maintain network infrastructure and implemented security protocols.", null, null)
    }

    private fun addInternshipCard(company: String, role: String, dateRange: String, description: String = "", filename: String? = null, id: String? = null) {
        val inflater = LayoutInflater.from(this)
        val card = inflater.inflate(R.layout.internship_card, internshipContainer, false)

        card.findViewById<TextView>(R.id.tvCompany).text = company
        card.findViewById<TextView>(R.id.tvRole).text = role
        card.findViewById<TextView>(R.id.tvDates).text = dateRange
        card.findViewById<TextView>(R.id.tvDescription).text = description

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
        val btnDelete = card.findViewById<Button>(R.id.btnDeleteInternship)
        btnDelete.setOnClickListener {
            if (id != null) {
                deleteInternship(id, card)
            } else {
                // For dummy data without ID, just remove from UI
                internshipContainer.removeView(card)
                Toast.makeText(this, "Internship deleted", Toast.LENGTH_SHORT).show()
            }
        }

        internshipContainer.addView(card)
        Log.d("InternshipActivity", "Added internship card for $company")
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
                Log.e("InternshipActivity", "Error configuring WebView: ${e.message}")
            }
            
            // Set WebViewClient to handle loading events with safeguards for cancellation
            webView.webViewClient = object : android.webkit.WebViewClient() {
                override fun onPageStarted(view: android.webkit.WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                    if (!isFinishing) {
                        try {
                            super.onPageStarted(view, url, favicon)
                            progressBar.visibility = android.view.View.VISIBLE
                        } catch (e: Exception) {
                            Log.e("InternshipActivity", "Error in onPageStarted: ${e.message}")
                        }
                    }
                }
                
                override fun onPageFinished(view: android.webkit.WebView?, url: String?) {
                    if (!isFinishing) {
                        try {
                            super.onPageFinished(view, url)
                            progressBar.visibility = android.view.View.GONE
                        } catch (e: Exception) {
                            Log.e("InternshipActivity", "Error in onPageFinished: ${e.message}")
                        }
                    }
                }
                
                override fun onReceivedError(view: android.webkit.WebView?, request: android.webkit.WebResourceRequest?, error: android.webkit.WebResourceError?) {
                    if (!isFinishing) {
                        try {
                            super.onReceivedError(view, request, error)
                            progressBar.visibility = android.view.View.GONE
                            Toast.makeText(this@InternshipActivity, "Error loading attachment", Toast.LENGTH_SHORT).show()
                        } catch (e: Exception) {
                            Log.e("InternshipActivity", "Error in onReceivedError: ${e.message}")
                        }
                    }
                }
                
                // Handle SSL errors
                override fun onReceivedSslError(view: android.webkit.WebView?, handler: android.webkit.SslErrorHandler?, error: android.net.http.SslError?) {
                    Toast.makeText(this@InternshipActivity, "SSL Certificate Error", Toast.LENGTH_SHORT).show()
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
                    Log.e("InternshipActivity", "Error closing dialog: ${e.message}")
                }
            }
            
            // Load the URL with a timeout and fallback
            webView.loadUrl(attachmentUrl)
            
            // Add a timeout handler
            android.os.Handler(mainLooper).postDelayed({
                if (progressBar.visibility == android.view.View.VISIBLE) {
                    progressBar.visibility = android.view.View.GONE
                    Toast.makeText(this@InternshipActivity, "Loading attachment is taking too long", Toast.LENGTH_SHORT).show()
                }
            }, 30000) // 30 seconds timeout
            
            dialog.setOnDismissListener {
                try {
                    webView.stopLoading()
                    webView.clearCache(true)
                } catch (e: Exception) {
                    Log.e("InternshipActivity", "Error in dialog dismiss: ${e.message}")
                }
            }
            
            dialog.show()
        } catch (e: Exception) {
            Toast.makeText(this, "Cannot open attachment: ${e.message}", Toast.LENGTH_SHORT).show()
            Log.e("InternshipActivity", "Error opening attachment: ${e.message}")
        }
    }
    
    private fun deleteInternship(id: String, cardView: View) {
        // Show confirmation dialog
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Delete Internship")
            .setMessage("Are you sure you want to delete this internship? This action cannot be undone.")
            .setPositiveButton("Delete") { _, _ ->
                // First remove from UI for better user experience
                internshipContainer.removeView(cardView)
                Toast.makeText(this@InternshipActivity, "Internship deleted", Toast.LENGTH_SHORT).show()
                
                // Then try to delete from backend
                try {
                // Call API to delete internship
                val call = apiService.deleteInternship(id, email ?: "")
                call.enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                        if (response.isSuccessful) {
                                Log.d("InternshipActivity", "Internship deleted successfully on server")
                        } else {
                                Log.e("InternshipActivity", "Failed to delete internship on server: ${response.code()}")
                        }
                    }
                    
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                            Log.e("InternshipActivity", "Error deleting internship on server: ${t.message}")
                    }
                })
                } catch (e: Exception) {
                    Log.e("InternshipActivity", "Exception deleting internship: ${e.message}")
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
