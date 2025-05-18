package com.example.smartcareer.activities

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import com.example.smartcareer.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import android.util.Log
import com.google.android.material.textfield.TextInputLayout

class LoginActivity : AppCompatActivity() {

    private lateinit var etEmail: EditText
    private lateinit var etPassword: EditText
    private lateinit var etConfirmPassword: EditText
    private lateinit var layoutConfirmPassword: TextInputLayout
    private lateinit var btnAction: Button
    private lateinit var tvToggleAuth: TextView
    private lateinit var tvLoginTitle: TextView
    private lateinit var sessionManager: SessionManager

    private var isLoginMode = true
    private lateinit var apiService: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        // Initialize SessionManager
        sessionManager = SessionManager(this)

        etEmail = findViewById(R.id.etEmail)
        etPassword = findViewById(R.id.etPassword)
        etConfirmPassword = findViewById(R.id.etConfirmPassword)
        layoutConfirmPassword = findViewById(R.id.layoutConfirmPassword)
        btnAction = findViewById(R.id.btnAction)
        tvToggleAuth = findViewById(R.id.tvToggleAuth)
        tvLoginTitle = findViewById(R.id.tvLoginTitle)

        apiService = ApiClient.getClient().create(ApiService::class.java)

        btnAction.setOnClickListener {
            val email = etEmail.text.toString().trim()
            val password = etPassword.text.toString().trim()
            val confirmPassword = etConfirmPassword.text.toString().trim()

            if (email.isEmpty() || password.isEmpty() || (!isLoginMode && confirmPassword.isEmpty())) {
                Toast.makeText(this, "Please fill in all fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (!isLoginMode && password != confirmPassword) {
                Toast.makeText(this, "Passwords do not match", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (isLoginMode) {
                loginUser(email, password)
            } else {
                registerUser(email, password)
            }
        }

        tvToggleAuth.setOnClickListener {
            isLoginMode = !isLoginMode
            updateMode()
        }

        updateMode()
    }

    private fun updateMode() {
        if (isLoginMode) {
            layoutConfirmPassword.visibility = View.GONE
            tvLoginTitle.text = "Welcome Back"
            btnAction.text = "Login"
            tvToggleAuth.text = "Don't have an account? Register"
        } else {
            layoutConfirmPassword.visibility = View.VISIBLE
            tvLoginTitle.text = "Create Account"
            btnAction.text = "Register"
            tvToggleAuth.text = "Already have an account? Login"
        }
    }

    private fun loginUser(email: String, password: String) {
        val call = apiService.login(email, password)
        call.enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                if (response.isSuccessful && response.body()?.get("message") == "Login successful") {
                    Log.d("LoginActivity", "Login success. Launching HomeActivity")

                    // Save email to SessionManager at login time
                    sessionManager.saveEmail(email)
                    Log.d("LoginActivity", "Email saved to SessionManager: $email")

                    // ✅ Open HomeActivity instead of AddInternshipActivity
                    val intent = Intent(this@LoginActivity, HomeActivity::class.java)
                    intent.putExtra("email", email)
                    startActivity(intent)
                    finish()
                } else {
                    Toast.makeText(this@LoginActivity, "Login failed", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                Toast.makeText(this@LoginActivity, "Error: ${t.message}", Toast.LENGTH_LONG).show()
            }
        })
    }

    private fun registerUser(email: String, password: String) {
        val call = apiService.register(email, password)
        call.enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                if (response.isSuccessful && response.body()?.get("message")?.contains("User") == true) {
                    Toast.makeText(this@LoginActivity, "Registration successful. You can now log in.", Toast.LENGTH_SHORT).show()
                    isLoginMode = true
                    updateMode()
                } else {
                    val errorMsg = when (response.code()) {
                        409 -> "This email is already registered."
                        400 -> "Invalid request. Please check your input."
                        500 -> "Server error. Please try again later."
                        else -> "Registration failed. Code: ${response.code()}"
                    }
                    Toast.makeText(this@LoginActivity, errorMsg, Toast.LENGTH_LONG).show()
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                Toast.makeText(this@LoginActivity, "Error: ${t.message}", Toast.LENGTH_LONG).show()
            }
        })
    }
}
