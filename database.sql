-- =====================================================================
-- K.K. Wagh Institute of Engineering Education and Research, Nashik
-- Department of Computer Engineering | Academic Year 2026-27
-- Course: Database Management Systems (DBMS Mini Project)
-- System: Internal Marks Management System
-- File: database.sql (Complete Relational Schema, DDL & Constraints)
-- =====================================================================

-- Drop database if exists and create fresh database
DROP DATABASE IF EXISTS internal_marks_db;
CREATE DATABASE internal_marks_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE internal_marks_db;

-- ---------------------------------------------------------------------
-- Table 1: departments
-- Stores departmental details within the institute
-- ---------------------------------------------------------------------
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_code VARCHAR(10) NOT NULL UNIQUE,
    dept_name VARCHAR(100) NOT NULL,
    intake_capacity INT NOT NULL DEFAULT 180,
    hod_name VARCHAR(100) NOT NULL,
    established_year INT NOT NULL DEFAULT 1984,
    CONSTRAINT chk_dept_intake CHECK (intake_capacity > 0),
    CONSTRAINT chk_dept_year CHECK (established_year >= 1984)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 2: teachers
-- Stores faculty members associated with departments
-- ---------------------------------------------------------------------
CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    designation VARCHAR(50) NOT NULL,
    department_id INT NOT NULL,
    CONSTRAINT fk_teachers_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_teacher_designation CHECK (
        designation IN ('Professor', 'Associate Professor', 'Assistant Professor', 'Adjunct Faculty')
    )
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 3: students
-- Stores student demographic and enrollment profile
-- ---------------------------------------------------------------------
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    prn VARCHAR(20) NOT NULL UNIQUE,
    roll_no VARCHAR(15) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    class_year VARCHAR(10) NOT NULL,
    division VARCHAR(5) NOT NULL,
    admission_year INT NOT NULL DEFAULT 2026,
    department_id INT NOT NULL,
    CONSTRAINT fk_students_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_student_roll UNIQUE (department_id, class_year, division, roll_no),
    CONSTRAINT chk_student_year CHECK (class_year IN ('FE', 'SE', 'TE', 'BE')),
    CONSTRAINT chk_student_div CHECK (division IN ('A', 'B', 'C', 'D'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 4: subjects
-- Stores curriculum subjects mapped to academic years and teachers
-- ---------------------------------------------------------------------
CREATE TABLE subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    class_year VARCHAR(10) NOT NULL,
    credits INT NOT NULL DEFAULT 3,
    department_id INT NOT NULL,
    teacher_id INT NULL,
    CONSTRAINT fk_subjects_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_subjects_teacher FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT chk_subject_sem CHECK (semester BETWEEN 1 AND 8),
    CONSTRAINT chk_subject_year CHECK (class_year IN ('FE', 'SE', 'TE', 'BE')),
    CONSTRAINT chk_subject_credits CHECK (credits > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 5: enrollments
-- Represents course registration of students for a specific academic year
-- ---------------------------------------------------------------------
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    academic_year VARCHAR(15) NOT NULL DEFAULT '2026-2027',
    semester INT NOT NULL,
    enrollment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_enrollments_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    -- Prevent duplicate enrollments for the same student in the same subject and academic term
    CONSTRAINT uq_student_enrollment UNIQUE (student_id, subject_id, academic_year, semester),
    CONSTRAINT chk_enrollment_sem CHECK (semester BETWEEN 1 AND 8),
    CONSTRAINT chk_enrollment_status CHECK (status IN ('Active', 'Completed', 'Dropped'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 6: assessments
-- Defines evaluation schemes per subject (In-Sem, End-Sem, TW, Practical, UT)
-- ---------------------------------------------------------------------
CREATE TABLE assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    assessment_name VARCHAR(100) NOT NULL,
    assessment_type VARCHAR(30) NOT NULL,
    max_marks DECIMAL(5,2) NOT NULL,
    weightage_percent DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    conducted_date DATE,
    academic_year VARCHAR(15) NOT NULL DEFAULT '2026-2027',
    CONSTRAINT fk_assessments_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_subject_assessment UNIQUE (subject_id, assessment_name, academic_year),
    CONSTRAINT chk_assessment_max_marks CHECK (max_marks > 0),
    CONSTRAINT chk_assessment_weightage CHECK (weightage_percent > 0 AND weightage_percent <= 100),
    CONSTRAINT chk_assessment_type CHECK (
        assessment_type IN ('In-Semester', 'End-Semester', 'Unit Test', 'Term Work', 'Practical / Oral', 'Assignment')
    )
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 7: marks
-- Records marks obtained by enrolled students for specific assessments
-- ---------------------------------------------------------------------
CREATE TABLE marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT NOT NULL,
    assessment_id INT NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    is_absent BOOLEAN NOT NULL DEFAULT FALSE,
    remarks VARCHAR(255) NULL,
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_marks_enrollment FOREIGN KEY (enrollment_id)
        REFERENCES enrollments(enrollment_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_marks_assessment FOREIGN KEY (assessment_id)
        REFERENCES assessments(assessment_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    -- Prevent duplicate marks entry for the same enrollment and assessment
    CONSTRAINT uq_enrollment_assessment UNIQUE (enrollment_id, assessment_id),
    CONSTRAINT chk_marks_non_negative CHECK (marks_obtained >= 0.00)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Triggers for Business Rules & Integrity Verification
-- ---------------------------------------------------------------------
DELIMITER //

-- Trigger: Ensure marks_obtained does not exceed assessment.max_marks on INSERT
CREATE TRIGGER trg_validate_marks_insert
BEFORE INSERT ON marks
FOR EACH ROW
BEGIN
    DECLARE v_max_marks DECIMAL(5,2);
    SELECT max_marks INTO v_max_marks
    FROM assessments
    WHERE assessment_id = NEW.assessment_id;

    IF NEW.is_absent = TRUE THEN
        SET NEW.marks_obtained = 0.00;
    ELSEIF NEW.marks_obtained > v_max_marks THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Validation Error: Marks obtained cannot exceed assessment maximum marks';
    END IF;
END //

-- Trigger: Ensure marks_obtained does not exceed assessment.max_marks on UPDATE
CREATE TRIGGER trg_validate_marks_update
BEFORE UPDATE ON marks
FOR EACH ROW
BEGIN
    DECLARE v_max_marks DECIMAL(5,2);
    SELECT max_marks INTO v_max_marks
    FROM assessments
    WHERE assessment_id = NEW.assessment_id;

    IF NEW.is_absent = TRUE THEN
        SET NEW.marks_obtained = 0.00;
    ELSEIF NEW.marks_obtained > v_max_marks THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Validation Error: Marks obtained cannot exceed assessment maximum marks';
    END IF;
END //

DELIMITER ;

-- ---------------------------------------------------------------------
-- Database Views for Reporting and Dashboard Summaries
-- Demonstrating SQL JOINs, Aggregates, GROUP BY
-- ---------------------------------------------------------------------

-- View: Complete Student Mark Details
CREATE OR REPLACE VIEW vw_student_marks_detailed AS
SELECT 
    m.mark_id,
    s.student_id,
    s.prn,
    s.roll_no,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.class_year,
    s.division,
    d.dept_code,
    d.dept_name,
    sub.subject_code,
    sub.subject_name,
    a.assessment_id,
    a.assessment_name,
    a.assessment_type,
    a.max_marks,
    m.marks_obtained,
    m.is_absent,
    ROUND((m.marks_obtained / a.max_marks) * 100, 2) AS percentage,
    CASE 
        WHEN m.is_absent = TRUE THEN 'Absent'
        WHEN (m.marks_obtained / a.max_marks) >= 0.40 THEN 'Pass'
        ELSE 'Fail'
    END AS result_status,
    e.academic_year,
    e.semester
FROM marks m
JOIN enrollments e ON m.enrollment_id = e.enrollment_id
JOIN students s ON e.student_id = s.student_id
JOIN departments d ON s.department_id = d.department_id
JOIN assessments a ON m.assessment_id = a.assessment_id
JOIN subjects sub ON a.subject_id = sub.subject_id;

-- View: Subject-wise Performance Summary (Aggregation & GROUP BY)
CREATE OR REPLACE VIEW vw_subject_performance_summary AS
SELECT 
    sub.subject_id,
    sub.subject_code,
    sub.subject_name,
    sub.class_year,
    sub.semester,
    a.assessment_id,
    a.assessment_name,
    a.max_marks,
    COUNT(m.mark_id) AS total_students_appeared,
    SUM(CASE WHEN m.is_absent = FALSE AND (m.marks_obtained / a.max_marks) >= 0.40 THEN 1 ELSE 0 END) AS students_passed,
    SUM(CASE WHEN m.is_absent = FALSE AND (m.marks_obtained / a.max_marks) < 0.40 THEN 1 ELSE 0 END) AS students_failed,
    SUM(CASE WHEN m.is_absent = TRUE THEN 1 ELSE 0 END) AS students_absent,
    ROUND(AVG(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE NULL END), 2) AS average_marks,
    MAX(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE NULL END) AS highest_marks,
    MIN(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE NULL END) AS lowest_marks,
    ROUND((SUM(CASE WHEN m.is_absent = FALSE AND (m.marks_obtained / a.max_marks) >= 0.40 THEN 1 ELSE 0 END) / 
           NULLIF(COUNT(m.mark_id), 0)) * 100, 2) AS pass_percentage
FROM subjects sub
JOIN assessments a ON sub.subject_id = a.subject_id
LEFT JOIN marks m ON a.assessment_id = m.assessment_id
GROUP BY sub.subject_id, sub.subject_code, sub.subject_name, sub.class_year, sub.semester, a.assessment_id, a.assessment_name, a.max_marks;
