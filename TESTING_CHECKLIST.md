# Internal Marks Management System — Testing Checklist & Test Matrix

**Institution:** K.K. Wagh Institute of Engineering Education and Research, Nashik  
**Department:** Department of Computer Engineering  
**Academic Year:** 2026–2027  
**Test Suite Status:** 12 of 12 Automated Tests Passing (100% Pass Rate)  

---

## 📋 Comprehensive Verification Matrix

| Test ID | Module / Requirement | Test Description | Test Inputs & Actions | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|:---:|
| **TC-01** | **Architecture** | Desktop Application Verification | Launch `python main.py` | Native desktop window opens (Tkinter/`ttk`), zero web dependencies | Native Tkinter window opens with full desktop navigation | **PASS** |
| **TC-02** | **Schema Design** | Seven Tables Verification | Inspect database schema | Tables `departments`, `teachers`, `students`, `subjects`, `enrollments`, `assessments`, `marks` exist with PKs & FKs | All 7 tables present with normalized schema and constraints | **PASS** |
| **TC-03** | **Referential Integrity** | Foreign Key Cascading & Restriction | 1. Attempt deleting Department with active students.<br>2. Delete a student with enrollments. | 1. Department deletion blocked by `ON DELETE RESTRICT`.<br>2. Student deleted and associated enrollments removed by `CASCADE`. | Enforced accurately by database engine | **PASS** |
| **TC-04** | **Requirement #9** | Duplicate Enrollment Prevention | Enroll Student `1` in Course `1` for AY `2026-2027`, Sem `5` twice | Database rejects second attempt via `uq_student_enrollment` with clear error alert | Caught and user-friendly error displayed | **PASS** |
| **TC-05** | **Requirement #9** | Duplicate Marks Entry Prevention | Insert marks for Enrollment `1` and Assessment `1` twice | Database rejects second insert via `uq_enrollment_assessment` | Duplicate blocked; updates allowed via `UPDATE` | **PASS** |
| **TC-06** | **Requirement #10** | Upper Bound Marks Validation | Attempt entering `35.00` marks for an assessment with `max_marks = 30.00` | Rejected by trigger `trg_validate_marks` and GUI form validation | Blocked with "Marks obtained cannot exceed maximum marks" | **PASS** |
| **TC-07** | **Requirement #10** | Lower Bound Marks Validation | Attempt entering `-5.00` marks | Rejected by `CHECK (marks_obtained >= 0.00)` | Blocked with "Marks cannot be negative" | **PASS** |
| **TC-08** | **CRUD: Students** | Student Registration & Edit | Add student 'Tanmay Patil' with PRN '72210099Z'; update roll number | Record saved with parameterized query; updated in table | Verified; row updated smoothly in treeview | **PASS** |
| **TC-09** | **Search & Filter** | Student Roster Filtering | Filter by Class Year: 'TE', Division: 'A', Search: 'Aarav' | Treeview displays matching record in real time | Single matching record displayed instantly | **PASS** |
| **TC-10** | **Requirement #6** | Report 1: Student Marksheet | Select student 'Aarav Sharma' in Reports | Generates table of all subjects, evaluations, aggregate %, and SPPU grade classification | Complete marksheet computed; exported to text file | **PASS** |
| **TC-11** | **Requirement #6** | Report 2: Subject Performance | Select 'Database Management Systems', 'In-Semester Exam' | Displays Appeared, Passed, Failed, Absent, Pass %, Average, Max, Min | KPI metrics match database aggregations | **PASS** |
| **TC-12** | **Requirement #6** | Report 3: Class Performance | Select Class 'TE', Division 'A' | Computes class mean, grade classification distribution, and merit leaderboard | Ranked students list generated using `GROUP BY` and `SUM()` | **PASS** |
| **TC-13** | **Requirement #7** | SQL Joins & Aggregates | Run view `vw_student_marks_detailed` and analytical queries | Multi-table joins across 5 tables execute with aggregations and grouping | Verified in automated unit test suite | **PASS** |
| **TC-14** | **Requirement #8** | Transaction Rollback on Error | Simulate database failure mid-operation | `conn.rollback()` executes; database state remains clean | Transaction atomicity verified | **PASS** |
| **TC-15** | **Requirement #11** | Sample Data Loading | Execute `sample_data.sql` | 3 departments, 5 teachers, 10 students, 6 subjects, 21 enrollments, 12 assessments, 44 marks loaded | All records verified with zero foreign key violations | **PASS** |
| **TC-16** | **Settings & Mode** | Dual-Engine Support (MySQL & SQLite) | Switch between MySQL and Standalone SQLite | Seamless operation in both modes for demonstration | Tested; GUI switches seamlessly without restarts | **PASS** |

---

## 🛠️ Step-by-Step Manual Testing Walkthrough

Follow these manual steps to evaluate the application during viva or project review:

### Step 1: Launch Application
```powershell
python main.py
```
- Verify that the Institutional Header displays:
  `K.K. Wagh Institute of Engineering Education and Research, Nashik`
  `Department of Computer Engineering | Academic Year 2026–27`
- Verify that the Database Connection badge displays:
  `🟢 MySQL Server` (or `🔵 Standalone SQLite`).

### Step 2: Test Student Management
1. Click **🎓 Students Roster** in the sidebar.
2. Filter by Class Year `TE` $\rightarrow$ 8 TE students appear.
3. In the search box, type `Ananya` $\rightarrow$ Ananya Joshi is filtered.
4. Click **Reset** $\rightarrow$ All students reload.
5. Click **➕ Add Student** $\rightarrow$ enter test details $\rightarrow$ click **Save Record**. Verify the new student appears in the table.

### Step 3: Test Course Enrollment & Duplicate Prevention (Req #9)
1. Click **📝 Course Enrollments** in the sidebar.
2. Click **➕ Enroll Student**.
3. Select an existing student (e.g., Aarav Sharma) and Course (`310241 - DBMS`, Sem 5, AY 2026-2027).
4. Click **Save Record**.
5. **Expected Result:** A modal warning appears:
   `Duplicate Error: The student is already enrolled in this subject for the specified academic year and semester.`

### Step 4: Test Marks Entry & Boundary Validation (Req #10)
1. Click **✍️ Marks Entry & Grading** in the sidebar.
2. Select Subject: `310241 - Database Management Systems`.
3. Select Assessment: `In-Semester Exam (In-Semester, Max: 30.0)`.
4. Double-click on any student.
5. In the form, enter `35.00` (which is $> 30.00$).
6. Click **Save Record**.
7. **Expected Result:** An alert modal appears:
   `Validation Error: Marks obtained (35.0) cannot exceed maximum marks (30.0).`
8. Now enter a valid mark, e.g. `27.50` $\rightarrow$ Click **Save Record** $\rightarrow$ table updates with status `Pass` and percentage `91.67%`.
9. Select another student and click **⚡ Mark Absent** $\rightarrow$ student's marks become `0.00` and status changes to `Absent`.

### Step 5: Test Report 1 (Student-wise Marksheet)
1. Click **📈 Reports & Marksheets** in the sidebar.
2. Open the **📜 Student-wise Marksheet** tab.
3. Select `TE-COMP-01 - Aarav Sharma (72210011A)`.
4. Observe the complete course breakdown table, cumulative total, aggregate percentage, and classification: `FIRST CLASS WITH DISTINCTION ⭐`.
5. Click **💾 Export Marksheet** $\rightarrow$ save the file as a `.txt` document. Open the exported text file to verify the official marksheet layout.

### Step 6: Test Report 2 (Subject-wise Performance)
1. Switch to the **📊 Subject-wise Report** tab.
2. Select Subject: `310241 - Database Management Systems` and Assessment: `End-Semester Exam`.
3. Review KPI cards:
   - Total Appeared
   - Pass Rate %
   - Average Marks
   - Highest / Lowest Score
4. Review the student roster ranked by marks obtained.

### Step 7: Test Report 3 (Class Performance Analytics)
1. Switch to the **🏛️ Class Performance & Analytics** tab.
2. Select Class Year `TE` and Division `A`.
3. Review the analytical summary:
   - Total Evaluated Students
   - Class Mean Aggregate %
   - Grade Distribution breakdown (Distinction, First Class, Second Class, Fail)
4. Review the **Class Merit Leaderboard** ranked from #1 downwards.

---

## 🤖 Running Automated Unit Test Suite

Run all test cases in a single command:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

**Expected Console Output:**
```
Ran 12 tests in 1.232s

OK
```
All 12 test cases pass without any errors or warnings.
