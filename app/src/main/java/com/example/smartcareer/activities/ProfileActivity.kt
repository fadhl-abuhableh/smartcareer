package com.example.smartcareer.activities

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.models.UserProfile
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import com.example.smartcareer.utils.SessionManager
import com.google.android.material.textfield.TextInputEditText
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

/**
 * Simplified ProfileActivity that just displays basic information
 */
class ProfileActivity : AppCompatActivity() {
    
    private lateinit var tvUserName: TextView
    private lateinit var tvUserEmail: TextView
    private lateinit var tvUserBio: TextView
    private lateinit var tvUserBirthday: TextView
    private lateinit var tvUserPhone: TextView
    private lateinit var btnEditProfile: Button
    private lateinit var btnBack: Button
    private lateinit var btnLogout: Button
    private lateinit var btnChangePassword: Button
    private lateinit var btnChangeEmail: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var sessionManager: SessionManager
    private lateinit var apiService: ApiService
    private var email: String? = null
    private var currentProfile: UserProfile? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_profile)
            
            // Initialize session manager and API service
            sessionManager = SessionManager(this)
            apiService = ApiClient.getClient().create(ApiService::class.java)
            
            // Initialize views
            tvUserName = findViewById(R.id.tvUserName)
            tvUserEmail = findViewById(R.id.tvUserEmail)
            tvUserBio = findViewById(R.id.tvUserBio)
            tvUserBirthday = findViewById(R.id.tvUserBirthday)
            tvUserPhone = findViewById(R.id.tvUserPhone)
            btnEditProfile = findViewById(R.id.btnEditProfile)
            btnBack = findViewById(R.id.btnBack)
            btnLogout = findViewById(R.id.btnLogout)
            btnChangePassword = findViewById(R.id.btnChangePassword)
            btnChangeEmail = findViewById(R.id.btnChangeEmail)
            progressBar = findViewById(R.id.progressBar)
            
            // Get email from intent or session with detailed logging
            val intentEmail = intent.getStringExtra("email")
            val sessionEmail = sessionManager.getEmail()
            
            Log.d("ProfileActivity", "Email from intent: $intentEmail")
            Log.d("ProfileActivity", "Email from session: $sessionEmail")
            
            email = intentEmail ?: sessionEmail
            
            if (email.isNullOrEmpty()) {
                Log.e("ProfileActivity", "No email available from intent or session")
                Toast.makeText(this, "Session expired. Please login again.", Toast.LENGTH_LONG).show()
                // Redirect to login
                sessionManager.clearSession()
                startActivity(Intent(this, LoginActivity::class.java))
                finish()
                return
            }
            
            // Save email to session if it came from intent
            if (intentEmail != null && intentEmail != sessionEmail) {
                Log.d("ProfileActivity", "Saving new email to session: $intentEmail")
                sessionManager.saveEmail(intentEmail)
            }
            
            // Set up listeners
            btnBack.setOnClickListener {
                finish()
            }
            
            btnEditProfile.setOnClickListener {
                showEditProfileDialog()
            }
            
            btnLogout.setOnClickListener {
                sessionManager.clearSession()
                val intent = Intent(this, LoginActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                startActivity(intent)
                finish()
            }
            
            btnChangePassword.setOnClickListener {
                showChangePasswordDialog()
            }
            
            btnChangeEmail.setOnClickListener {
                showChangeEmailDialog()
            }
            
            // Load user profile
            loadUserProfile()
            
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error in ProfileActivity: ${e.message}")
            e.printStackTrace()
            Toast.makeText(this, "Error showing profile", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
    
    private fun loadUserProfile() {
        progressBar.visibility = View.VISIBLE
        
        // Set default values from session while API loads
        val userName = sessionManager.getUserName() ?: "User"
        val userEmail = email ?: "No email available"
        
        tvUserName.text = userName
        tvUserEmail.text = userEmail
        
        // If no email, can't load profile
        if (email.isNullOrEmpty()) {
            progressBar.visibility = View.GONE
            return
        }
        
        // Load profile from API
        val call = apiService.getUserProfile(email!!)
        call.enqueue(object : Callback<Map<String, Any>> {
            override fun onResponse(call: Call<Map<String, Any>>, response: Response<Map<String, Any>>) {
                progressBar.visibility = View.GONE
                
                if (response.isSuccessful && response.body() != null) {
                    try {
                        val profileData = response.body()!!
                        
                        // Extract profile information with proper type casting
                        val name = (profileData["name"] as? String) ?: userName
                        val profileEmail = (profileData["email"] as? String) ?: userEmail
                        val bio = (profileData["bio"] as? String) ?: "No bio information available yet."
                        val birthday = (profileData["birthday"] as? String) ?: "Not specified"
                        val phone = (profileData["phone"] as? String) ?: "Not specified"
                        
                        // Store the current profile data
                        currentProfile = UserProfile(
                            email = profileEmail,
                            name = name,
                            bio = bio,
                            birthday = birthday,
                            phone = phone
                        )
                        
                        // Update UI
                        updateProfileUI(profileEmail, name, bio, phone, birthday)
                        
                        // Save to session for future use
                        sessionManager.saveUserName(name)
                        
                        Log.d("ProfileActivity", "Profile loaded successfully: $currentProfile")
                    } catch (e: Exception) {
                        Log.e("ProfileActivity", "Error parsing profile data: ${e.message}")
                        showError("Error loading profile data")
                    }
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Unknown error"
                    Log.e("ProfileActivity", "Failed to load profile: $errorBody")
                    showError("Failed to load profile: ${response.code()}")
                }
            }
            
            override fun onFailure(call: Call<Map<String, Any>>, t: Throwable) {
                progressBar.visibility = View.GONE
                Log.e("ProfileActivity", "Error loading profile: ${t.message}")
                showError("Network error: ${t.message}")
                
                // Use default profile when API fails
                if (email != null) {
                    val defaultProfile = UserProfile.createDefaultProfile(email!!)
                    currentProfile = defaultProfile
                    updateProfileUI(
                        defaultProfile.email,
                        defaultProfile.name,
                        defaultProfile.bio,
                        defaultProfile.phone,
                        defaultProfile.birthday
                    )
                }
            }
        })
    }
    
    private fun showChangePasswordDialog() {
        try {
            val dialogView = layoutInflater.inflate(R.layout.dialog_change_password, null)
            
            // Get references to dialog views
            val etCurrentPassword = dialogView.findViewById<EditText>(R.id.etCurrentPassword)
            val etNewPassword = dialogView.findViewById<EditText>(R.id.etNewPassword)
            val etConfirmPassword = dialogView.findViewById<EditText>(R.id.etConfirmPassword)
            
            val dialog = AlertDialog.Builder(this)
                .setTitle("Change Password")
                .setView(dialogView)
                .setPositiveButton("Save") { _, _ ->
                    // Get values
                    val currentPassword = etCurrentPassword.text.toString()
                    val newPassword = etNewPassword.text.toString()
                    val confirmPassword = etConfirmPassword.text.toString()
                    
                    // Validate
                    if (newPassword != confirmPassword) {
                        Toast.makeText(this, "Passwords don't match", Toast.LENGTH_SHORT).show()
                        return@setPositiveButton
                    }
                    
                    // Update password
                    updatePassword(currentPassword, newPassword)
                }
                .setNegativeButton("Cancel", null)
                .create()
            
            dialog.show()
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error showing password dialog: ${e.message}")
            Toast.makeText(this, "Error opening password form", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun updatePassword(currentPassword: String, newPassword: String) {
        progressBar.visibility = View.VISIBLE
        
        if (email.isNullOrEmpty()) {
            progressBar.visibility = View.GONE
            Toast.makeText(this, "Email not available", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Log request details
        Log.d("ProfileActivity", "Sending password update request for user: $email")
        
        // Use the dedicated password change endpoint instead
        val call = apiService.changePassword(email!!, currentPassword, newPassword)
        call.enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                progressBar.visibility = View.GONE
                
                // Log detailed response info
                Log.d("ProfileActivity", "Password update response code: ${response.code()}")
                Log.d("ProfileActivity", "Password update response body: ${response.body()}")
                
                if (response.isSuccessful) {
                    Toast.makeText(this@ProfileActivity, "Password updated successfully", Toast.LENGTH_SHORT).show()
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Unknown error"
                    Log.e("ProfileActivity", "Failed to update password: $errorBody")
                    Toast.makeText(this@ProfileActivity, "Failed to update password", Toast.LENGTH_SHORT).show()
                }
            }
            
            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                progressBar.visibility = View.GONE
                Log.e("ProfileActivity", "Error updating password: ${t.message}", t)
                Toast.makeText(this@ProfileActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
    
    private fun showChangeEmailDialog() {
        try {
            val dialogView = layoutInflater.inflate(R.layout.dialog_change_email, null)
            
            // Get references to dialog views
            val etCurrentEmail = dialogView.findViewById<EditText>(R.id.etCurrentEmail)
            val etNewEmail = dialogView.findViewById<EditText>(R.id.etNewEmail)
            val etPassword = dialogView.findViewById<EditText>(R.id.etPassword)
            
            // Pre-fill current email
            etCurrentEmail.setText(email)
            etCurrentEmail.isEnabled = false  // Make current email read-only
            
            val dialog = AlertDialog.Builder(this)
                .setTitle("Change Email")
                .setView(dialogView)
                .setPositiveButton("Save") { _, _ ->
                    // Get values
                    val newEmail = etNewEmail.text.toString().trim()
                    val password = etPassword.text.toString()
                    
                    // Validate
                    if (newEmail.isEmpty()) {
                        Toast.makeText(this, "New email is required", Toast.LENGTH_SHORT).show()
                        return@setPositiveButton
                    }
                    if (!android.util.Patterns.EMAIL_ADDRESS.matcher(newEmail).matches()) {
                        Toast.makeText(this, "Please enter a valid email address", Toast.LENGTH_SHORT).show()
                        return@setPositiveButton
                    }
                    if (password.isEmpty()) {
                        Toast.makeText(this, "Password is required", Toast.LENGTH_SHORT).show()
                        return@setPositiveButton
                    }
                    
                    // Update email
                    updateEmail(newEmail, password)
                }
                .setNegativeButton("Cancel", null)
                .create()
            
            dialog.show()
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error showing email dialog: ${e.message}")
            Toast.makeText(this, "Error opening email form", Toast.LENGTH_SHORT).show()
        }
    }

    private fun updateEmail(newEmail: String, password: String) {
        progressBar.visibility = View.VISIBLE
        
        if (email.isNullOrEmpty()) {
            progressBar.visibility = View.GONE
            Toast.makeText(this, "Current email not available", Toast.LENGTH_SHORT).show()
            return
        }
        
        try {
            // Make API request using the new form-encoded endpoint
            val call = apiService.changeEmail(
                currentEmail = email!!,
                newEmail = newEmail,
                password = password
            )
            
            call.enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    progressBar.visibility = View.GONE
                    
                    if (response.isSuccessful) {
                        // Update successful
                        Toast.makeText(this@ProfileActivity, "Email updated successfully", Toast.LENGTH_SHORT).show()
                        
                        // Update session and local email
                        sessionManager.saveEmail(newEmail)
                        email = newEmail
                        
                        // Update UI
                        tvUserEmail.text = newEmail
                    } else {
                        val errorBody = response.errorBody()?.string() ?: "Unknown error"
                        Log.e("ProfileActivity", "Email update failed: $errorBody")
                        
                        when (response.code()) {
                            400 -> showValidationError(errorBody)
                            401 -> showAuthError()
                            else -> showDetailedError(errorBody, response.code())
                        }
                    }
                }
                
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    progressBar.visibility = View.GONE
                    Log.e("ProfileActivity", "Email update failed: ${t.message}")
                    showError("Network error: ${t.message}")
                }
            })
        } catch (e: Exception) {
            progressBar.visibility = View.GONE
            Log.e("ProfileActivity", "Error preparing email update: ${e.message}")
            showError("Error: ${e.message}")
        }
    }
    
    private fun showEditProfileDialog() {
        try {
            val dialogView = layoutInflater.inflate(R.layout.dialog_edit_profile, null)
            
            // Get references to dialog views
            val etName = dialogView.findViewById<TextInputEditText>(R.id.etName)
            val etBio = dialogView.findViewById<TextInputEditText>(R.id.etBio)
            val etPhone = dialogView.findViewById<TextInputEditText>(R.id.etPhone)
            val etBirthday = dialogView.findViewById<TextInputEditText>(R.id.etBirthday)
            
            // Pre-fill with current values
            currentProfile?.let { profile ->
                etName.setText(profile.name)
                etBio.setText(profile.bio)
                etPhone.setText(profile.phone)
                etBirthday.setText(profile.birthday)
            }
            
            // Create dialog
            val dialog = AlertDialog.Builder(this)
                .setTitle("Edit Profile")
                .setView(dialogView)
                .setPositiveButton("Save", null) // Set to null initially
                .setNegativeButton("Cancel", null)
                .create()
            
            // Show dialog
            dialog.show()
            
            // Override positive button click to handle validation
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                // Get values
                val name = etName.text?.toString()?.trim() ?: ""
                val bio = etBio.text?.toString()?.trim() ?: ""
                val phone = etPhone.text?.toString()?.trim() ?: ""
                val birthday = etBirthday.text?.toString()?.trim() ?: ""
                
                // Validate birthday format if provided
                if (birthday.isNotEmpty()) {
                    try {
                        val dateFormat = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.getDefault())
                        dateFormat.isLenient = false
                        dateFormat.parse(birthday)
                    } catch (e: Exception) {
                        etBirthday.error = "Please use YYYY-MM-DD format"
                        return@setOnClickListener
                    }
                }
                
                // Validate phone if provided
                if (phone.isNotEmpty() && !phone.matches(Regex("^[+]?[0-9]{10,13}$"))) {
                    etPhone.error = "Please enter a valid phone number"
                    return@setOnClickListener
                }
                
                // If all validations pass, update profile
                dialog.dismiss()
                updateProfile(name, bio, phone, birthday)
            }
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error showing edit dialog: ${e.message}")
            Toast.makeText(this, "Error opening edit form", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun updateProfile(name: String, bio: String, phone: String, birthday: String) {
        progressBar.visibility = View.VISIBLE
        
        try {
            // Log request data in detail
            Log.d("ProfileActivity", "Profile update request data:")
            Log.d("ProfileActivity", "Name: $name")
            Log.d("ProfileActivity", "Bio: $bio")
            Log.d("ProfileActivity", "Phone: $phone")
            Log.d("ProfileActivity", "Birthday: $birthday")
            Log.d("ProfileActivity", "Email: $email")
            
            // Make API request using the form-encoded endpoint
            val call = apiService.updateUserProfileForm(
                name = name.takeIf { it.isNotEmpty() },
                bio = bio.takeIf { it.isNotEmpty() },
                phone = phone.takeIf { it.isNotEmpty() },
                birthday = birthday.takeIf { it.isNotEmpty() },
                currentEmail = email
            )
            
            call.enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    progressBar.visibility = View.GONE
                    
                    if (response.isSuccessful) {
                        val result = response.body()
                        if (result != null) {
                            // Update successful
                            Toast.makeText(this@ProfileActivity, "Profile updated successfully", Toast.LENGTH_SHORT).show()
                            
                            // Update current profile with new data
                            currentProfile = currentProfile?.copy(
                                name = name,
                                bio = bio,
                                phone = phone,
                                birthday = birthday
                            )
                            
                            // Save to session for persistence
                            sessionManager.saveUserName(name)
                            
                            // Update UI
                            updateProfileUI(
                                email ?: currentProfile?.email ?: "",
                                name,
                                bio,
                                phone,
                                birthday
                            )
                            
                            // Reload profile to ensure data is synced with server
                            loadUserProfile()
                        } else {
                            showError("Empty response from server")
                        }
                    } else {
                        // Handle error with detailed logging
                        val errorBody = response.errorBody()?.string() ?: "Unknown error"
                        Log.e("ProfileActivity", "Profile update failed with code: ${response.code()}")
                        Log.e("ProfileActivity", "Error response body: $errorBody")
                        
                        when (response.code()) {
                            400 -> {
                                Log.e("ProfileActivity", "Bad Request - Invalid data sent to server")
                                showValidationError(errorBody)
                            }
                            401 -> showAuthError()
                            else -> showDetailedError(errorBody, response.code())
                        }
                    }
                }
                
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    progressBar.visibility = View.GONE
                    Log.e("ProfileActivity", "Profile update failed: ${t.message}")
                    showError("Network error: ${t.message}")
                }
            })
        } catch (e: Exception) {
            progressBar.visibility = View.GONE
            Log.e("ProfileActivity", "Error preparing profile update: ${e.message}")
            showError("Error: ${e.message}")
        }
    }
    
    private fun updateProfileUI(newEmail: String, name: String, bio: String, phone: String, birthday: String) {
        // Update UI elements
        tvUserEmail.text = newEmail
        tvUserName.text = name
        tvUserBio.text = bio
        tvUserBirthday.text = birthday
        tvUserPhone.text = phone
        
        // Update current profile
        currentProfile = currentProfile?.copy(
            email = newEmail,
            name = name,
            bio = bio,
            phone = phone,
            birthday = birthday
        )
        
        // Save to session
        sessionManager.saveUserName(name)
    }
    
    private fun showValidationError(errorBody: String) {
        AlertDialog.Builder(this)
            .setTitle("Validation Error")
            .setMessage("Please check your input:\n$errorBody")
            .setPositiveButton("OK", null)
            .show()
    }
    
    private fun showAuthError() {
        AlertDialog.Builder(this)
            .setTitle("Authentication Error")
            .setMessage("Your session has expired. Please log in again.")
            .setPositiveButton("OK") { _, _ ->
                sessionManager.clearSession()
                startActivity(Intent(this, LoginActivity::class.java))
                finish()
            }
            .setCancelable(false)
            .show()
    }
    
    private fun showDetailedError(errorBody: String, code: Int) {
        val message = """
            Profile update failed with code: $code
            
            Details: $errorBody
            
            Please report this to your system administrator.
        """.trimIndent()
        
        AlertDialog.Builder(this)
            .setTitle("Update Error")
            .setMessage(message)
            .setPositiveButton("OK", null)
            .show()
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    override fun onResume() {
        super.onResume()
        loadUserProfile() // Reload profile when returning to this activity
    }
} 