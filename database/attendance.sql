-- EduTrack Attendance Database
-- Created for the attendance tracking system

CREATE DATABASE IF NOT EXISTS edutrack_db;
USE edutrack_db;

-- Table for storing user information (teachers/attendance personnel)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'teacher', 'attendance') DEFAULT 'teacher',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing branch information
CREATE TABLE branches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    branch_code VARCHAR(10) UNIQUE NOT NULL,
    branch_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Table for storing division/class information
CREATE TABLE divisions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    division_code VARCHAR(10) UNIQUE NOT NULL,
    division_name VARCHAR(100) NOT NULL,
    branch_id INT,
    academic_year YEAR,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

-- Table for storing subjects
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_code VARCHAR(10) UNIQUE NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Table for storing students
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    roll_no VARCHAR(20) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    division_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(roll_no, division_id),
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE
);

-- Table for storing attendance records
CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent') DEFAULT 'absent',
    marked_by INT,  -- User who marked the attendance
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, subject_id, attendance_date),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert sample data

-- Insert sample branches
INSERT INTO branches (branch_code, branch_name) VALUES
('CS', 'Computer Science'),
('ME', 'Mechanical Engineering'),
('EE', 'Electrical Engineering');

-- Insert sample divisions
INSERT INTO divisions (division_code, division_name, branch_id, academic_year) VALUES
('CS-A', 'Computer Science A', 1, 2023),
('CS-B', 'Computer Science B', 1, 2023),
('ME-A', 'Mechanical A', 2, 2023);

-- Insert sample subjects
INSERT INTO subjects (subject_code, subject_name) VALUES
('MATH101', 'Mathematics I'),
('PHY102', 'Physics II'),
('PROG201', 'Programming Fundamentals'),
('DBMS301', 'Database Management Systems');

-- Insert sample students
INSERT INTO students (roll_no, full_name, division_id) VALUES
('CS001', 'John Smith', 1),
('CS002', 'Jane Doe', 1),
('CS003', 'Robert Johnson', 1),
('CS004', 'Emily Davis', 2),
('CS005', 'Michael Wilson', 2);

-- Insert sample user (password is "password123" hashed with bcrypt)
INSERT INTO users (username, password_hash, full_name, role) VALUES
('attendance_user', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'Attendance Officer', 'attendance');

-- Insert sample attendance records
INSERT INTO attendance (student_id, subject_id, attendance_date, status, marked_by) VALUES
(1, 1, '2023-10-01', 'present', 1),
(2, 1, '2023-10-01', 'present', 1),
(3, 1, '2023-10-01', 'absent', 1),
(1, 3, '2023-10-02', 'present', 1),
(2, 3, '2023-10-02', 'absent', 1);