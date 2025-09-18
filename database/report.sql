-- EduTrack Reports Database
-- Created for the reporting and analytics system

CREATE DATABASE IF NOT EXISTS edutrack_reports_db;
USE edutrack_reports_db;

-- Tables from previous systems (already created in other databases)
-- These would typically be in a single database, but shown here for reference

-- Assuming we have these tables from previous setups:
-- branches, divisions, subjects, students, attendance

-- For reporting purposes, let's create some additional tables and views

-- Attendance summary view for reporting
CREATE VIEW attendance_summary AS
SELECT 
    a.student_id,
    s.roll_no,
    s.name AS student_name,
    b.name AS branch_name,
    d.name AS division_name,
    sub.name AS subject_name,
    a.attendance_date,
    a.status,
    a.marked_at
FROM attendance a
JOIN students s ON a.student_id = s.id
JOIN branches b ON s.branch_id = b.id
JOIN divisions d ON s.division_id = d.id
JOIN subjects sub ON a.subject_id = sub.id;

-- Monthly attendance summary
CREATE VIEW monthly_attendance_summary AS
SELECT 
    student_id,
    roll_no,
    student_name,
    branch_name,
    division_name,
    subject_name,
    YEAR(attendance_date) AS year,
    MONTH(attendance_date) AS month,
    COUNT(*) AS total_classes,
    SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) AS absent_count,
    ROUND((SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS attendance_percentage
FROM attendance_summary
GROUP BY student_id, roll_no, student_name, branch_name, division_name, subject_name, YEAR(attendance_date), MONTH(attendance_date);

-- Create a stored procedure for generating reports
DELIMITER //

CREATE PROCEDURE GenerateAttendanceReport(
    IN p_branch_id INT,
    IN p_division_id INT,
    IN p_subject_id INT,
    IN p_from_date DATE,
    IN p_to_date DATE
)
BEGIN
    SELECT 
        s.roll_no,
        s.name AS student_name,
        COUNT(a.id) AS total_classes,
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_count,
        SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_count,
        ROUND((SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) / COUNT(a.id)) * 100, 2) AS attendance_percentage
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id 
        AND a.subject_id = p_subject_id 
        AND a.attendance_date BETWEEN p_from_date AND p_to_date
    WHERE s.branch_id = p_branch_id AND s.division_id = p_division_id
    GROUP BY s.id, s.roll_no, s.name
    ORDER BY s.roll_no;
END //

DELIMITER ;

-- Create a procedure for overall analytics
DELIMITER //

CREATE PROCEDURE GetOverallAnalytics(
    IN p_branch_id INT,
    IN p_division_id INT,
    IN p_subject_id INT,
    IN p_from_date DATE,
    IN p_to_date DATE
)
BEGIN
    -- Overall attendance statistics
    SELECT 
        COUNT(DISTINCT s.id) AS total_students,
        COUNT(a.id) AS total_classes,
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS total_present,
        SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS total_absent,
        ROUND((SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) / COUNT(a.id)) * 100, 2) AS overall_percentage,
        MIN(attendance_date) AS first_date,
        MAX(attendance_date) AS last_date
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id 
        AND a.subject_id = p_subject_id 
        AND a.attendance_date BETWEEN p_from_date AND p_to_date
    WHERE s.branch_id = p_branch_id AND s.division_id = p_division_id;
END //

DELIMITER ;

-- Create a procedure for daily attendance trend
DELIMITER //

CREATE PROCEDURE GetDailyAttendanceTrend(
    IN p_branch_id INT,
    IN p_division_id INT,
    IN p_subject_id INT,
    IN p_from_date DATE,
    IN p_to_date DATE
)
BEGIN
    SELECT 
        attendance_date,
        COUNT(*) AS total_students,
        SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) AS present_count,
        ROUND((SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS daily_percentage
    FROM attendance a
    JOIN students s ON a.student_id = s.id
    WHERE s.branch_id = p_branch_id 
        AND s.division_id = p_division_id
        AND a.subject_id = p_subject_id
        AND a.attendance_date BETWEEN p_from_date AND p_to_date
    GROUP BY attendance_date
    ORDER BY attendance_date;
END //

DELIMITER ;

-- Create a table for storing generated reports
CREATE TABLE generated_reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_name VARCHAR(255) NOT NULL,
    branch_id INT,
    division_id INT,
    subject_id INT,
    from_date DATE,
    to_date DATE,
    generated_by INT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parameters JSON,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (division_id) REFERENCES divisions(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (generated_by) REFERENCES users(id)
);

-- Insert sample attendance data for reporting
-- Assuming we have students with IDs 1-7 from previous examples

INSERT INTO attendance (student_id, subject_id, attendance_date, status, marked_by) VALUES
-- October 2023 attendance data for CS students in Mathematics
(1, 1, '2023-10-01', 'present', 1),
(2, 1, '2023-10-01', 'present', 1),
(3, 1, '2023-10-01', 'absent', 1),
(4, 1, '2023-10-01', 'present', 1),
(5, 1, '2023-10-01', 'present', 1),

(1, 1, '2023-10-02', 'present', 1),
(2, 1, '2023-10-02', 'absent', 1),
(3, 1, '2023-10-02', 'present', 1),
(4, 1, '2023-10-02', 'present', 1),
(5, 1, '2023-10-02', 'absent', 1),

(1, 1, '2023-10-03', 'present', 1),
(2, 1, '2023-10-03', 'present', 1),
(3, 1, '2023-10-03', 'present', 1),
(4, 1, '2023-10-03', 'absent', 1),
(5, 1, '2023-10-03', 'present', 1),

(1, 1, '2023-10-04', 'present', 1),
(2, 1, '2023-10-04', 'present', 1),
(3, 1, '2023-10-04', 'absent', 1),
(4, 1, '2023-10-04', 'present', 1),
(5, 1, '2023-10-04', 'present', 1),

(1, 1, '2023-10-05', 'absent', 1),
(2, 1, '2023-10-05', 'present', 1),
(3, 1, '2023-10-05', 'present', 1),
(4, 1, '2023-10-05', 'present', 1),
(5, 1, '2023-10-05', 'absent', 1);

-- Create a view for report-ready data
CREATE VIEW report_ready_data AS
SELECT 
    b.name AS branch_name,
    d.name AS division_name,
    sub.name AS subject_name,
    s.roll_no,
    s.name AS student_name,
    a.attendance_date,
    a.status,
    CASE WHEN a.status = 'present' THEN 1 ELSE 0 END AS present_numeric,
    CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END AS absent_numeric
FROM students s
JOIN branches b ON s.branch_id = b.id
JOIN divisions d ON s.division_id = d.id
JOIN attendance a ON s.id = a.student_id
JOIN subjects sub ON a.subject_id = sub.id;

-- Create index for better report performance
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_attendance_student_subject ON attendance(student_id, subject_id);
CREATE INDEX idx_student_branch_division ON students(branch_id, division_id);

-- Function to calculate attendance percentage
DELIMITER //

CREATE FUNCTION CalculateAttendancePercentage(
    p_student_id INT,
    p_subject_id INT,
    p_from_date DATE,
    p_to_date DATE
) RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_classes INT;
    DECLARE present_count INT;
    DECLARE percentage DECIMAL(5,2);
    
    SELECT COUNT(*) INTO total_classes
    FROM attendance
    WHERE student_id = p_student_id
    AND subject_id = p_subject_id
    AND attendance_date BETWEEN p_from_date AND p_to_date;
    
    SELECT COUNT(*) INTO present_count
    FROM attendance
    WHERE student_id = p_student_id
    AND subject_id = p_subject_id
    AND status = 'present'
    AND attendance_date BETWEEN p_from_date AND p_to_date;
    
    IF total_classes > 0 THEN
        SET percentage = (present_count / total_classes) * 100;
    ELSE
        SET percentage = 0;
    END IF;
    
    RETURN percentage;
END //

DELIMITER ;