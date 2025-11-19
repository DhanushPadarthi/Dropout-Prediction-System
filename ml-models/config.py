"""
Configuration file for ML models and data processing
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data'
SCRIPTS_DIR = BASE_DIR / 'scripts'

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)

# Model Configuration
MODEL_CONFIG = {
    'logistic_regression': {
        'name': 'Logistic Regression',
        'file_name': 'logistic_regression_model.joblib',
        'params': {
            'random_state': 42,
            'max_iter': 1000,
            'solver': 'liblinear'
        }
    },
    'decision_tree': {
        'name': 'Decision Tree',
        'file_name': 'decision_tree_model.joblib',
        'params': {
            'random_state': 42,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 3
        }
    }
}

# Feature Configuration
FEATURE_CONFIG = {
    'attendance_features': {
        'overall_attendance_percentage': 'float',
        'recent_attendance_trend': 'float',  # Last 30 days trend
        'consecutive_absences': 'int',
        'attendance_variation': 'float',  # Standard deviation
    },
    'academic_features': {
        'current_cgpa': 'float',
        'semester_gpa': 'float',
        'grade_trend': 'float',  # Improvement/decline trend
        'failed_subjects': 'int',
        'backlog_count': 'int',
        'academic_consistency': 'float',  # Performance variation
    },
    'financial_features': {
        'fee_payment_percentage': 'float',
        'payment_delay_days': 'int',
        'financial_assistance': 'bool',
        'fee_payment_pattern': 'float',  # Regularity score
    },
    'behavioral_features': {
        'mentor_meeting_frequency': 'float',
        'library_usage': 'float',
        'extracurricular_participation': 'float',
        'disciplinary_actions': 'int',
    },
    'demographic_features': {
        'semester': 'int',
        'department_dropout_rate': 'float',
        'batch_performance': 'float',
        'distance_from_home': 'float',
    }
}

# Risk Thresholds
RISK_THRESHOLDS = {
    'attendance': {
        'high_risk': 60.0,      # Below 60%
        'medium_risk': 75.0,    # Between 60-75%
    },
    'academic': {
        'high_risk': 6.0,       # CGPA below 6.0
        'medium_risk': 7.0,     # CGPA between 6.0-7.0
    },
    'backlogs': {
        'high_risk': 3,         # 3 or more backlogs
        'medium_risk': 1,       # 1-2 backlogs
    },
    'fees': {
        'high_risk': 90,        # More than 90 days overdue
        'medium_risk': 30,      # 30-90 days overdue
    }
}

# Model Training Configuration
TRAINING_CONFIG = {
    'test_size': 0.2,
    'validation_size': 0.1,
    'random_state': 42,
    'cv_folds': 5,
    'scoring_metric': 'roc_auc',
    'feature_selection': {
        'method': 'recursive_feature_elimination',
        'n_features': 15
    }
}

# Data Processing Configuration
DATA_CONFIG = {
    'missing_value_strategy': {
        'numerical': 'median',
        'categorical': 'mode'
    },
    'scaling_method': 'standard',  # or 'minmax', 'robust'
    'outlier_detection': {
        'method': 'iqr',
        'threshold': 1.5
    },
    'feature_engineering': {
        'polynomial_features': False,
        'interaction_features': True,
        'log_transform': ['fee_payment_percentage', 'attendance_percentage']
    }
}

# Prediction Configuration
PREDICTION_CONFIG = {
    'ensemble_method': 'weighted_average',  # or 'voting', 'stacking'
    'weights': {
        'logistic_regression': 0.6,
        'decision_tree': 0.4
    },
    'risk_score_range': (0, 100),
    'risk_categories': {
        'low': (0, 30),
        'medium': (30, 70),
        'high': (70, 100)
    }
}

# Monitoring and Retraining Configuration
MONITORING_CONFIG = {
    'model_performance_threshold': 0.75,  # Minimum AUC score
    'data_drift_threshold': 0.1,
    'retrain_frequency_days': 30,
    'minimum_new_samples': 100,
    'alert_thresholds': {
        'performance_drop': 0.05,
        'prediction_confidence': 0.7
    }
}

# File paths
MODEL_PATHS = {
    'logistic_regression': MODELS_DIR / MODEL_CONFIG['logistic_regression']['file_name'],
    'decision_tree': MODELS_DIR / MODEL_CONFIG['decision_tree']['file_name'],
    'scaler': MODELS_DIR / 'feature_scaler.joblib',
    'feature_selector': MODELS_DIR / 'feature_selector.joblib',
    'label_encoder': MODELS_DIR / 'label_encoder.joblib'
}

DATA_PATHS = {
    'raw_data': DATA_DIR / 'raw_student_data.csv',
    'processed_data': DATA_DIR / 'processed_student_data.csv',
    'training_data': DATA_DIR / 'training_data.csv',
    'test_data': DATA_DIR / 'test_data.csv',
    'sample_data': DATA_DIR / 'sample_data.csv'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': BASE_DIR / 'logs' / 'ml_pipeline.log'
}

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)