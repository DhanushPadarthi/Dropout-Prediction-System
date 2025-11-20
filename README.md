# 🎓 AI-Based Dropout Prediction & Counseling System

## Overview

A comprehensive digital dashboard that automatically collects student data (attendance, scores, fees, backlogs), applies rule-based thresholds and machine learning models to detect at-risk students, and provides early, data-driven intervention through regular notifications sent to mentors, parents, and students.

## 🏗️ System Architecture

```
Frontend (React + Chart.js)
    ↓
Backend (Django REST API)
    ↓
Database (MongoDB)
    ↓
ML Pipeline (Logistic Regression + Decision Tree)
    ↓
Notification System (Celery + Redis)
```

## 📁 Project Structure

```
ai-dropout-prediction-system/
├── backend/                 # Django REST API
│   ├── apps/               # Django apps
│   ├── config/             # Settings & configurations
│   ├── requirements.txt    # Python dependencies
│   └── manage.py          # Django management
├── frontend/               # React application
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
├── ml-models/             # Machine learning pipeline
│   ├── models/            # Trained models
│   ├── data/              # Training data
│   └── scripts/           # Training scripts
├── deployment/            # Docker & CI/CD
│   ├── docker/            # Docker configurations
│   └── aws/               # AWS deployment scripts
└── docs/                  # Documentation
```

## 🚀 Key Features

- **Consolidated Digital Dashboard**: Unified view of all student data
- **Automatic Data Ingestion**: Real-time data synchronization
- **Rule-Based Threshold Engine**: Instant alerts on threshold breaches
- **ML Prediction Models**: Logistic Regression + Decision Tree
- **Constant Monitoring**: Celery-powered background tasks
- **Multi-Channel Notifications**: Email, SMS, WhatsApp alerts
- **Counseling Module**: Intervention tracking and support
- **Role-Based Dashboards**: Student, Mentor, Admin interfaces

## 🛠️ Tech Stack

### Frontend
- **React.js** - UI framework
- **Chart.js** - Data visualization
- **Bootstrap/Tailwind** - Responsive design
- **Axios** - API communication

### Backend
- **Django** - Web framework
- **Django REST Framework** - API development
- **MongoDB** - Database
- **Celery + Redis** - Background tasks & caching

### Machine Learning
- **Logistic Regression** - Primary prediction model
- **Decision Tree** - Secondary model
- **NumPy & Pandas** - Data processing
- **Scikit-learn** - ML framework

### DevOps
- **Docker** - Containerization
- **AWS EC2/ECS** - Deployment
- **GitHub Actions** - CI/CD pipeline

## 📊 Success Metrics

- **Student-Level**: Lower dropout rates, improved attendance
- **Teacher-Level**: 50-60% less manual monitoring
- **Institution-Level**: Higher retention, better parent involvement

## 🎯 Target Users

- **Primary**: Students, Mentors/Teachers, Academic Counselors
- **Secondary**: Parents/Guardians, Administration

## 📅 Development Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Requirements & Setup | 2-3 days | ✅ |
| UI/UX + Dashboard | 1 week | 🔄 |
| Backend + API | 1 week | 🔄 |
| ML Integration | 1 week | 🔄 |
| Notification System | 4-5 days | 🔄 |
| Testing & QA | 3 days | ⏳ |
| Deployment | 2-3 days | ⏳ |

**Total: ~4-5 Weeks**

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB
- Redis

### Backend Setup
```bash
cd backend
venv\scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### ML Pipeline
```bash
cd ml-models
python train_models.py
```

## 🔧 Configuration

Environment variables and configuration files are located in:
- Backend: `backend/config/settings/`
- Frontend: `frontend/.env`
- ML: `ml-models/config.py`

## 📞 Support

For questions or support, please contact the development team.

---

**Developed for Smart India Hackathon 2024**
