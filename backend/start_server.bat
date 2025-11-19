#!/bin/bash
# Quick fix script for Django API

# Navigate to backend directory
cd "D:\projects\SIH - 2\ai-dropout-prediction-system\backend"

# Activate virtual environment
call venv\Scripts\activate.bat

# Start Django server
python manage.py runserver 127.0.0.1:8000