# 📄 FINAL PRODUCT REQUIREMENTS DOCUMENT (PRD)

## AI-Based Dropout Prediction & Counseling System

---

## 1. Product Overview

The AI-Based Dropout Prediction & Counseling System is a consolidated **digital dashboard** that automatically collects student data (attendance, scores, fees, backlogs), applies **rule-based thresholds and machine learning models** to detect at-risk students, and provides **early, data-driven intervention** through regular notifications sent to mentors, parents, and students.

The system performs **constant monitoring** of student activity and ensures that any changes in student performance are instantly reflected on the dashboard along with timely alerts.

---

## 2. Problem Statement

Educational institutions struggle to identify at-risk students early due to manual monitoring, scattered data sources, and lack of predictive tools.
This leads to delayed interventions, reduced student engagement, increased stress, and ultimately higher dropout rates.

A smart, automated system is needed to consolidate student data, detect risks early, and deliver actionable insights to mentors and parents.

---

## 3. Goals & Objectives

### Primary Goals

* Predict student dropout risk early using rule-based + ML logic
* Provide a centralized dashboard with real-time data
* Notify mentors and guardians regularly for early action
* Support students through academic, emotional, and financial counseling

### Secondary Objectives

* Reduce manual workload for teachers
* Improve student academic outcomes
* Enhance parent–teacher communication
* Increase overall retention rate

---

## 4. Target Users

### Primary Users

* Students
* Mentors/Teachers
* Academic Counselors

### Secondary Users

* Parents/Guardians
* Institutional Administration

---

## 5. Key Features & Functional Requirements

---

### A. Consolidated Digital Dashboard

**Description:** Unified dashboard showing all student-related data.
**Features:**

* Attendance, test scores, fee status, backlogs
* Real-time updates whenever new data is entered
* Visual charts using **Chart.js**
* Color-coded indicators (Green, Yellow, Red)

---

### B. Automatic Data Ingestion

**Requirements:**

* Attendance integration (daily)
* Internal assessment scores (weekly updates)
* Fee payment logs
* Backlog/semester results
* Auto-sync using Django scripts / Celery tasks

---

### C. Rule-Based Threshold Engine

**Description:** First-level filtering using simple thresholds.
**Rules Examples:**

* Attendance < 60%
* Continuous score drop
* 2 or more backlogs
* Fee overdue
  Any rule breach generates **instant alert + risk flag**.

---

### D. Machine Learning Prediction

**Models:**

* Logistic Regression
* Decision Tree

**Output:**

* Risk Score (0–100)
* Risk Category (Low / Medium / High)
* Reason for risk (attendance/academics/fees/backlogs)

**Frequency:**

* Daily ML re-evaluation using background Celery tasks
* Weekly summary reports

---

### E. Constant Monitoring System

**Powered By:** Celery + Django
**Functionalities:**

* Runs scheduled tasks every few hours
* Reevaluates risk whenever attendance/score changes
* Triggers instant notifications on high-risk changes

This directly satisfies SIH requirement of:
**"dispatches regular notifications to mentors and guardians through constant monitoring."**

---

### F. Notifications & Alerts

**Features:**

* Daily alerts for high-risk students
* Weekly risk score summary to parents/mentors
* Real-time alerts when risk level increases
* Email/SMS/WhatsApp support
* All alerts dispatched via Celery

---

### G. Counseling & Intervention Module

**Features:**

* Recommended action plan (academic, emotional, financial)
* Booking counseling sessions
* Mentor notes
* Tracking student recovery progress

---

### H. Student Self-Help Portal

**Features:**

* Attendance tracker
* Risk score viewer
* Backlog support resources
* Fee reminders
* Study materials

---

### I. Mentor's Dashboard

**Features:**

* View all at-risk students
* Take action per student
* Contact parents
* Add remarks
* Track student progress over time

---

### J. Admin Panel

**Features:**

* Batch-wise / department-wise risk analytics
* Institution-level retention metrics
* Export reports
* Manage thresholds and ML model settings

---

## 6. Technical Architecture

### Frontend

* React.js
* Chart.js
* Bootstrap / Tailwind
* Responsive UI

### Backend

* Django
* Django REST Framework
* Business logic for rules + ML integration

### Database

* MongoDB

  * Student Records
  * Attendance/Score Logs
  * Risk Scores
  * Notification Logs
  * Counseling History

### Machine Learning Stack

* Logistic Regression
* Decision Tree
* NumPy, Pandas
* Model retraining scripts

### Notifications & Background Processing

* Celery + Redis
* Scheduled tasks (daily/weekly/hourly)
* Real-time triggering on data changes

### Deployment

* Docker Containers
* AWS EC2 / ECS
* GitHub CI/CD

---

## 7. Success Metrics

### Student-Level

* Lower dropout rates
* Improved attendance and test score consistency

### Teacher-Level

* 50–60% less manual monitoring
* Faster identification of at-risk students

### Institution-Level

* Higher retention
* More transparency in student performance tracking
* Improved parent involvement

---

## 8. Risks & Mitigations

| Risk                  | Mitigation                                         |
| --------------------- | -------------------------------------------------- |
| Poor data quality     | Validation filters + fallback rule-based logic     |
| ML model inaccuracies | Regular retraining + hybrid rule+ML approach       |
| Alert overloading     | Smart alert throttling + priority management       |
| Low parent engagement | Multi-channel communication (SMS, email, WhatsApp) |

---

## 9. Project Timeline

| Phase                     | Duration |
| ------------------------- | -------- |
| Requirement Finalization  | 2–3 days |
| UI/UX + Dashboard Design  | 1 week   |
| Backend + API Development | 1 week   |
| ML Model Integration      | 1 week   |
| Notification System       | 4–5 days |
| Testing & QA              | 3 days   |
| Deployment                | 2–3 days |

**Total: ~4–5 Weeks**

---

# ✔ FINAL PRD Completed

This PRD covers:

* Consolidated dashboard
* Automatic ingestion
* ML-based prediction
* Rule-based thresholds
* Constant monitoring
* Regular notifications
* Counseling module
* Fully aligned with SIH problem statement