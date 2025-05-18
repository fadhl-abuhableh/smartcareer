package com.example.smartcareer.models

/**
 * Data class representing a user profile
 */
data class UserProfile(
    val email: String,
    val name: String = "",
    val birthday: String = "",
    val phone: String = "",
    val profileImageUrl: String = "",
    val password: String = "",
    val bio: String = "No bio information available yet. Update your profile to add your professional summary."
) {
    /**
     * Convert profile to a map for API requests
     */
    fun toMap(): Map<String, String> {
        val map = mutableMapOf(
            "current_email" to email,
            "new_email" to email,
            "name" to name,
            "birthday" to birthday,
            "phone" to phone,
            "bio" to bio
        )
        
        if (password.isNotEmpty()) {
            map["password"] = password
        }
        
        return map
    }

    companion object {
        /**
         * Create a UserProfile object from a map returned by the API
         */
        fun fromMap(map: Map<String, Any>): UserProfile {
            return UserProfile(
                email = map["email"] as? String ?: "",
                name = map["name"] as? String ?: "",
                birthday = map["birthday"] as? String ?: "",
                phone = map["phone"] as? String ?: "",
                profileImageUrl = map["profile_image_url"] as? String ?: "",
                bio = map["bio"] as? String ?: "No bio information available yet.",
                password = ""
            )
        }
        
        /**
         * Create a default user profile for when the API call fails
         */
        fun createDefaultProfile(email: String): UserProfile {
            return UserProfile(
                email = email,
                name = "User",
                bio = "Welcome to SmartCareer! Your profile information will appear here once you update your profile details."
            )
        }
    }
} 