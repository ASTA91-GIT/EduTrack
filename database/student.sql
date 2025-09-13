-- EduTrack Student Dashboard Database
-- Created for the student dashboard system

CREATE DATABASE IF NOT EXISTS edutrack_student_db;
USE edutrack_student_db;

-- Users table (from authentication system)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student',
    student_id INT UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Students table (linked to users)
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    branch_id INT,
    division_id INT,
    enrollment_date DATE,
    date_of_birth DATE,
    contact_number VARCHAR(15),
    address TEXT,
    guardian_name VARCHAR(100),
    guardian_contact VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE SET NULL,
    INDEX idx_roll_no (roll_no)
);

-- Subjects table
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_code VARCHAR(20) UNIQUE NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    credits INT DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance table
CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'excused') DEFAULT 'absent',
    marked_by INT,
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, subject_id, attendance_date),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_attendance_date (attendance_date)
);

-- Grades table
CREATE TABLE grades (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    assignment_type ENUM('exam', 'quiz', 'assignment', 'project', 'participation') NOT NULL,
    title VARCHAR(100) NOT NULL,
    maximum_marks DECIMAL(5,2) NOT NULL,
    obtained_marks DECIMAL(5,2) NOT NULL,
    percentage DECIMAL(5,2) GENERATED ALWAYS AS ((obtained_marks / maximum_marks) * 100) STORED,
    grade CHAR(2),
    feedback TEXT,
    graded_by INT,
    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_assignment_type (assignment_type)
);

-- Assignments table
CREATE TABLE assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    assignment_type ENUM('exam', 'quiz', 'assignment', 'project') NOT NULL,
    maximum_marks DECIMAL(5,2) NOT NULL,
    due_date DATETIME NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_due_date (due_date)
);

-- Student assignments (submissions)
CREATE TABLE student_assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    submitted_at TIMESTAMP NULL,
    file_path VARCHAR(255),
    status ENUM('not_started', 'in_progress', 'submitted', 'graded') DEFAULT 'not_started',
    obtained_marks DECIMAL(5,2) NULL,
    feedback TEXT,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(assignment_id, student_id),
    INDEX idx_status (status)
);

-- Schedule table
CREATE TABLE schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_id INT NOT NULL,
    branch_id INT,
    division_id INT,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE,
    INDEX idx_day_time (day_of_week, start_time)
);

-- Insert sample data

-- Sample users (students)
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('student1', 'john.smith@student.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'John Smith', 'student'),
('student2', 'emma.johnson@student.edu', '$2b$10$KssILxWNR6k62B7yiX0GAe2Q7wwHlrzhF3LqtVvpyvHZf0Mw2N3VO', 'Emma Johnson', 'student');

-- Sample students
INSERT INTO students (user_id, roll_no, branch_id, division_id, enrollment_date) VALUES
(1, 'CS001', 1, 1, '2023-09-01'),
(2, 'CS002', 1, 1, '2023-09-01');

-- Sample subjects
INSERT INTO subjects (subject_code, subject_name, credits) VALUES
('MATH101', 'Mathematics I', 4),
('PHY102', 'Physics II', 4),
('PROG201', 'Programming Fundamentals', 3),
('DBMS301', 'Database Management Systems', 3);

-- Sample attendance records for student 1
INSERT INTO attendance (student_id, subject_id, attendance_date, status, marked_by) VALUES
(1, 1, '2024-01-15', 'present', 3),
(1, 2, '2024-01-15', 'present', 3),
(1, 3, '2024-01-15', 'late', 3),
(1, 1, '2024-01-16', 'present', 3),
(1, 2, '2024-01-16', 'absent', 3),
(1, 3, '2024-01-16', 'present', 3);

-- Sample grades for student 1
INSERT INTO grades (student_id, subject_id, assignment_type, title, maximum_marks, obtained_marks, grade, graded_by) VALUES
(1, 1, 'exam', 'Midterm Exam', 100, 85, 'A', 3),
(1, 1, 'quiz', 'Quiz 1', 20, 18, 'A', 3),
(1, 2, 'assignment', 'Physics Lab 1', 30, 27, 'B', 3),
(1, 3, 'project', 'Programming Project', 50, 45, 'A', 3);

-- Sample assignments
INSERT INTO assignments (subject_id, title, description, assignment_type, maximum_marks, due_date, created_by) VALUES
(1, 'Calculus Homework', 'Complete exercises 1-10 from chapter 5', 'assignment', 20, '2024-01-20 23:59:00', 3),
(2, 'Physics Lab Report', 'Write lab report for experiment 3', 'assignment', 30, '2024-01-22 17:00:00', 3),
(3, 'Programming Assignment', 'Implement sorting algorithms', 'project', 50, '2024-01-25 23:59:00', 3),
(4, 'Database Design', 'Design ER diagram for library system', 'assignment', 25, '2024-01-18 23:59:00', 3);

-- Sample student assignments
INSERT INTO student_assignments (assignment_id, student_id, status) VALUES
(1, 1, 'not_started'),
(2, 1, 'in_progress'),
(3, 1, 'submitted'),
(4, 1, 'graded');

-- Sample schedule
INSERT INTO schedule (subject_id, branch_id, division_id, day_of_week, start_time, end_time, room_number) VALUES
(1, 1, 1, 'Monday', '09:00:00', '10:30:00', 'Room 101'),
(2, 1, 1, 'Monday', '11:00:00', '12:30:00', 'Lab 201'),
(3, 1, 1, 'Monday', '14:00:00', '15:30:00', 'Room 102'),
(1, 1, 1, 'Wednesday', '09:00:00', '10:30:00', 'Room 101'),
(2, 1, 1, 'Wednesday', '11:00:00', '12:30:00', 'Lab 201'),
(4, 1, 1, 'Wednesday', '14:00:00', '15:30:00', 'Room 103');

-- Views for student dashboard

-- Student attendance summary view
CREATE VIEW student_attendance_summary AS
SELECT 
    s.id AS student_id,
    s.roll_no,
    u.full_name,
    sub.subject_name,
    COUNT(a.id) AS total_classes,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) AS late_count,
    ROUND((SUM(CASE WHEN a.status IN ('present', 'late') THEN 1 ELSE 0 END) / COUNT(a.id)) * 100, 2) AS attendance_percentage
FROM students s
JOIN users u ON s.user_id = u.id
JOIN attendance a ON s.id = a.student_id
JOIN subjects sub ON a.subject_id = sub.id
GROUP BY s.id, s.roll_no, u.full_name, sub.subject_name;

-- Student grades summary view
CREATE VIEW student_grades_summary AS
SELECT 
    s.id AS student_id,
    s.roll_no,
    u.full_name,
    sub.subject_name,
    g.assignment_type,
    g.title,
    g.maximum_marks,
    g.obtained_marks,
    g.percentage,
    g.grade,
    g.graded_at
FROM students s
JOIN users u ON s.user_id = u.id
JOIN grades g ON s.id = g.student_id
JOIN subjects sub ON g.subject_id = sub.id;

-- Upcoming assignments view
CREATE VIEW student_upcoming_assignments AS
SELECT 
    s.id AS student_id,
    a.id AS assignment_id,
    sub.subject_name,
    a.title,
    a.description,
    a.assignment_type,
    a.maximum_marks,
    a.due_date,
    sa.status,
    DATEDIFF(a.due_date, NOW()) AS days_remaining
FROM students s
JOIN student_assignments sa ON s.id = sa.student_id
JOIN assignments a ON sa.assignment_id = a.id
JOIN subjects sub ON a.subject_id = sub.id
WHERE a.due_date > NOW()
ORDER BY a.due_date;

-- Today's schedule view
CREATE VIEW student_todays_schedule AS
SELECT 
    s.id AS student_id,
    sch.day_of_week,
    sub.subject_name,
    sch.start_time,
    sch.end_time,
    sch.room_number
FROM students s
JOIN schedule sch ON s.branch_id = sch.branch_id AND s.division_id = sch.division_id
JOIN subjects sub ON sch.subject_id = sub.id
WHERE sch.day_of_week = DAYNAME(CURDATE())
ORDER BY sch.start_time;

-- Stored procedures for student dashboard

-- Get student attendance percentage
DELIMITER //
CREATE PROCEDURE GetStudentAttendancePercentage(IN p_student_id INT)
BEGIN
    SELECT 
        attendance_percentage
    FROM student_attendance_summary
    WHERE student_id = p_student_id
    LIMIT 1;
END //
DELIMITER ;

-- Get student grades
DELIMITER //
CREATE PROCEDURE GetStudentGrades(IN p_student_id INT)
BEGIN
    SELECT 
        subject_name,
        assignment_type,
        title,
        maximum_marks,
        obtained_marks,
        percentage,
        grade,
        graded_at
    FROM student_grades_summary
    WHERE student_id = p_student_id
    ORDER BY graded_at DESC;
END //
DELIMITER ;

-- Get student upcoming assignments
DELIMITER //
CREATE PROCEDURE GetStudentUpcomingAssignments(IN p_student_id INT)
BEGIN
    SELECT 
        subject_name,
        title,
        assignment_type,
        maximum_marks,
        due_date,
        status,
        days_remaining
    FROM student_upcoming_assignments
    WHERE student_id = p_student_id
    ORDER BY due_date
    LIMIT 5;
END //
DELIMITER ;

-- Get student today's schedule
DELIMITER //
CREATE PROCEDURE GetStudentTodaysSchedule(IN p_student_id INT)
BEGIN
    SELECT 
        subject_name,
        start_time,
        end_time,
        room_number
    FROM student_todays_schedule
    WHERE student_id = p_student_id
    ORDER BY start_time;
END //
DELIMITER ;