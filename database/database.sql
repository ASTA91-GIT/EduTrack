-- --------------------------------------------------------
-- EduTrack Student Attendance System Database
-- --------------------------------------------------------

-- Create database
DROP DATABASE IF EXISTS `edutrack_db`;
CREATE DATABASE `edutrack_db`;
USE `edutrack_db`;

-- --------------------------------------------------------
-- Table structure for table `departments`
-- --------------------------------------------------------
CREATE TABLE `departments` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `code` VARCHAR(10) NOT NULL,
  `description` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_dept_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `programs`
-- --------------------------------------------------------
CREATE TABLE `programs` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `department_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `code` VARCHAR(10) NOT NULL,
  `duration_years` INT DEFAULT 4,
  `description` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_program_code` (`code`),
  KEY `fk_program_department` (`department_id`),
  CONSTRAINT `fk_program_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `students`
-- --------------------------------------------------------
CREATE TABLE `students` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `student_id` VARCHAR(20) NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(15),
  `program_id` INT UNSIGNED NOT NULL,
  `current_semester` INT DEFAULT 1,
  `academic_status` ENUM('active', 'inactive', 'suspended', 'graduated') DEFAULT 'active',
  `enrollment_date` DATE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_student_id` (`student_id`),
  UNIQUE KEY `unique_email` (`email`),
  KEY `fk_student_program` (`program_id`),
  CONSTRAINT `fk_student_program` FOREIGN KEY (`program_id`) REFERENCES `programs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `faculty`
-- --------------------------------------------------------
CREATE TABLE `faculty` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `faculty_id` VARCHAR(20) NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(15),
  `department_id` INT UNSIGNED NOT NULL,
  `designation` VARCHAR(50) NOT NULL,
  `employment_status` ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_faculty_id` (`faculty_id`),
  UNIQUE KEY `unique_faculty_email` (`email`),
  KEY `fk_faculty_department` (`department_id`),
  CONSTRAINT `fk_faculty_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `courses`
-- --------------------------------------------------------
CREATE TABLE `courses` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `course_code` VARCHAR(20) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `credits` INT DEFAULT 3,
  `program_id` INT UNSIGNED NOT NULL,
  `semester` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_course_code` (`course_code`),
  KEY `fk_course_program` (`program_id`),
  CONSTRAINT `fk_course_program` FOREIGN KEY (`program_id`) REFERENCES `programs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `sections`
-- --------------------------------------------------------
CREATE TABLE `sections` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `course_id` INT UNSIGNED NOT NULL,
  `section_code` VARCHAR(10) NOT NULL,
  `faculty_id` INT UNSIGNED NOT NULL,
  `max_students` INT DEFAULT 60,
  `current_enrollment` INT DEFAULT 0,
  `academic_term` VARCHAR(20) NOT NULL,
  `year` YEAR NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_section` (`course_id`, `section_code`, `academic_term`, `year`),
  KEY `fk_section_course` (`course_id`),
  KEY `fk_section_faculty` (`faculty_id`),
  CONSTRAINT `fk_section_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_section_faculty` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `enrollments`
-- --------------------------------------------------------
CREATE TABLE `enrollments` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `student_id` INT UNSIGNED NOT NULL,
  `section_id` INT UNSIGNED NOT NULL,
  `enrollment_date` DATE,
  `enrollment_status` ENUM('enrolled', 'dropped', 'completed') DEFAULT 'enrolled',
  `grade` VARCHAR(2) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_enrollment` (`student_id`, `section_id`),
  KEY `fk_enrollment_student` (`student_id`),
  KEY `fk_enrollment_section` (`section_id`),
  CONSTRAINT `fk_enrollment_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_enrollment_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `class_schedule`
-- --------------------------------------------------------
CREATE TABLE `class_schedule` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `section_id` INT UNSIGNED NOT NULL,
  `day_of_week` ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `room` VARCHAR(20),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_schedule_section` (`section_id`),
  CONSTRAINT `fk_schedule_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `attendance`
-- --------------------------------------------------------
CREATE TABLE `attendance` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `student_id` INT UNSIGNED NOT NULL,
  `section_id` INT UNSIGNED NOT NULL,
  `class_date` DATE NOT NULL,
  `status` ENUM('present', 'absent', 'late', 'excused') DEFAULT 'absent',
  `check_in_time` TIME NULL,
  `check_out_time` TIME NULL,
  `notes` TEXT,
  `recorded_by` INT UNSIGNED NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_attendance` (`student_id`, `section_id`, `class_date`),
  KEY `fk_attendance_student` (`student_id`),
  KEY `fk_attendance_section` (`section_id`),
  KEY `fk_attendance_faculty` (`recorded_by`),
  CONSTRAINT `fk_attendance_faculty` FOREIGN KEY (`recorded_by`) REFERENCES `faculty` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_attendance_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_attendance_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `attendance_summary`
-- --------------------------------------------------------
CREATE TABLE `attendance_summary` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `student_id` INT UNSIGNED NOT NULL,
  `section_id` INT UNSIGNED NOT NULL,
  `total_classes` INT DEFAULT 0,
  `classes_present` INT DEFAULT 0,
  `classes_absent` INT DEFAULT 0,
  `classes_late` INT DEFAULT 0,
  `attendance_percentage` DECIMAL(5,2) DEFAULT 0.00,
  `last_updated` DATE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_attendance_summary` (`student_id`, `section_id`),
  KEY `fk_summary_student` (`student_id`),
  KEY `fk_summary_section` (`section_id`),
  CONSTRAINT `fk_summary_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_summary_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `holidays`
-- --------------------------------------------------------
CREATE TABLE `holidays` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `holiday_date` DATE NOT NULL,
  `academic_term` VARCHAR(20) NOT NULL,
  `description` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_holiday` (`holiday_date`, `academic_term`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `users`
-- --------------------------------------------------------
CREATE TABLE `users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `user_type` ENUM('admin', 'faculty', 'student') NOT NULL,
  `reference_id` INT UNSIGNED NOT NULL COMMENT 'ID from students or faculty table',
  `is_active` BOOLEAN DEFAULT TRUE,
  `last_login` TIMESTAMP NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_username` (`username`),
  UNIQUE KEY `unique_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `system_settings`
-- --------------------------------------------------------
CREATE TABLE `system_settings` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `setting_key` VARCHAR(50) NOT NULL,
  `setting_value` TEXT NOT NULL,
  `description` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_setting_key` (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Insert sample data
-- --------------------------------------------------------

-- Insert departments
INSERT INTO `departments` (`name`, `code`, `description`) VALUES
('Computer Science', 'CS', 'Department of Computer Science'),
('Business Administration', 'BA', 'Department of Business Administration'),
('Mathematics', 'MATH', 'Department of Mathematics');

-- Insert programs
INSERT INTO `programs` (`department_id`, `name`, `code`, `duration_years`, `description`) VALUES
(1, 'Bachelor of Computer Science', 'BCS', 4, 'Undergraduate program in Computer Science'),
(1, 'Master of Computer Science', 'MCS', 2, 'Graduate program in Computer Science'),
(2, 'Bachelor of Business Administration', 'BBA', 4, 'Undergraduate program in Business Administration');

-- Insert students
INSERT INTO `students` (`student_id`, `first_name`, `last_name`, `email`, `phone`, `program_id`, `current_semester`, `academic_status`, `enrollment_date`) VALUES
('CS2021001', 'John', 'Davis', 'john.davis@edu.in', '9876543210', 1, 3, 'active', '2021-08-01'),
('CS2021002', 'Sarah', 'Wilson', 'sarah.wilson@edu.in', '9876543211', 1, 3, 'active', '2021-08-01'),
('CS2021003', 'Michael', 'Brown', 'michael.brown@edu.in', '9876543212', 1, 3, 'active', '2021-08-01'),
('CS2021004', 'Emily', 'Chen', 'emily.chen@edu.in', '9876543213', 1, 3, 'active', '2021-08-01'),
('BBA2021001', 'Robert', 'Johnson', 'robert.johnson@edu.in', '9876543214', 3, 3, 'active', '2021-08-01');

-- Insert faculty
INSERT INTO `faculty` (`faculty_id`, `first_name`, `last_name`, `email`, `phone`, `department_id`, `designation`, `employment_status`) VALUES
('FCS001', 'James', 'Smith', 'james.smith@edu.in', '9876550001', 1, 'Professor', 'active'),
('FCS002', 'Patricia', 'Johnson', 'patricia.johnson@edu.in', '9876550002', 1, 'Associate Professor', 'active'),
('FBA001', 'Robert', 'Williams', 'robert.williams@edu.in', '9876550003', 2, 'Assistant Professor', 'active');

-- Insert courses
INSERT INTO `courses` (`course_code`, `name`, `description`, `credits`, `program_id`, `semester`) VALUES
('CS301', 'Database Systems', 'Fundamentals of database design and management', 4, 1, 3),
('CS302', 'Software Engineering', 'Principles of software development', 4, 1, 3),
('CS303', 'Web Development', 'Building modern web applications', 3, 1, 3),
('BBA301', 'Marketing Principles', 'Introduction to marketing concepts', 4, 3, 3);

-- Insert sections
INSERT INTO `sections` (`course_id`, `section_code`, `faculty_id`, `max_students`, `current_enrollment`, `academic_term`, `year`) VALUES
(1, 'A', 1, 60, 4, 'Fall', 2023),
(1, 'B', 2, 60, 0, 'Fall', 2023),
(2, 'A', 1, 60, 4, 'Fall', 2023),
(3, 'A', 2, 60, 4, 'Fall', 2023),
(4, 'A', 3, 60, 1, 'Fall', 2023);

-- Insert enrollments
INSERT INTO `enrollments` (`student_id`, `section_id`, `enrollment_date`, `enrollment_status`) VALUES
(1, 1, '2023-08-15', 'enrolled'),
(2, 1, '2023-08-15', 'enrolled'),
(3, 1, '2023-08-15', 'enrolled'),
(4, 1, '2023-08-15', 'enrolled'),
(1, 3, '2023-08-15', 'enrolled'),
(2, 3, '2023-08-15', 'enrolled'),
(3, 3, '2023-08-15', 'enrolled'),
(4, 3, '2023-08-15', 'enrolled'),
(1, 4, '2023-08-15', 'enrolled'),
(2, 4, '2023-08-15', 'enrolled'),
(3, 4, '2023-08-15', 'enrolled'),
(4, 4, '2023-08-15', 'enrolled'),
(5, 5, '2023-08-15', 'enrolled');

-- Insert class schedule
INSERT INTO `class_schedule` (`section_id`, `day_of_week`, `start_time`, `end_time`, `room`) VALUES
(1, 'Monday', '09:00:00', '10:30:00', 'Room 101'),
(1, 'Wednesday', '09:00:00', '10:30:00', 'Room 101'),
(1, 'Friday', '09:00:00', '10:30:00', 'Room 101'),
(3, 'Tuesday', '11:00:00', '12:30:00', 'Lab 201'),
(3, 'Thursday', '11:00:00', '12:30:00', 'Lab 201'),
(4, 'Monday', '14:00:00', '15:30:00', 'Room 102'),
(4, 'Wednesday', '14:00:00', '15:30:00', 'Room 102');

-- Insert attendance records
INSERT INTO `attendance` (`student_id`, `section_id`, `class_date`, `status`, `check_in_time`, `recorded_by`) VALUES
(1, 1, '2023-11-06', 'present', '09:05:00', 1),
(2, 1, '2023-11-06', 'present', '09:02:00', 1),
(3, 1, '2023-11-06', 'present', '09:00:00', 1),
(4, 1, '2023-11-06', 'absent', NULL, 1),
(1, 1, '2023-11-08', 'present', '09:01:00', 1),
(2, 1, '2023-11-08', 'late', '09:15:00', 1),
(3, 1, '2023-11-08', 'present', '09:04:00', 1),
(4, 1, '2023-11-08', 'present', '09:03:00', 1);

-- Insert attendance summary
INSERT INTO `attendance_summary` (`student_id`, `section_id`, `total_classes`, `classes_present`, `classes_absent`, `classes_late`, `attendance_percentage`, `last_updated`) VALUES
(1, 1, 2, 2, 0, 0, 100.00, '2023-11-08'),
(2, 1, 2, 2, 0, 1, 100.00, '2023-11-08'),
(3, 1, 2, 2, 0, 0, 100.00, '2023-11-08'),
(4, 1, 2, 1, 1, 0, 50.00, '2023-11-08');

-- Insert holidays
INSERT INTO `holidays` (`name`, `holiday_date`, `academic_term`, `description`) VALUES
('Diwali', '2023-11-12', 'Fall 2023', 'Festival of Lights'),
('Christmas', '2023-12-25', 'Fall 2023', 'Christmas Holiday');

-- Insert users
INSERT INTO `users` (`username`, `password`, `email`, `user_type`, `reference_id`, `is_active`) VALUES
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin@edu.in', 'admin', 1, TRUE),
('jsmith', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'james.smith@edu.in', 'faculty', 1, TRUE),
('pjohnson', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'patricia.johnson@edu.in', 'faculty', 2, TRUE),
('jdavis', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'john.davis@edu.in', 'student', 1, TRUE),
('swilson', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'sarah.wilson@edu.in', 'student', 2, TRUE);

-- Insert system settings
INSERT INTO `system_settings` (`setting_key`, `setting_value`, `description`) VALUES
('attendance_threshold', '75', 'Minimum attendance percentage required'),
('late_threshold_minutes', '15', 'Minutes after which a student is marked late'),
('system_name', 'EduTrack - Student Attendance System', 'Name of the system'),
('academic_term', 'Fall 2023', 'Current academic term');

-- --------------------------------------------------------
-- Create views for common queries
-- --------------------------------------------------------

-- View for student attendance details
CREATE VIEW `student_attendance_view` AS
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.course_code,
    c.name AS course_name,
    sec.section_code,
    a.class_date,
    a.status,
    a.check_in_time,
    f.first_name AS recorded_by_first_name,
    f.last_name AS recorded_by_last_name
FROM attendance a
JOIN students s ON a.student_id = s.id
JOIN sections sec ON a.section_id = sec.id
JOIN courses c ON sec.course_id = c.id
JOIN faculty f ON a.recorded_by = f.id;

-- View for faculty courses
CREATE VIEW `faculty_courses_view` AS
SELECT 
    f.faculty_id,
    CONCAT(f.first_name, ' ', f.last_name) AS faculty_name,
    c.course_code,
    c.name AS course_name,
    sec.section_code,
    sec.academic_term,
    sec.year,
    COUNT(e.student_id) AS enrolled_students
FROM faculty f
JOIN sections sec ON f.id = sec.faculty_id
JOIN courses c ON sec.course_id = c.id
LEFT JOIN enrollments e ON sec.id = e.section_id AND e.enrollment_status = 'enrolled'
GROUP BY f.id, sec.id;

-- View for student enrollment details
CREATE VIEW `student_enrollment_view` AS
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    p.name AS program_name,
    c.course_code,
    c.name AS course_name,
    sec.section_code,
    f.first_name AS faculty_first_name,
    f.last_name AS faculty_last_name,
    sec.academic_term,
    sec.year
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN sections sec ON e.section_id = sec.id
JOIN courses c ON sec.course_id = c.id
JOIN faculty f ON sec.faculty_id = f.id
JOIN programs p ON s.program_id = p.id
WHERE e.enrollment_status = 'enrolled';

-- --------------------------------------------------------
-- Create triggers for automation
-- --------------------------------------------------------

-- Trigger to update enrollment count when a student enrolls
DELIMITER $$
CREATE TRIGGER `after_enrollment_insert`
AFTER INSERT ON `enrollments`
FOR EACH ROW
BEGIN
    UPDATE sections 
    SET current_enrollment = current_enrollment + 1 
    WHERE id = NEW.section_id;
END$$
DELIMITER ;

-- Trigger to update enrollment count when a student drops
DELIMITER $$
CREATE TRIGGER `after_enrollment_update`
AFTER UPDATE ON `enrollments`
FOR EACH ROW
BEGIN
    IF OLD.enrollment_status = 'enrolled' AND NEW.enrollment_status != 'enrolled' THEN
        UPDATE sections 
        SET current_enrollment = current_enrollment - 1 
        WHERE id = NEW.section_id;
    END IF;
END$$
DELIMITER ;

-- Trigger to update attendance summary
DELIMITER $$
CREATE TRIGGER `after_attendance_insert`
AFTER INSERT ON `attendance`
FOR EACH ROW
BEGIN
    DECLARE total INT;
    DECLARE present INT;
    DECLARE absent INT;
    DECLARE late INT;
    DECLARE percentage DECIMAL(5,2);
    
    -- Get counts
    SELECT COUNT(*),
           SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END),
           SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END),
           SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END)
    INTO total, present, absent, late
    FROM attendance
    WHERE student_id = NEW.student_id AND section_id = NEW.section_id;
    
    -- Calculate percentage
    IF total > 0 THEN
        SET percentage = (present / total) * 100;
    ELSE
        SET percentage = 0;
    END IF;
    
    -- Update or insert summary
    INSERT INTO attendance_summary (student_id, section_id, total_classes, classes_present, classes_absent, classes_late, attendance_percentage, last_updated)
    VALUES (NEW.student_id, NEW.section_id, total, present, absent, late, percentage, CURDATE())
    ON DUPLICATE KEY UPDATE
        total_classes = total,
        classes_present = present,
        classes_absent = absent,
        classes_late = late,
        attendance_percentage = percentage,
        last_updated = CURDATE();
END$$
DELIMITER ;

-- Show all tables
SHOW TABLES;
