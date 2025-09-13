-- EduTrack Student Management Database
-- Created for the student management system

CREATE DATABASE IF NOT EXISTS edutrack_student_db;
USE edutrack_student_db;

-- Table for storing branches
CREATE TABLE branches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_branch_name (name)
);

-- Table for storing divisions
CREATE TABLE divisions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    branch_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(branch_id, name),
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    INDEX idx_division_name (name)
);

-- Table for storing subjects
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_subject_name (name)
);

-- Junction table for subjects assigned to specific branch-division combinations
CREATE TABLE branch_division_subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    branch_id INT NOT NULL,
    division_id INT NOT NULL,
    subject_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(branch_id, division_id, subject_id),
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Table for storing students
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    roll_no VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    branch_id INT NOT NULL,
    division_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(roll_no, branch_id, division_id),
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE,
    INDEX idx_student_rollno (roll_no),
    INDEX idx_student_name (name)
);

-- Junction table for student-subject enrollment
CREATE TABLE student_subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Insert sample data

-- Sample branches
INSERT INTO branches (name, code) VALUES
('Computer Science', 'CS'),
('Information Technology', 'IT'),
('Mechanical Engineering', 'ME'),
('Electrical Engineering', 'EE');

-- Sample divisions for Computer Science
INSERT INTO divisions (branch_id, name, code) VALUES
(1, 'FY-A', 'CS-FYA'),
(1, 'FY-B', 'CS-FYB'),
(1, 'SY-A', 'CS-SYA'),
(1, 'SY-B', 'CS-SYB'),
(1, 'TY-A', 'CS-TYA');

-- Sample divisions for Information Technology
INSERT INTO divisions (branch_id, name, code) VALUES
(2, 'FY-A', 'IT-FYA'),
(2, 'FY-B', 'IT-FYB'),
(2, 'SY-A', 'IT-SYA');

-- Sample subjects
INSERT INTO subjects (name, code) VALUES
('Mathematics', 'MATH101'),
('Physics', 'PHY102'),
('Programming Fundamentals', 'PROG201'),
('Database Management Systems', 'DBMS301'),
('Web Development', 'WEB401'),
('Data Structures', 'DS301'),
('Algorithms', 'ALGO401');

-- Assign subjects to Computer Science FY-A
INSERT INTO branch_division_subjects (branch_id, division_id, subject_id) VALUES
(1, 1, 1), -- CS, FY-A, Mathematics
(1, 1, 2), -- CS, FY-A, Physics
(1, 1, 3), -- CS, FY-A, Programming Fundamentals
(1, 1, 4); -- CS, FY-A, Database Management Systems

-- Assign subjects to Computer Science FY-B
INSERT INTO branch_division_subjects (branch_id, division_id, subject_id) VALUES
(1, 2, 1), -- CS, FY-B, Mathematics
(1, 2, 2), -- CS, FY-B, Physics
(1, 2, 3), -- CS, FY-B, Programming Fundamentals
(1, 2, 4); -- CS, FY-B, Database Management Systems

-- Sample students
INSERT INTO students (roll_no, name, branch_id, division_id) VALUES
('CS001', 'John Smith', 1, 1),
('CS002', 'Jane Doe', 1, 1),
('CS003', 'Robert Johnson', 1, 1),
('CS004', 'Emily Davis', 1, 2),
('CS005', 'Michael Wilson', 1, 2),
('IT001', 'Sarah Brown', 2, 6),
('IT002', 'David Lee', 2, 6);

-- Enroll students in subjects
INSERT INTO student_subjects (student_id, subject_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), -- John Smith enrolled in all subjects
(2, 1), (2, 3),                   -- Jane Doe enrolled in Math and Programming
(3, 2), (3, 4),                   -- Robert Johnson enrolled in Physics and DBMS
(4, 1), (4, 2), (4, 3),           -- Emily Davis enrolled in Math, Physics, Programming
(5, 1), (5, 4);                   -- Michael Wilson enrolled in Math and DBMS

-- Create views for easier data retrieval

-- View for students with branch and division information
CREATE VIEW student_details AS
SELECT 
    s.id,
    s.roll_no,
    s.name AS student_name,
    b.name AS branch_name,
    d.name AS division_name,
    s.created_at
FROM students s
JOIN branches b ON s.branch_id = b.id
JOIN divisions d ON s.division_id = d.id
WHERE s.is_active = TRUE;

-- View for subjects available by branch and division
CREATE VIEW branch_division_subject_details AS
SELECT 
    b.name AS branch_name,
    d.name AS division_name,
    s.name AS subject_name,
    s.code AS subject_code,
    bds.created_at
FROM branch_division_subjects bds
JOIN branches b ON bds.branch_id = b.id
JOIN divisions d ON bds.division_id = d.id
JOIN subjects s ON bds.subject_id = s.id;

-- View for student enrollments
CREATE VIEW student_enrollments AS
SELECT 
    s.roll_no,
    s.name AS student_name,
    b.name AS branch_name,
    d.name AS division_name,
    sub.name AS subject_name,
    ss.enrolled_at
FROM student_subjects ss
JOIN students s ON ss.student_id = s.id
JOIN subjects sub ON ss.subject_id = sub.id
JOIN branches b ON s.branch_id = b.id
JOIN divisions d ON s.division_id = d.id;

-- Create stored procedures for common operations

-- Procedure to add a new student
DELIMITER //
CREATE PROCEDURE AddStudent(
    IN p_roll_no VARCHAR(50),
    IN p_name VARCHAR(100),
    IN p_branch_id INT,
    IN p_division_id INT
)
BEGIN
    INSERT INTO students (roll_no, name, branch_id, division_id)
    VALUES (p_roll_no, p_name, p_branch_id, p_division_id);
    
    SELECT LAST_INSERT_ID() AS student_id;
END //
DELIMITER ;

-- Procedure to get subjects by branch and division
DELIMITER //
CREATE PROCEDURE GetSubjectsByBranchDivision(
    IN p_branch_id INT,
    IN p_division_id INT
)
BEGIN
    SELECT s.id, s.name, s.code
    FROM branch_division_subjects bds
    JOIN subjects s ON bds.subject_id = s.id
    WHERE bds.branch_id = p_branch_id AND bds.division_id = p_division_id
    AND s.is_active = TRUE;
END //
DELIMITER ;