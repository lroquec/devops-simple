CREATE DATABASE IF NOT EXISTS `microservices` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `microservices`;

-- Users table with role and avatar fields
CREATE TABLE IF NOT EXISTS `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `username` varchar(50) NOT NULL,
    `password` varchar(255) NOT NULL,
    `email` varchar(100) NOT NULL,
    `role` ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    `avatar_path` varchar(255) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessions table for JWT blacklisting
CREATE TABLE IF NOT EXISTS `revoked_tokens` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `jti` varchar(36) NOT NULL,
    `revoked_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `jti` (`jti`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin user (password: admin123)
INSERT INTO `users` (`username`, `password`, `email`, `role`) 
VALUES ('admin', 'f865b53623b121fd34ee5426c792e5c33af8c227', 'admin@system.local', 'admin');