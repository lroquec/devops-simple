CREATE DATABASE IF NOT EXISTS `pythonlogin`;
USE `pythonlogin`;

CREATE TABLE IF NOT EXISTS `accounts` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `username` varchar(50) NOT NULL,
    `password` varchar(255) NOT NULL,
    `email` varchar(100) NOT NULL,
    `role` ENUM('admin', 'user') DEFAULT 'user',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Insert default admin user
INSERT INTO `accounts` (`username`, `password`, `email`, `role`) 
VALUES ('admin', SHA1('adminpassword'), 'admin@example.com', 'admin');
