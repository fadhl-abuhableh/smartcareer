package com.example.smartcareer


import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.activities.LoginActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Launch Resume Feedback screen directly
        startActivity(Intent(this, LoginActivity::class.java))
        finish()
    }
}
