package com.example.smartcareer.activities

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.utils.SessionManager
import com.google.android.material.bottomnavigation.BottomNavigationView

class InsightsActivity : AppCompatActivity() {

    private var email: String? = null
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.careerinsights)
        
        // Initialize SessionManager
        sessionManager = SessionManager(this)
        
        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("InsightsActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("InsightsActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("InsightsActivity", "Email saved to SessionManager: $email")
        }

        findViewById<Button>(R.id.btnResumeFeedback).setOnClickListener {
            val intent = Intent(this, ResumeFeedbackActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnCareerAdvice).setOnClickListener {
            val intent = Intent(this, CareerAdviceActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnRoadmap).setOnClickListener {
            val intent = Intent(this, RoadmapActivity::class.java)
            intent.putExtra("email", email)
            startActivity(intent)
        }

        val navView = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        navView.selectedItemId = R.id.menu_insights
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
                R.id.menu_milestones -> {
                    val intent = Intent(this, MilestoneActivity::class.java)
                    intent.putExtra("email", email)
                    startActivity(intent)
                    true
                }
                else -> false
            }
        }
    }
}
