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

class AddInternshipActivity : AppCompatActivity() {

    private lateinit var etCompany: EditText
    private lateinit var etRole: EditText
    private lateinit var etDates: EditText
    private lateinit var etDescription: EditText
    private lateinit var btnSubmit: Button
    private lateinit var btnAttachment: Button
    private lateinit var tvSelectedFile: TextView
    private lateinit var sessionManager: SessionManager

    private var fileUri: Uri? = null
    private var email: String? = null

    companion object {
        const val FILE_PICK_CODE = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.add_internship)

        // Initialize SessionManager
        sessionManager = SessionManager(this)

        etCompany = findViewById(R.id.etCompany)
        etRole = findViewById(R.id.etRole)
        etDates = findViewById(R.id.etDates)
        etDescription = findViewById(R.id.etDescription)
        btnSubmit = findViewById(R.id.btnSubmit)
        btnAttachment = findViewById(R.id.btnAddAttachment)
        tvSelectedFile = findViewById(R.id.tvSelectedFile)

        // Get email from intent
        email = intent.getStringExtra("email")
        Log.d("AddInternshipActivity", "Email from intent: $email")
        
        // If email is null, try to get from SessionManager
        if (email.isNullOrEmpty()) {
            email = sessionManager.getEmail()
            Log.d("AddInternshipActivity", "Email from SessionManager: $email")
        } else {
            // Save email to SessionManager
            sessionManager.saveEmail(email!!)
            Log.d("AddInternshipActivity", "Email saved to SessionManager: $email")
        }

        btnAttachment.setOnClickListener { pickFile() }
        btnSubmit.setOnClickListener { submitInternship() }
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

    private fun submitInternship() {
        val company = etCompany.text.toString().trim()
        val role = etRole.text.toString().trim()
        val dates = etDates.text.toString().trim()
        val description = etDescription.text.toString().trim()
        
        Log.d("AddInternshipActivity", "Email: $email")
        Log.d("AddInternshipActivity", "Company: $company, Role: $role")
        Log.d("AddInternshipActivity", "Dates: $dates, Description: $description")

        if (email.isNullOrEmpty() || company.isBlank() || role.isBlank() || dates.isBlank() || description.isBlank()) {
            Toast.makeText(this, "Please fill in all fields", Toast.LENGTH_SHORT).show()
            return
        }

        val formData = mutableMapOf<String, RequestBody>()
        formData["email"] = email!!.toPlainRequestBody()
        formData["company"] = company.toPlainRequestBody()
        formData["role"] = role.toPlainRequestBody()
        formData["dates"] = dates.toPlainRequestBody()
        formData["description"] = description.toPlainRequestBody()
        
        // Debug log for request data
        Log.d("AddInternshipActivity", "Request data: email=${email}, company=${company}, role=${role}, dates=${dates}, description=${description}")

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
        val call = apiService.addInternship(formData, filePart)

        call.enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                Log.d("AddInternshipActivity", "Response code: ${response.code()}")
                
                if (response.isSuccessful) {
                    val responseBody = response.body()
                    Log.d("AddInternshipActivity", "Response successful: $responseBody")
                    Toast.makeText(this@AddInternshipActivity, "Internship submitted!", Toast.LENGTH_SHORT).show()
                    // Set result code for the calling activity to know it should refresh
                    setResult(RESULT_OK)
                    finish()
                } else {
                    try {
                        val errorBody = response.errorBody()?.string()
                        Log.e("AddInternshipActivity", "Error response: $errorBody")
                        Toast.makeText(
                            this@AddInternshipActivity,
                            "Failed: ${response.message()} (${response.code()}) - $errorBody",
                            Toast.LENGTH_SHORT
                        ).show()
                    } catch (e: Exception) {
                        Log.e("AddInternshipActivity", "Error parsing error response: ${e.message}")
                        Toast.makeText(
                            this@AddInternshipActivity,
                            "Failed: ${response.message()} (${response.code()})",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                Log.e("AddInternshipActivity", "Network error: ${t.message}", t)
                Toast.makeText(this@AddInternshipActivity, "Error: ${t.message}", Toast.LENGTH_LONG).show()
            }
        })
    }
}
