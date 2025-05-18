package com.example.smartcareer.utils

import android.content.Context
import android.content.SharedPreferences

class SessionManager(context: Context) {
    private val sharedPreferences: SharedPreferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    private val editor: SharedPreferences.Editor = sharedPreferences.edit()

    companion object {
        private const val PREF_NAME = "SmartCareerPrefs"
        private const val KEY_EMAIL = "user_email"
        private const val KEY_USERNAME = "user_name"
    }

    // Save email to SharedPreferences
    fun saveEmail(email: String) {
        editor.putString(KEY_EMAIL, email)
        editor.apply()
    }

    // Get email from SharedPreferences
    fun getEmail(): String? {
        return sharedPreferences.getString(KEY_EMAIL, null)
    }
    
    // Save username to SharedPreferences
    fun saveUserName(userName: String) {
        editor.putString(KEY_USERNAME, userName)
        editor.apply()
    }

    // Get username from SharedPreferences
    fun getUserName(): String? {
        return sharedPreferences.getString(KEY_USERNAME, null)
    }

    // Clear all data from SharedPreferences
    fun clearSession() {
        editor.clear()
        editor.apply()
    }
} 