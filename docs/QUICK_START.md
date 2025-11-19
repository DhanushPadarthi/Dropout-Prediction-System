# 🚀 Quick Start Guide

## Prerequisites

Before running the AI-Based Dropout Prediction System, ensure you have the following installed:

- **Python 3.9+**
- **Node.js 16+**
- **MongoDB**
- **Redis**
- **Git**

## Backend Setup (Django)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup:**
   ```bash
   copy .env.example .env
   # Edit .env file with your configuration
   ```

5. **Database setup:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Frontend Setup (React)

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Environment setup:**
   ```bash
   copy .env.example .env
   # Edit .env file with your configuration
   ```

4. **Start development server:**
   ```bash
   npm start
   ```

## ML Models Setup

1. **Navigate to ML models directory:**
   ```bash
   cd ml-models
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate sample data and train models:**
   ```bash
   python scripts/data_preprocessing.py
   python scripts/train_models.py
   ```

## Services Setup

### MongoDB
- Install MongoDB Community Edition
- Start MongoDB service
- Default connection: `mongodb://localhost:27017`

### Redis
- Install Redis
- Start Redis server
- Default connection: `redis://localhost:6379/0`

### Celery (Background Tasks)
```bash
cd backend
celery -A dropout_prediction worker --loglevel=info
```

## Access the Application

1. **Frontend:** http://localhost:3000
2. **Backend API:** http://localhost:8000
3. **Django Admin:** http://localhost:8000/admin

## Default Login Credentials

- **Username:** admin
- **Password:** admin

## Project Structure Overview

```
ai-dropout-prediction-system/
├── backend/          # Django REST API
├── frontend/         # React Application  
├── ml-models/        # Machine Learning Pipeline
├── deployment/       # Docker & CI/CD configs
└── docs/            # Documentation
```

## Key Features

✅ **Real-time Dashboard** - Overview of student risks  
✅ **ML Prediction Models** - Logistic Regression + Decision Tree  
✅ **Rule-based Alerts** - Automated threshold monitoring  
✅ **Multi-channel Notifications** - Email, SMS, WhatsApp  
✅ **Student Management** - Comprehensive student profiles  
✅ **Analytics & Reports** - Detailed performance insights  

## Next Steps

1. Configure your database connections
2. Set up email/SMS services for notifications
3. Train ML models with your data
4. Customize risk thresholds
5. Deploy to production environment

## Support

For issues or questions:
- Check the documentation in `/docs`
- Review the PRD for feature specifications
- Contact the development team

---

**Happy Coding! 🎓✨**