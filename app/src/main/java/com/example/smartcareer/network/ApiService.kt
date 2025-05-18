package com.example.smartcareer.network

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Call
import retrofit2.http.*

interface ApiService {

    // ✅ Register user
    @FormUrlEncoded
    @POST("/register")
    fun register(
        @Field("email") email: String,
        @Field("password") password: String
    ): Call<Map<String, String>>

    // ✅ Login user
    @FormUrlEncoded
    @POST("/login")
    fun login(
        @Field("email") email: String,
        @Field("password") password: String
    ): Call<Map<String, String>>

    // ✅ Add internship
    @Multipart
    @POST("/add_internship")
    fun addInternship(
        @PartMap data: Map<String, @JvmSuppressWildcards RequestBody>,
        @Part attachment: MultipartBody.Part? = null
    ): Call<Map<String, String>>

    // ✅ Get user internships
    @GET("/get_internships")
    fun getUserInternships(
        @Query("email") email: String
    ): Call<List<Map<String, String>>>
    
    // ✅ Delete internship
    @FormUrlEncoded
    @POST("/delete_internship")
    fun deleteInternship(
        @Field("id") id: String,
        @Field("email") email: String
    ): Call<Map<String, String>>

    // ✅ Add milestone
    @Multipart
    @POST("/add_milestone")
    fun addMilestone(
        @PartMap data: Map<String, @JvmSuppressWildcards RequestBody>,
        @Part attachment: MultipartBody.Part? = null
    ): Call<Map<String, String>>
    
    // ✅ Get user milestones
    @GET("/get_milestones")
    fun getUserMilestones(
        @Query("email") email: String
    ): Call<List<Map<String, String>>>
    
    // ✅ Delete milestone
    @FormUrlEncoded
    @POST("/delete_milestone")
    fun deleteMilestone(
        @Field("id") id: String,
        @Field("email") email: String
    ): Call<Map<String, String>>
    
    // ✅ Get career advice
    @POST("/api/career-advice")
    fun getCareerAdvice(
        @Body requestData: Map<String, String>
    ): Call<Map<String, String>>
    
    // ✅ Get resume feedback
    @POST("/api/resume-feedback")
    fun getResumeFeedback(
        @Body requestData: Map<String, String>
    ): Call<Map<String, String>>
    
    // ✅ Get detailed roadmap
    @POST("/api/detailed-roadmap")
    fun getDetailedRoadmap(
        @Body requestData: Map<String, String>
    ): Call<List<Map<String, String>>>

    // ✅ Get user profile
    @GET("/api/user-profile")
    fun getUserProfile(
        @Query("email") email: String
    ): Call<Map<String, Any>>

    // ✅ Update user profile
    @Multipart
    @POST("/update-profile")
    fun updateUserProfile(
        @PartMap data: Map<String, @JvmSuppressWildcards RequestBody>,
        @Part profileImage: MultipartBody.Part? = null
    ): Call<Any>
    
    // ✅ Update user profile with form-encoded data
    @FormUrlEncoded
    @POST("/api/update-profile")
    fun updateUserProfileForm(
        @Field("name") name: String? = null,
        @Field("bio") bio: String? = null,
        @Field("phone") phone: String? = null,
        @Field("birthday") birthday: String? = null,
        @Field("current_email") currentEmail: String? = null
    ): Call<Map<String, String>>
    
    // ✅ Update user profile with JSON data
    @POST("/api/update-profile")
    fun updateUserProfileJson(
        @Body profileData: Map<String, String>  // Email is optional, only needed for identification
    ): Call<Map<String, String>>
    
    // ✅ Change password
    @FormUrlEncoded
    @POST("/change-password")
    fun changePassword(
        @Field("email") email: String,
        @Field("current_password") currentPassword: String,
        @Field("new_password") newPassword: String
    ): Call<Map<String, String>>

    // ✅ Update user profile image
    @Multipart
    @POST("/api/update-profile-image")
    fun updateUserProfileImage(
        @PartMap data: Map<String, @JvmSuppressWildcards RequestBody>,
        @Part profileImage: MultipartBody.Part
    ): Call<Map<String, String>>

    // ✅ Update user email
    @FormUrlEncoded
    @POST("/api/change-email")
    fun changeEmail(
        @Field("current_email") currentEmail: String,
        @Field("new_email") newEmail: String,
        @Field("password") password: String
    ): Call<Map<String, String>>
}
