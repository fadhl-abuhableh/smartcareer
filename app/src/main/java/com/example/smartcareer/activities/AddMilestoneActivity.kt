package com.example.smartcareer.activities

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.util.Log
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.smartcareer.R
import com.example.smartcareer.network.ApiClient
import com.example.smartcareer.network.ApiService
import com.example.smartcareer.utils.SessionManager
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File
import java.io.FileOutputStream

class AddMilestoneActivity : AppCompatActivity() {

    private lateinit var etTitle: EditText
    private lateinit var etDate: EditText
    private lateinit var etDescription: EditText
    private lateinit var btnSubmit: Button
    private lateinit var btnAttach: Button
    private lateinit var tvSelectedFile: TextView
    private var fileUri: Uri? = null
    private var email: String? = null
    private lateinit var sessionManager: SessionManager

    companion object {
        const val FILE_PICK_CODE = 1010
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.add_milestones)

        // Initialize SessionManager
        sessionManager = SessionManager(this)

        etTitle = findViewById(R.id.etMilestoneTitle)
        etDate = findViewById(R.id.etMilestoneDate)
        etDescription = findViewById(R.id.etMilestoneDescription)
        btnSubmit = findViewById(R.id.btnSubmitMilestone)
        btnAttach = findViewById(R.id.btnAddMilestoneAttachment)
        tvSelectedFile = findViewById(R.id.tvMilestoneSelectedFile)

        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("AddMilestoneActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("AddMilestoneActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("AddMilestoneActivity", "Email saved to SessionManager: $email")
        }

        btnAttach.setOnClickListener {
            pickFile()
        }

        btnSubmit.setOnClickListener {
            submitMilestone()
        }
    }

    private fun pickFile() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.type = "*/*"
        val mimeTypes = arrayOf("application/pdf", "image/*")
        intent.putExtra(Intent.EXTRA_MIME_TYPES, mimeTypes)
        startActivityForResult(intent, FILE_PICK_CODE)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == FILE_PICK_CODE && resultCode == Activity.RESULT_OK) {
            fileUri = data?.data
            fileUri?.let {
                val fileName = getFileNameFromUri(it)
                tvSelectedFile.text = "Selected: $fileName"
            }
        }
    }

    private fun getFileNameFromUri(uri: Uri): String {
        var name = "unknown_file"
        val cursor = contentResolver.query(uri, null, null, null, null)
        cursor?.use {
            if (it.moveToFirst()) {
                val index = it.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (index >= 0) {
                    name = it.getString(index)
                }
            }
        }
        return name
    }

    private fun String.toPlainRequestBody(): RequestBody =
        RequestBody.create("text/plain".toMediaTypeOrNull(), this)

    private fun submitMilestone() {
        val title = etTitle.text.toString().trim()
        val date = etDate.text.toString().trim()
        val description = etDescription.text.toString().trim()

        // Debug logs
        Log.d("AddMilestoneActivity", "Email: $email")
        Log.d("AddMilestoneActivity", "Title: $title, isEmpty: ${title.isEmpty()}, isBlank: ${title.isBlank()}")
        Log.d("AddMilestoneActivity", "Date: $date, isEmpty: ${date.isEmpty()}, isBlank: ${date.isBlank()}")
        Log.d("AddMilestoneActivity", "Description: $description, isEmpty: ${description.isEmpty()}, isBlank: ${description.isBlank()}")

        if (email.isNullOrEmpty() || title.isBlank() || date.isBlank()) {
            Toast.makeText(this, "Please fill in all required fields", Toast.LENGTH_SHORT).show()
            // Detailed toast message for debugging
            val missingFields = mutableListOf<String>().apply {
                if (email.isNullOrEmpty()) add("Email")
                if (title.isBlank()) add("Title")
                if (date.isBlank()) add("Date")
            }
            Toast.makeText(this, "Missing fields: ${missingFields.joinToString()}", Toast.LENGTH_LONG).show()
            return
        }

        val data = mutableMapOf<String, RequestBody>()
        data["email"] = email!!.toPlainRequestBody()
        data["title"] = title.toPlainRequestBody()
        data["date"] = date.toPlainRequestBody()
        data["description"] = description.toPlainRequestBody()

        // Debug log for request data
        Log.d("AddMilestoneActivity", "Request data: email=${email}, title=${title}, date=${date}, description=${description}")

        val filePart: MultipartBody.Part? = fileUri?.let {
            val inputStream = contentResolver.openInputStream(it)!!
            val file = File(cacheDir, getFileNameFromUri(it))
            val outputStream = FileOutputStream(file)
            inputStream.copyTo(outputStream)
            outputStream.close()

            val mimeType = contentResolver.getType(it) ?: "application/octet-stream"
            val requestFile = RequestBody.create(mimeType.toMediaTypeOrNull(), file)
            MultipartBody.Part.createFormData("attachment", file.name, requestFile)
        }

        val apiService = ApiClient.getClient().create(ApiService::class.java)
        val call = apiService.addMilestone(data, filePart)

        call.enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                Log.d("AddMilestoneActivity", "Response code: ${response.code()}")
                
                if (response.isSuccessful) {
                    val responseBody = response.body()
                    Log.d("AddMilestoneActivity", "Response successful: $responseBody")
                    Toast.makeText(this@AddMilestoneActivity, "Milestone submitted!", Toast.LENGTH_SHORT).show()
                    finish()
                } else {
                    try {
                        val errorBody = response.errorBody()?.string()
                        Log.e("AddMilestoneActivity", "Error response: $errorBody")
                        Toast.makeText(
                            this@AddMilestoneActivity,
                            "Failed: ${response.message()} (${response.code()}) - $errorBody",
                            Toast.LENGTH_SHORT
                        ).show()
                    } catch (e: Exception) {
                        Log.e("AddMilestoneActivity", "Error parsing error response: ${e.message}")
                        Toast.makeText(
                            this@AddMilestoneActivity,
                            "Failed: ${response.message()} (${response.code()})",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                Log.e("AddMilestoneActivity", "Network error: ${t.message}", t)
                Toast.makeText(this@AddMilestoneActivity, "Error: ${t.message}", Toast.LENGTH_LONG).show()
            }
        })
    }
} 
