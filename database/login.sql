-- EduTrack Authentication Database
-- Created for the login and registration system

CREATE DATABASE IF NOT EXISTS edutrack_auth_db;
USE edutrack_auth_db;

-- Table for storing user information
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('teacher', 'student', 'admin') NOT NULL,
    institutional_email VARCHAR(150) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Table for storing password reset tokens
CREATE TABLE password_reset_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token)
);

-- Table for storing email verification tokens
CREATE TABLE verification_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token)
);

-- Table for tracking login attempts (for security)
CREATE TABLE login_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(150) NOT NULL,
    ip_address VARCHAR(45),
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_attempted_at (attempted_at)
);

-- Insert sample users
-- Note: Passwords are hashed with bcrypt (cost factor 10)
-- Default password for all sample users: "Password123!"

-- Sample teacher
INSERT INTO users (full_name, email, password_hash, role, institutional_email, is_verified) VALUES
('John Smith', 'john.smith@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'teacher', 'jsmith@institution.edu', TRUE);

-- Sample student
INSERT INTO users (full_name, email, password_hash, role, institutional_email, is_verified) VALUES
('Emma Johnson', 'emma.johnson@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'student', 'ejohnson@student.institution.edu', TRUE);

-- Sample admin
INSERT INTO users (full_name, email, password_hash, role, institutional_email, is_verified) VALUES
('Admin User', 'admin@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'admin', 'admin@institution.edu', TRUE);

-- Additional sample teachers
INSERT INTO users (full_name, email, password_hash, role, institutional_email, is_verified) VALUES
('Sarah Wilson', 'sarah.wilson@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'teacher', 'swilson@institution.edu', TRUE),
('Michael Brown', 'michael.brown@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'teacher', 'mbrown@institution.edu', TRUE);

-- Additional sample students
INSERT INTO users (full_name, email, password_hash, role, institutional_email, is_verified) VALUES
('David Lee', 'david.lee@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'student', 'dlee@student.institution.edu', TRUE),
('Sophia Garcia', 'sophia.garcia@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'student', 'sgarcia@student.institution.edu', TRUE);

-- Create a view for active users
CREATE VIEW active_users AS
SELECT id, full_name, email, role, institutional_email, created_at, last_login
FROM users
WHERE is_active = TRUE AND is_verified = TRUE;

-- Create a procedure for user registration
DELIMITER //
CREATE PROCEDURE RegisterUser(
    IN p_full_name VARCHAR(100),
    IN p_email VARCHAR(150),
    IN p_password_hash VARCHAR(255),
    IN p_role ENUM('teacher', 'student', 'admin'),
    IN p_institutional_email VARCHAR(150)
)
BEGIN
    INSERT INTO users (full_name, email, password_hash, role, institutional_email)
    VALUES (p_full_name, p_email, p_password_hash, p_role, p_institutional_email);
    
    SELECT LAST_INSERT_ID() as user_id;
END //
DELIMITER ;

-- Create a procedure for updating last login
DELIMITER //
CREATE PROCEDURE UpdateLastLogin(IN p_user_id INT)
BEGIN
    UPDATE users 
    SET last_login = CURRENT_TIMESTAMP 
    WHERE id = p_user_id;
END //
DELIMITER ;

-- Create a trigger to add institutional email if not provided
DELIMITER //
CREATE TRIGGER before_user_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.institutional_email IS NULL THEN
        SET NEW.institutional_email = NEW.email;
    END IF;
END //
DELIMITER ;