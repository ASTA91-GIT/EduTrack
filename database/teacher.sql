-- EduTrack Teacher Dashboard Database
-- Created for the teacher dashboard system

CREATE DATABASE IF NOT EXISTS edutrack_teacher_db;
USE edutrack_teacher_db;

-- Users table (from authentication system)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'teacher',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    profile_image VARCHAR(255) DEFAULT 'default-profile.png',
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Teachers table (extended profile information)
CREATE TABLE teachers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100),
    designation VARCHAR(100),
    qualification VARCHAR(100),
    specialization VARCHAR(100),
    date_of_joining DATE,
    contact_number VARCHAR(15),
    office_room VARCHAR(20),
    office_hours TEXT,
    bio TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_employee_id (employee_id),
    INDEX idx_department (department)
);

-- Teacher subjects (what subjects a teacher teaches)
CREATE TABLE teacher_subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    subject_id INT NOT NULL,
    academic_year YEAR,
    semester ENUM('1', '2', '3', '4', '5', '6', '7', '8') DEFAULT '1',
    is_active BOOLEAN DEFAULT TRUE,
    assigned_date DATE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(teacher_id, subject_id, academic_year, semester),
    INDEX idx_academic_year (academic_year)
);

-- Teacher classes (what classes a teacher handles)
CREATE TABLE teacher_classes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    branch_id INT,
    division_id INT,
    academic_year YEAR,
    responsibility ENUM('class_teacher', 'subject_teacher', 'coordinator') DEFAULT 'subject_teacher',
    is_active BOOLEAN DEFAULT TRUE,
    assigned_date DATE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE SET NULL,
    UNIQUE(teacher_id, branch_id, division_id, academic_year),
    INDEX idx_responsibility (responsibility)
);

-- Teacher attendance (tracking when teachers mark attendance)
CREATE TABLE teacher_attendance_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    marked_count INT DEFAULT 0,
    last_marked_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    UNIQUE(teacher_id, attendance_date),
    INDEX idx_attendance_date (attendance_date)
);

-- Teacher dashboard statistics (pre-calculated for performance)
CREATE TABLE teacher_dashboard_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    stat_date DATE NOT NULL,
    total_students INT DEFAULT 0,
    total_classes_today INT DEFAULT 0,
    attendance_marked_today INT DEFAULT 0,
    pending_assignments INT DEFAULT 0,
    upcoming_deadlines INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    UNIQUE(teacher_id, stat_date),
    INDEX idx_stat_date (stat_date)
);

-- Teacher profile settings
CREATE TABLE teacher_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    theme ENUM('light', 'dark') DEFAULT 'light',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    dashboard_layout JSON,
    preferred_subjects JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    UNIQUE(teacher_id)
);

-- Insert sample data

-- Sample teacher user
INSERT INTO users (username, email, password_hash, full_name, role, profile_image) VALUES
('teacher1', 'john.teacher@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'John Smith', 'teacher', 'teacher-profile-1.png'),
('teacher2', 'sarah.wilson@edutrack.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'Sarah Wilson', 'teacher', 'teacher-profile-2.png');

-- Sample teacher profiles
INSERT INTO teachers (user_id, employee_id, department, designation, qualification, specialization, date_of_joining, contact_number) VALUES
(1, 'TECH001', 'Computer Science', 'Assistant Professor', 'M.Tech in Computer Science', 'Database Systems', '2020-06-15', '+1234567890'),
(2, 'TECH002', 'Mathematics', 'Professor', 'Ph.D in Mathematics', 'Advanced Calculus', '2018-03-10', '+1987654321');

-- Sample teacher subjects
INSERT INTO teacher_subjects (teacher_id, subject_id, academic_year, semester) VALUES
(1, 1, 2024, '1'),  -- John teaches Mathematics
(1, 3, 2024, '1'),  -- John teaches Programming
(2, 1, 2024, '1'),  -- Sarah teaches Mathematics
(2, 2, 2024, '1');  -- Sarah teaches Physics

-- Sample teacher classes
INSERT INTO teacher_classes (teacher_id, branch_id, division_id, academic_year, responsibility) VALUES
(1, 1, 1, 2024, 'class_teacher'),   -- John is class teacher for CS FY-A
(1, 1, 2, 2024, 'subject_teacher'), -- John teaches CS FY-B
(2, 1, 1, 2024, 'subject_teacher'), -- Sarah teaches CS FY-A
(2, 2, 1, 2024, 'class_teacher');   -- Sarah is class teacher for IT FY-A

-- Sample teacher attendance log
INSERT INTO teacher_attendance_log (teacher_id, attendance_date, marked_count, last_marked_at) VALUES
(1, CURDATE(), 3, NOW()),
(2, CURDATE(), 2, NOW());

-- Sample dashboard statistics
INSERT INTO teacher_dashboard_stats (teacher_id, stat_date, total_students, total_classes_today, attendance_marked_today, pending_assignments, upcoming_deadlines) VALUES
(1, CURDATE(), 45, 3, 3, 2, 1),
(2, CURDATE(), 30, 2, 2, 1, 0);

-- Sample teacher settings
INSERT INTO teacher_settings (teacher_id, theme, notifications_enabled, email_notifications) VALUES
(1, 'light', TRUE, TRUE),
(2, 'dark', TRUE, FALSE);

-- Views for teacher dashboard

-- Teacher profile view
CREATE VIEW teacher_profiles AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    u.full_name,
    u.profile_image,
    u.last_login,
    t.employee_id,
    t.department,
    t.designation,
    t.qualification,
    t.specialization,
    t.date_of_joining,
    t.contact_number,
    t.office_room,
    t.office_hours,
    t.bio
FROM users u
JOIN teachers t ON u.id = t.user_id
WHERE u.role = 'teacher' AND u.is_active = TRUE AND t.is_active = TRUE;

-- Teacher subjects view
CREATE VIEW teacher_subject_details AS
SELECT 
    t.id as teacher_id,
    u.full_name as teacher_name,
    s.subject_code,
    s.subject_name,
    ts.academic_year,
    ts.semester,
    ts.assigned_date
FROM teachers t
JOIN users u ON t.user_id = u.id
JOIN teacher_subjects ts ON t.id = ts.teacher_id
JOIN subjects s ON ts.subject_id = s.id
WHERE ts.is_active = TRUE;

-- Teacher class responsibilities view
CREATE VIEW teacher_class_responsibilities AS
SELECT 
    t.id as teacher_id,
    u.full_name as teacher_name,
    b.name as branch_name,
    d.name as division_name,
    tc.academic_year,
    tc.responsibility,
    tc.assigned_date
FROM teachers t
JOIN users u ON t.user_id = u.id
JOIN teacher_classes tc ON t.id = tc.teacher_id
JOIN branches b ON tc.branch_id = b.id
JOIN divisions d ON tc.division_id = d.id
WHERE tc.is_active = TRUE;

-- Teacher dashboard statistics view
CREATE VIEW teacher_dashboard_view AS
SELECT 
    t.id as teacher_id,
    u.full_name as teacher_name,
    tds.stat_date,
    tds.total_students,
    tds.total_classes_today,
    tds.attendance_marked_today,
    tds.pending_assignments,
    tds.upcoming_deadlines,
    tal.marked_count as today_attendance_marked
FROM teachers t
JOIN users u ON t.user_id = u.id
JOIN teacher_dashboard_stats tds ON t.id = tds.teacher_id
JOIN teacher_attendance_log tal ON t.id = tal.teacher_id AND tal.attendance_date = CURDATE()
WHERE tds.stat_date = CURDATE();

-- Stored procedures for teacher dashboard

-- Get teacher profile by user ID
DELIMITER //
CREATE PROCEDURE GetTeacherProfile(IN p_user_id INT)
BEGIN
    SELECT * FROM teacher_profiles WHERE user_id = p_user_id;
END //
DELIMITER ;

-- Update teacher profile
DELIMITER //
CREATE PROCEDURE UpdateTeacherProfile(
    IN p_user_id INT,
    IN p_full_name VARCHAR(100),
    IN p_email VARCHAR(150),
    IN p_department VARCHAR(100),
    IN p_designation VARCHAR(100),
    IN p_contact_number VARCHAR(15),
    IN p_bio TEXT
)
BEGIN
    UPDATE users u
    JOIN teachers t ON u.id = t.user_id
    SET 
        u.full_name = p_full_name,
        u.email = p_email,
        t.department = p_department,
        t.designation = p_designation,
        t.contact_number = p_contact_number,
        t.bio = p_bio,
        t.updated_at = CURRENT_TIMESTAMP
    WHERE u.id = p_user_id;
END //
DELIMITER ;

-- Update teacher password
DELIMITER //
CREATE PROCEDURE UpdateTeacherPassword(
    IN p_user_id INT,
    IN p_password_hash VARCHAR(255)
)
BEGIN
    UPDATE users 
    SET password_hash = p_password_hash
    WHERE id = p_user_id;
END //
DELIMITER ;

-- Update teacher profile image
DELIMITER //
CREATE PROCEDURE UpdateTeacherProfileImage(
    IN p_user_id INT,
    IN p_profile_image VARCHAR(255)
)
BEGIN
    UPDATE users 
    SET profile_image = p_profile_image
    WHERE id = p_user_id;
END //
DELIMITER ;

-- Get teacher dashboard statistics
DELIMITER //
CREATE PROCEDURE GetTeacherDashboardStats(IN p_teacher_id INT)
BEGIN
    SELECT * FROM teacher_dashboard_view WHERE teacher_id = p_teacher_id;
END //
DELIMITER ;

-- Update teacher settings
DELIMITER //
CREATE PROCEDURE UpdateTeacherSettings(
    IN p_teacher_id INT,
    IN p_theme ENUM('light', 'dark'),
    IN p_notifications_enabled BOOLEAN,
    IN p_email_notifications BOOLEAN
)
BEGIN
    INSERT INTO teacher_settings (teacher_id, theme, notifications_enabled, email_notifications)
    VALUES (p_teacher_id, p_theme, p_notifications_enabled, p_email_notifications)
    ON DUPLICATE KEY UPDATE
        theme = p_theme,
        notifications_enabled = p_notifications_enabled,
        email_notifications = p_email_notifications,
        updated_at = CURRENT_TIMESTAMP;
END //
DELIMITER ;

-- Teacher login tracking
DELIMITER //
CREATE PROCEDURE TrackTeacherLogin(IN p_user_id INT)
BEGIN
    UPDATE users 
    SET last_login = CURRENT_TIMESTAMP
    WHERE id = p_user_id;
END //
DELIMITER ;