-- Create user_profiles table
CREATE TABLE IF NOT EXISTS `user_profiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL DEFAULT '',
  `bio` text,
  `birthday` date DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `profile_image_url` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `fk_user_profiles_email` FOREIGN KEY (`email`) REFERENCES `users` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add index for faster lookups by email
CREATE INDEX IF NOT EXISTS `idx_user_profiles_email` ON `user_profiles` (`email`);

-- Add bio field to existing table if it doesn't exist
ALTER TABLE `user_profiles` ADD COLUMN IF NOT EXISTS `bio` text AFTER `name`;

-- Sample query to test the table
-- SELECT * FROM user_profiles LIMIT 5;

-- Notes:
-- 1. This assumes that the 'users' table already exists with 'email' as a unique field
-- 2. The foreign key constraint ensures data integrity between users and profiles
-- 3. The ON DELETE CASCADE ensures that when a user is deleted, their profile is also deleted
-- 4. The ON UPDATE CASCADE ensures that if a user's email changes, their profile email is updated as well 