CREATE DATABASE IF NOT EXISTS `microservices` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `microservices`;

CREATE TABLE IF NOT EXISTS `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `username` varchar(80) NOT NULL,
    `password` varchar(120) NOT NULL,
    `email` varchar(120) NOT NULL,
    `role` ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Insert default admin user (password: admin123)
INSERT INTO `users` (`username`, `password`, `email`, `role`) 
VALUES ('admin', 'f865b53623b121fd34ee5426c792e5c33af8c227', 'admin@system.local', 'admin');