-- =====================================================================
-- K.K. Wagh Institute of Engineering Education and Research, Nashik
-- Department of Computer Engineering | Academic Year 2026-27
-- Course: Database Management Systems (DBMS Mini Project)
-- System: Internal Marks Management System
-- File: sample_data.sql (Realistic Sample Data for Testing)
-- =====================================================================

USE internal_marks_db;

-- ---------------------------------------------------------------------
-- 1. Insert Departments
-- ---------------------------------------------------------------------
INSERT INTO departments (department_id, dept_code, dept_name, intake_capacity, hod_name, established_year) VALUES
(1, 'COMP', 'Computer Engineering', 180, 'Dr. S. S. Sane', 1984),
(2, 'IT', 'Information Technology', 120, 'Dr. P. D. Bhamre', 1999),
(3, 'AIDS', 'Artificial Intelligence & Data Science', 60, 'Dr. V. C. Bagal', 2020);

-- ---------------------------------------------------------------------
-- 2. Insert Teachers
-- ---------------------------------------------------------------------
INSERT INTO teachers (teacher_id, emp_code, first_name, last_name, email, phone, designation, department_id) VALUES
(1, 'T-COMP-101', 'Pramod', 'Shah', 'pbshah@kkwagh.edu.in', '9822011223', 'Professor', 1),
(2, 'T-COMP-102', 'Archana', 'Kulkarni', 'arkulkarni@kkwagh.edu.in', '9822022334', 'Associate Professor', 1),
(3, 'T-COMP-103', 'Sachin', 'Patil', 'smpatil@kkwagh.edu.in', '9822033445', 'Assistant Professor', 1),
(4, 'T-COMP-104', 'Vidya', 'Deshmukh', 'vddeshmukh@kkwagh.edu.in', '9822044556', 'Associate Professor', 1),
(5, 'T-IT-201', 'Nitin', 'Jadhav', 'nsjadhav@kkwagh.edu.in', '9822055667', 'Assistant Professor', 2);

-- ---------------------------------------------------------------------
-- 3. Insert Students
-- ---------------------------------------------------------------------
INSERT INTO students (student_id, prn, roll_no, first_name, last_name, email, phone, class_year, division, admission_year, department_id) VALUES
(1, '72210011A', 'TE-COMP-01', 'Aarav', 'Sharma', 'aarav.sharma@kkwagh.edu.in', '9123456780', 'TE', 'A', 2024, 1),
(2, '72210012B', 'TE-COMP-02', 'Ananya', 'Joshi', 'ananya.joshi@kkwagh.edu.in', '9123456781', 'TE', 'A', 2024, 1),
(3, '72210013C', 'TE-COMP-03', 'Rohan', 'Kadam', 'rohan.kadam@kkwagh.edu.in', '9123456782', 'TE', 'A', 2024, 1),
(4, '72210014D', 'TE-COMP-04', 'Sneha', 'Patil', 'sneha.patil@kkwagh.edu.in', '9123456783', 'TE', 'A', 2024, 1),
(5, '72210015E', 'TE-COMP-05', 'Aditya', 'Shinde', 'aditya.shinde@kkwagh.edu.in', '9123456784', 'TE', 'A', 2024, 1),
(6, '72210016F', 'TE-COMP-06', 'Priya', 'Deshmukh', 'priya.deshmukh@kkwagh.edu.in', '9123456785', 'TE', 'A', 2024, 1),
(7, '72210017G', 'TE-COMP-07', 'Omkar', 'Gaikwad', 'omkar.gaikwad@kkwagh.edu.in', '9123456786', 'TE', 'A', 2024, 1),
(8, '72210018H', 'TE-COMP-08', 'Tanvi', 'Kulkarni', 'tanvi.kulkarni@kkwagh.edu.in', '9123456787', 'TE', 'A', 2024, 1),
(9, '72310021A', 'SE-COMP-01', 'Siddharth', 'More', 'siddharth.more@kkwagh.edu.in', '9123456788', 'SE', 'B', 2025, 1),
(10, '72310022B', 'SE-COMP-02', 'Isha', 'Borse', 'isha.borse@kkwagh.edu.in', '9123456789', 'SE', 'B', 2025, 1);

-- ---------------------------------------------------------------------
-- 4. Insert Subjects
-- ---------------------------------------------------------------------
INSERT INTO subjects (subject_id, subject_code, subject_name, semester, class_year, credits, department_id, teacher_id) VALUES
(1, '310241', 'Database Management Systems', 5, 'TE', 4, 1, 1),
(2, '310242', 'Theory of Computation', 5, 'TE', 3, 1, 2),
(3, '310243', 'Operating Systems', 5, 'TE', 3, 1, 3),
(4, '310244', 'Computer Networks and Security', 5, 'TE', 3, 1, 4),
(5, '210241', 'Data Structures and Algorithms', 3, 'SE', 4, 1, 3),
(6, '410241', 'Machine Learning', 7, 'BE', 4, 1, 1);

-- ---------------------------------------------------------------------
-- 5. Insert Enrollments
-- ---------------------------------------------------------------------
-- Enroll TE students in Semester 5 courses
INSERT INTO enrollments (enrollment_id, student_id, subject_id, academic_year, semester, enrollment_date, status) VALUES
-- Student 1 (Aarav Sharma)
(1, 1, 1, '2026-2027', 5, '2026-07-15', 'Active'),
(2, 1, 2, '2026-2027', 5, '2026-07-15', 'Active'),
(3, 1, 3, '2026-2027', 5, '2026-07-15', 'Active'),
(4, 1, 4, '2026-2027', 5, '2026-07-15', 'Active'),
-- Student 2 (Ananya Joshi)
(5, 2, 1, '2026-2027', 5, '2026-07-15', 'Active'),
(6, 2, 2, '2026-2027', 5, '2026-07-15', 'Active'),
(7, 2, 3, '2026-2027', 5, '2026-07-15', 'Active'),
(8, 2, 4, '2026-2027', 5, '2026-07-15', 'Active'),
-- Student 3 (Rohan Kadam)
(9, 3, 1, '2026-2027', 5, '2026-07-15', 'Active'),
(10, 3, 2, '2026-2027', 5, '2026-07-15', 'Active'),
(11, 3, 3, '2026-2027', 5, '2026-07-15', 'Active'),
(12, 3, 4, '2026-2027', 5, '2026-07-15', 'Active'),
-- Student 4 (Sneha Patil)
(13, 4, 1, '2026-2027', 5, '2026-07-15', 'Active'),
(14, 4, 2, '2026-2027', 5, '2026-07-15', 'Active'),
-- Student 5 (Aditya Shinde)
(15, 5, 1, '2026-2027', 5, '2026-07-15', 'Active'),
(16, 5, 2, '2026-2027', 5, '2026-07-15', 'Active'),
-- Student 6 (Priya Deshmukh)
(17, 6, 1, '2026-2027', 5, '2026-07-15', 'Active'),
-- Student 7 (Omkar Gaikwad)
(18, 7, 1, '2026-2027', 5, '2026-07-15', 'Active'),
-- Student 8 (Tanvi Kulkarni)
(19, 8, 1, '2026-2027', 5, '2026-07-15', 'Active'),
-- SE Students in DSA
(20, 9, 5, '2026-2027', 3, '2026-07-15', 'Active'),
(21, 10, 5, '2026-2027', 3, '2026-07-15', 'Active');

-- ---------------------------------------------------------------------
-- 6. Insert Assessments
-- ---------------------------------------------------------------------
INSERT INTO assessments (assessment_id, subject_id, assessment_name, assessment_type, max_marks, weightage_percent, conducted_date, academic_year) VALUES
-- DBMS Assessments (Subject 1)
(1, 1, 'In-Semester Exam', 'In-Semester', 30.00, 100.00, '2026-09-10', '2026-2027'),
(2, 1, 'End-Semester Exam', 'End-Semester', 70.00, 100.00, '2026-11-25', '2026-2027'),
(3, 1, 'Unit Test 1', 'Unit Test', 25.00, 100.00, '2026-08-20', '2026-2027'),
(4, 1, 'Term Work', 'Term Work', 25.00, 100.00, '2026-11-10', '2026-2027'),
(5, 1, 'Practical / Oral', 'Practical / Oral', 25.00, 100.00, '2026-11-15', '2026-2027'),
-- TOC Assessments (Subject 2)
(6, 2, 'In-Semester Exam', 'In-Semester', 30.00, 100.00, '2026-09-12', '2026-2027'),
(7, 2, 'End-Semester Exam', 'End-Semester', 70.00, 100.00, '2026-11-28', '2026-2027'),
-- OS Assessments (Subject 3)
(8, 3, 'In-Semester Exam', 'In-Semester', 30.00, 100.00, '2026-09-15', '2026-2027'),
(9, 3, 'End-Semester Exam', 'End-Semester', 70.00, 100.00, '2026-12-02', '2026-2027'),
-- CNS Assessments (Subject 4)
(10, 4, 'In-Semester Exam', 'In-Semester', 30.00, 100.00, '2026-09-18', '2026-2027'),
(11, 4, 'End-Semester Exam', 'End-Semester', 70.00, 100.00, '2026-12-05', '2026-2027'),
-- DSA Assessments (Subject 5)
(12, 5, 'Unit Test 1', 'Unit Test', 25.00, 100.00, '2026-08-22', '2026-2027');

-- ---------------------------------------------------------------------
-- 7. Insert Marks
-- ---------------------------------------------------------------------
-- Student 1 (Aarav Sharma) Marks
-- Enrollment 1: DBMS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(1, 1, 27.50, FALSE, 'Excellent analytical answers'),
(1, 2, 62.00, FALSE, 'Strong performance in SQL and transactions'),
(1, 3, 24.00, FALSE, 'Full marks in ER diagram problem'),
(1, 4, 23.50, FALSE, 'Timely lab submission'),
(1, 5, 24.00, FALSE, 'Confident viva responses');

-- Enrollment 2: TOC
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(2, 6, 26.00, FALSE, 'Well drawn DFA and PDA models'),
(2, 7, 58.00, FALSE, 'Good theoretical mastery');

-- Enrollment 3: OS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(3, 8, 25.00, FALSE, 'Clear understanding of scheduling algorithms'),
(3, 9, 61.00, FALSE, 'Comprehensive answers');

-- Enrollment 4: CNS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(4, 10, 28.00, FALSE, 'Accurate cryptography steps'),
(4, 11, 64.00, FALSE, 'Very well prepared');

-- Student 2 (Ananya Joshi) Marks
-- Enrollment 5: DBMS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(5, 1, 29.00, FALSE, 'Outstanding performance - top of class'),
(5, 2, 66.50, FALSE, 'Excellent schema design and relational calculus'),
(5, 3, 25.00, FALSE, 'Full marks'),
(5, 4, 24.50, FALSE, 'Consistently neat lab documentation'),
(5, 5, 25.00, FALSE, 'Flawless viva and query execution');

-- Enrollment 6: TOC
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(6, 6, 28.50, FALSE, 'Perfect Turing machine representation'),
(6, 7, 65.00, FALSE, 'First class with distinction performance');

-- Student 3 (Rohan Kadam) Marks
-- Enrollment 9: DBMS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(9, 1, 18.00, FALSE, 'Average - needs more SQL practice'),
(9, 2, 38.00, FALSE, 'Passing threshold achieved'),
(9, 3, 16.00, FALSE, 'Fair attempt'),
(9, 4, 18.00, FALSE, 'Satisfactory lab manual'),
(9, 5, 17.50, FALSE, 'Basic concepts clear');

-- Student 4 (Sneha Patil) Marks
-- Enrollment 13: DBMS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(13, 1, 24.50, FALSE, 'Good conceptual clarity'),
(13, 2, 54.00, FALSE, 'Well written query optimization answers'),
(13, 3, 21.00, FALSE, 'Good score'),
(13, 4, 22.00, FALSE, 'Completed on time'),
(13, 5, 22.50, FALSE, 'Prompt answers');

-- Student 5 (Aditya Shinde) Marks
-- Enrollment 15: DBMS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(15, 1, 9.50, FALSE, 'Failed In-Sem, need remedial sessions'),
(15, 2, 24.00, FALSE, 'Failed End-Sem, backlog exam required'),
(15, 3, 8.00, FALSE, 'Poor attempt'),
(15, 4, 14.00, FALSE, 'Incomplete write-ups'),
(15, 5, 12.00, FALSE, 'Struggled with primary keys');

-- Student 6 (Priya Deshmukh) Marks (Includes an Absent case for testing)
-- Enrollment 17: DBMS
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(17, 1, 0.00, TRUE, 'Medical emergency - Absent with prior notice'),
(17, 2, 59.00, FALSE, 'Re-appeared with approval, good recovery'),
(17, 3, 20.00, FALSE, 'Good test attempt'),
(17, 4, 21.00, FALSE, 'Lab certified'),
(17, 5, 20.50, FALSE, 'Good demonstration');

-- Student 7 (Omkar Gaikwad) Marks
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(18, 1, 21.00, FALSE, 'Good'),
(18, 2, 49.00, FALSE, 'Passed comfortably');

-- Student 8 (Tanvi Kulkarni) Marks
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(19, 1, 26.00, FALSE, 'Strong performance'),
(19, 2, 60.50, FALSE, 'First class mark');

-- SE Students (DSA Marks - Assessment 12: Unit Test 1)
INSERT INTO marks (enrollment_id, assessment_id, marks_obtained, is_absent, remarks) VALUES
(20, 12, 23.50, FALSE, 'Proficient in Linked Lists and Binary Trees'),
(21, 12, 21.00, FALSE, 'Good implementation of Stack and Queue');

