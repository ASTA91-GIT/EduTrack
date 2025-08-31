-- EduTrack Database Schema
-- Automated Student Attendance Monitoring & Analytics System

-- Create database
CREATE DATABASE IF NOT EXISTS edutrack_db;
USE edutrack_db;

-- Students table
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    roll_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    face_data LONGTEXT, -- Store face recognition data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Faculty table
CREATE TABLE faculty (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Classes table
CREATE TABLE classes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    faculty_id INT,
    department VARCHAR(50) NOT NULL,
    schedule_day VARCHAR(20) NOT NULL,
    schedule_time TIME NOT NULL,
    duration INT DEFAULT 60, -- in minutes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE SET NULL
);

-- Attendance table
CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    status ENUM('present', 'absent', 'late') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method ENUM('qr_code', 'face_recognition', 'manual', 'rfid') DEFAULT 'manual',
    location_data JSON, -- Store GPS coordinates if available
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, class_id, DATE(timestamp))
);

-- QR Codes table
CREATE TABLE qr_codes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_id INT NOT NULL,
    code_data VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Notifications table
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    user_type ENUM('student', 'faculty', 'admin') NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('attendance_alert', 'system', 'reminder') NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics cache table for performance
CREATE TABLE analytics_cache (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_data JSON NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO students (name, roll_number, email, department) VALUES
('John Doe', 'CS001', 'john.doe@college.edu', 'Computer Science'),
('Jane Smith', 'CS002', 'jane.smith@college.edu', 'Computer Science'),
('Mike Johnson', 'ME001', 'mike.johnson@college.edu', 'Mechanical Engineering'),
('Sarah Wilson', 'EE001', 'sarah.wilson@college.edu', 'Electrical Engineering');

INSERT INTO faculty (name, email, department, password_hash) VALUES
('Dr. Robert Brown', 'robert.brown@college.edu', 'Computer Science', '$2b$10$hashedpassword'),
('Prof. Lisa Davis', 'lisa.davis@college.edu', 'Mechanical Engineering', '$2b$10$hashedpassword'),
('Dr. James Miller', 'james.miller@college.edu', 'Electrical Engineering', '$2b$10$hashedpassword');

INSERT INTO classes (name, subject, faculty_id, department, schedule_day, schedule_time) VALUES
('CS101', 'Introduction to Programming', 1, 'Computer Science', 'Monday', '09:00:00'),
('CS102', 'Data Structures', 1, 'Computer Science', 'Tuesday', '10:00:00'),
('ME101', 'Engineering Mechanics', 2, 'Mechanical Engineering', 'Wednesday', '11:00:00'),
('EE101', 'Circuit Theory', 3, 'Electrical Engineering', 'Thursday', '14:00:00');

-- Create indexes for better performance
CREATE INDEX idx_attendance_student_date ON attendance(student_id, DATE(timestamp));
CREATE INDEX idx_attendance_class_date ON attendance(class_id, DATE(timestamp));
CREATE INDEX idx_students_department ON students(department);
CREATE INDEX idx_classes_faculty ON classes(faculty_id);
