# Bug Tracker with Test Case Management

A comprehensive Software Quality Assurance (SQA) project demonstrating bug tracking, test case management, test execution tracking, and automated quality metrics including code coverage and mutation testing.

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Quality Metrics](#quality-metrics)
- [Workflow Example](#workflow-example)

---

## ✨ Features

### Core Functionality

- **Bug Management**: Create, view, edit, and delete bugs with validation
- **Test Case Management**: Create and manage test cases
- **Test Execution**: Record test execution results (Pass/Fail)
- **Bug-Test Linking**: Link bugs to test cases for traceability
- **Status Workflow**: Enforced bug status transitions (Open → In Progress → Resolved → Closed)
- **Reports Dashboard**: Comprehensive dashboard with statistics and metrics

### Quality Assurance Features

- **Code Coverage Tracking**: Automated coverage analysis with pytest-cov
- **Mutation Testing**: Code quality validation with mutmut
- **Automated Testing**: 72 comprehensive pytest tests
- **Data Validation**: Server-side validation for all inputs
- **Duplicate Prevention**: Prevents duplicate bugs (same title + module)

---

## �️ Technology Stack

- **Backend**: Python 3.11, Flask 3.0.3
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5, Bootstrap Icons
- **Testing**: pytest 8.2.2, pytest-cov 5.0.0
- **Quality Tools**: mutmut 2.4.4 (mutation testing)

---

## 📁 Project Structure

```
bug_tracker/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── db.py                 # Database connection and initialization
│   ├── routes/
│   │   ├── bugs.py           # Bug CRUD operations
│   │   ├── test_cases.py     # Test case management
│   │   ├── executions.py     # Test execution tracking
│   │   └── reports.py        # Dashboard and metrics
│   └── templates/
│       ├── base.html         # Base template with navigation
│       ├── index.html        # Home page
│       ├── bugs/             # Bug templates
│       ├── test_cases/       # Test case templates
│       ├── executions/       # Execution templates
│       └── reports/          # Dashboard template
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   ├── test_bugs.py          # Bug functionality tests (26 tests)
│   ├── test_executions.py   # Execution tests (21 tests)
│   └── test_reports.py       # Dashboard tests (25 tests)
├── instance/
│   └── bug_tracker.db        # SQLite database (auto-created)
├── .coveragerc               # Coverage configuration
├── pytest.ini                # Pytest configuration
├── mutmut_config.py          # Mutation testing configuration
├── run_mutation.bat          # Windows mutation test script
├── run_mutation.sh           # Linux/Mac mutation test script
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── README.md                 # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
cd bug_tracker
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python run.py
```

The database will be automatically created at `instance/bug_tracker.db`.

---

## � Usage

### Starting the Application

```bash
python run.py
```

The application will be available at: `http://127.0.0.1:5000`

### Main Features

#### 1. **Bug Management** (`/bugs/`)

- Create new bugs with title, module, description, and severity
- View all bugs with filtering by status
- Edit bug details and link to test cases
- Delete bugs
- Update bug status following workflow rules

#### 2. **Test Case Management** (`/test-cases/`)

- Create test cases with title, description, and expected results
- View all test cases
- Link test cases to bugs

#### 3. **Test Execution** (`/executions/`)

- Execute test cases and record results (Pass/Fail)
- Add execution notes
- Create bugs directly from failed test executions
- View execution history

#### 4. **Reports Dashboard** (`/reports/`)

- Bug statistics (total, by status, by severity)
- Test execution results (pass/fail counts)
- Code coverage metrics (per-module breakdown)
- Mutation testing results (mutation score)

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/
```

### Run Tests with Verbose Output

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_bugs.py
pytest tests/test_executions.py
pytest tests/test_reports.py
```

### Test Coverage

- **Total Tests**: 72
- **All Passing**: ✅
- **Code Coverage**: 78%

---

## 📊 Quality Metrics

### Code Coverage Analysis

Run tests with coverage:

```bash
pytest tests/
```

Coverage results are automatically generated and displayed in the dashboard.

**Current Coverage:**

- Overall: **78%**
- `app/db.py`: 100%
- `app/routes/reports.py`: 91%
- `app/routes/executions.py`: 92%
- `app/__init__.py`: 89%
- `app/routes/test_cases.py`: 64%
- `app/routes/bugs.py`: 61%

### Mutation Testing

Run mutation tests:

```bash
# Windows
run_mutation.bat

# Linux/Mac
chmod +x run_mutation.sh
./run_mutation.sh
```

**Current Mutation Score: 44.2%**

- Total Mutants: 429
- Killed: 169 (tests caught the mutation)
- Survived: 213 (tests didn't catch the mutation)
- Skipped: 47

Results are displayed in the dashboard at `/reports/`.

---

## 🔄 Workflow Examples

### Example 1: Failed Test → Bug Creation → Resolution

**Scenario**: Login functionality is broken

1. **Create Test Case**
   - Navigate to **Test Cases** → **Create New**
   - Title: "User Login Test"
   - Description: "Verify user can login with valid credentials"
   - Expected Result: "User redirected to dashboard with welcome message"
   - Click **Create Test Case**

2. **Execute Test Case (First Run - FAIL)**
   - Navigate to **Executions** → **Run Test**
   - Select: "User Login Test"
   - Result: **Fail**
   - Notes: "Login button not responding when clicked"
   - Click **Record Execution**

3. **Create Bug from Failed Test**
   - On execution detail page, click **"Create Bug from this Failure"**
   - Bug form auto-filled with test case information
   - Add details:
     - Severity: **High**
     - Module: **Authentication**
     - Description: "Login button click event not working"
   - Click **Create Bug**

4. **Track Bug Progress**
   - Bug created with status: **Open**
   - Developer starts work → Update status to **In Progress**
   - Bug fixed → Update status to **Resolved**
   - QA verifies fix → Update status to **Closed**

5. **Re-test After Fix (Second Run - PASS)**
   - Navigate to **Executions** → **Run Test**
   - Select: "User Login Test"
   - Result: **Pass**
   - Notes: "Login button now working correctly"
   - Click **Record Execution**

6. **View Traceability**
   - Bug detail page shows linked test case
   - Test case shows 2 executions (1 Fail, 1 Pass)
   - Complete audit trail of bug lifecycle

---

### Example 2: Passing Test (No Bug Needed)

**Scenario**: Logout functionality works correctly

1. **Create Test Case**
   - Navigate to **Test Cases** → **Create New**
   - Title: "User Logout Test"
   - Description: "Verify user can logout successfully"
   - Expected Result: "User logged out and redirected to login page"
   - Click **Create Test Case**

2. **Execute Test Case (PASS)**
   - Navigate to **Executions** → **Run Test**
   - Select: "User Logout Test"
   - Result: **Pass**
   - Notes: "Logout functionality working as expected"
   - Click **Record Execution**

3. **No Bug Creation Needed**
   - Execution detail page shows **Pass** status
   - No "Create Bug" button displayed (only shown for failures)
   - Test case marked as passing

4. **Regular Regression Testing**
   - Run same test periodically
   - All executions recorded in history
   - Ensures functionality remains stable

---

### Example 3: Multiple Test Executions

**Scenario**: Payment processing with intermittent issues

1. **Create Test Case**
   - Title: "Payment Processing Test"
   - Description: "Process $10 payment with valid card"
   - Expected Result: "Payment successful, confirmation displayed"

2. **First Execution (PASS)**
   - Result: **Pass**
   - Notes: "Payment processed successfully"

3. **Second Execution (FAIL)**
   - Result: **Fail**
   - Notes: "Payment gateway timeout after 30 seconds"
   - Create Bug: "Payment Gateway Timeout"
   - Severity: **Critical**
   - Module: **Payments**

4. **Third Execution (FAIL)**
   - Result: **Fail**
   - Notes: "Still timing out, issue persists"
   - Link to existing bug (no new bug needed)

5. **Fourth Execution (PASS)**
   - Result: **Pass**
   - Notes: "Timeout issue resolved, payment successful"
   - Update bug status to **Resolved**

6. **Fifth Execution (PASS)**
   - Result: **Pass**
   - Notes: "Regression test - still working"
   - Update bug status to **Closed**

**Execution History Shows:**

- Total: 5 executions
- Pass: 3 (60%)
- Fail: 2 (40%)
- Linked Bug: 1 (resolved)

---

### Example 4: Creating Bug Without Test Case

**Scenario**: Bug found during manual testing

1. **Create Bug Directly**
   - Navigate to **Bugs** → **Create New**
   - Title: "Dashboard Charts Not Loading"
   - Module: **Dashboard**
   - Description: "Charts show loading spinner indefinitely"
   - Severity: **Medium**
   - Test Case: Leave blank (no test case yet)
   - Click **Create Bug**

2. **Create Test Case Later**
   - Navigate to **Test Cases** → **Create New**
   - Title: "Dashboard Charts Display Test"
   - Description: "Verify all dashboard charts load within 5 seconds"
   - Expected Result: "All charts display data correctly"

3. **Link Bug to Test Case**
   - Navigate to bug detail page
   - Click **Edit Bug**
   - Select test case: "Dashboard Charts Display Test"
   - Click **Update Bug**

4. **Execute Test and Track**
   - Run test case → Result: **Fail** (confirms bug)
   - Fix bug → Update status to **Resolved**
   - Run test case → Result: **Pass** (verifies fix)
   - Update bug status to **Closed**

---

### Example 5: Monitoring Quality Metrics

**Scenario**: Weekly quality review

1. **Navigate to Dashboard** (`/reports/`)

2. **Review Bug Statistics**
   - Total Bugs: 15
   - Open: 3 (20%)
   - In Progress: 5 (33%)
   - Resolved: 4 (27%)
   - Closed: 3 (20%)

3. **Review Severity Breakdown**
   - Critical: 2
   - High: 5
   - Medium: 6
   - Low: 2

4. **Review Test Execution Results**
   - Total Executions: 45
   - Pass: 32 (71%)
   - Fail: 13 (29%)

5. **Review Code Coverage**
   - Overall: 78%
   - Critical modules: 89-100%
   - Identify low coverage areas for improvement

6. **Review Mutation Testing**
   - Mutation Score: 44.2%
   - Killed Mutants: 169
   - Survived Mutants: 213
   - Plan to strengthen test assertions

7. **Action Items**
   - Focus on resolving Critical and High severity bugs
   - Improve test coverage for modules below 70%
   - Add stronger assertions to increase mutation score
   - Create test cases for bugs without test coverage

---

### Example 6: Complete Traceability Chain

**Scenario**: Following a bug from discovery to closure

1. **Test Case Created**
   - "Search Functionality Test"
   - Expected: "Search returns relevant results"

2. **Test Execution (Fail)**
   - Result: Fail
   - Notes: "Search returns empty results for valid query"

3. **Bug Created from Failure**
   - Title: "Search Returns No Results"
   - Linked to: "Search Functionality Test"
   - Status: Open

4. **Bug Lifecycle**
   - Developer assigned → Status: In Progress
   - Code fixed → Status: Resolved
   - QA verified → Status: Closed

5. **Re-test Execution (Pass)**
   - Same test case executed
   - Result: Pass
   - Notes: "Search now returns correct results"

6. **Traceability View**
   - **Test Case** shows:
     - 2 executions (1 Fail, 1 Pass)
     - 1 linked bug (Closed)
   - **Bug** shows:
     - Linked test case
     - Status history (Open → In Progress → Resolved → Closed)
   - **Executions** show:
     - Complete test history
     - Pass/Fail trend

**Complete Audit Trail:**

```
Test Case → Execution (Fail) → Bug Created →
Bug Fixed → Execution (Pass) → Bug Closed
```

---

### Key Workflow Benefits

✅ **Traceability**: Every bug linked to test case  
✅ **History**: Complete execution history tracked  
✅ **Metrics**: Real-time quality metrics  
✅ **Validation**: Status workflow prevents invalid transitions  
✅ **Automation**: Automated test execution and reporting  
✅ **Visibility**: Dashboard provides instant quality overview

---

## 🎯 Key Features Demonstrated

### Software Quality Assurance Practices

1. **Test-Driven Development**
   - 72 comprehensive automated tests
   - Tests written before and during development
   - Continuous test execution

2. **Code Coverage Analysis**
   - Automated coverage tracking with pytest-cov
   - Per-module coverage breakdown
   - Coverage trends over time

3. **Mutation Testing**
   - Validates test suite effectiveness
   - Identifies weak test assertions
   - Measures test quality beyond coverage

4. **Traceability**
   - Bugs linked to test cases
   - Test executions linked to test cases
   - Complete audit trail

5. **Validation & Error Handling**
   - Server-side input validation
   - Duplicate prevention
   - Status workflow enforcement
   - User-friendly error messages

---

## 📈 Quality Metrics Summary

| Metric                | Value  | Status         |
| --------------------- | ------ | -------------- |
| **Total Tests**       | 72     | ✅ All Passing |
| **Code Coverage**     | 78%    | ✅ Excellent   |
| **Mutation Score**    | 44.2%  | ✅ Good        |
| **Database Coverage** | 100%   | ✅ Perfect     |
| **Critical Modules**  | 89-92% | ✅ Very Good   |

---

## � Configuration Files

### `.coveragerc`

Configures code coverage analysis:

- Tracks `app/` directory
- Excludes tests, templates, and virtual environment
- Generates JSON report for dashboard

### `pytest.ini`

Configures pytest behavior:

- Enables coverage collection
- Generates coverage reports
- Sets test discovery paths

### `mutmut_config.py`

Configures mutation testing:

- Targets `app/routes/` for mutations
- Excludes test files and templates
- Uses pytest as test runner

---

## 📝 Database Schema

### Tables

**bugs**

- `id` (INTEGER PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `description` (TEXT)
- `severity` (TEXT NOT NULL) - Low, Medium, High, Critical
- `status` (TEXT NOT NULL) - Open, In Progress, Resolved, Closed
- `module` (TEXT NOT NULL)
- `test_case_id` (INTEGER) - Foreign key to test_cases
- `created_at` (TIMESTAMP)

**test_cases**

- `id` (INTEGER PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `description` (TEXT)
- `expected_result` (TEXT NOT NULL)
- `created_at` (TIMESTAMP)

**test_executions**

- `id` (INTEGER PRIMARY KEY)
- `test_case_id` (INTEGER NOT NULL) - Foreign key to test_cases
- `result` (TEXT NOT NULL) - Pass, Fail
- `notes` (TEXT)
- `executed_at` (TIMESTAMP)

---

## 🎓 Academic Context

This project demonstrates key Software Quality Assurance concepts:

1. **Test Management**: Systematic approach to test case creation and execution
2. **Defect Tracking**: Complete bug lifecycle management
3. **Traceability**: Links between requirements (test cases) and defects (bugs)
4. **Quality Metrics**: Code coverage and mutation testing
5. **Automation**: Automated testing and quality measurement
6. **Best Practices**: Input validation, error handling, status workflows

---

## 📄 License

This is an academic project for educational purposes.

---

## 👤 Author

Master's Level SQA Project

---

## 🙏 Acknowledgments

- Flask framework for web application development
- pytest for testing framework
- mutmut for mutation testing
- Bootstrap for UI components
