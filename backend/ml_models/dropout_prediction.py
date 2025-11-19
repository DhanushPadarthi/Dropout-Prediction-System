import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import os
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

try:
    from students.models_mongo import Student, Department, Batch, Attendance
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    from students.models import Student, Department, Batch


class DropoutPredictionML:
    """
    Machine Learning models for dropout prediction
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        self.is_trained = False
        
        # Define feature columns
        self.feature_columns = [
            'current_semester', 'cgpa', 'attendance_percentage', 'family_income',
            'distance_from_home', 'is_hosteler_encoded', 'gender_encoded',
            'department_encoded', 'age', 'fee_payment_ratio'
        ]
        
        # Initialize models
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=1000
            ),
            'decision_tree': DecisionTreeClassifier(
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            ),
            'support_vector_machine': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=500,
                random_state=42
            ),
            'naive_bayes': GaussianNB()
        }
        
        self.scalers = {name: StandardScaler() for name in self.models.keys()}
    
    def prepare_data_from_mongodb(self):
        """Fetch and prepare data from MongoDB"""
        if not MONGODB_AVAILABLE:
            raise Exception("MongoDB not available")
        
        students = list(Student.objects.all())
        
        if len(students) < 10:
            raise Exception("Not enough student data for training (minimum 10 required)")
        
        data = []
        for student in students:
            try:
                # Calculate age
                if student.date_of_birth:
                    age = (date.today() - student.date_of_birth).days / 365.25
                else:
                    age = 20  # Default age
                
                # Calculate fee payment ratio
                if student.total_fee_amount > 0:
                    fee_payment_ratio = student.paid_amount / student.total_fee_amount
                else:
                    fee_payment_ratio = 1.0  # Assume paid if no fee amount
                
                student_data = {
                    'student_id': student.student_id,
                    'current_semester': student.current_semester,
                    'cgpa': student.cgpa,
                    'attendance_percentage': student.attendance_percentage,
                    'family_income': student.family_income or 500000,  # Default if None
                    'distance_from_home': student.distance_from_home or 50,  # Default if None
                    'is_hosteler': student.is_hosteler,
                    'gender': student.gender,
                    'department': student.batch.department.code,
                    'age': age,
                    'fee_payment_ratio': fee_payment_ratio,
                    'current_risk_score': student.current_risk_score,
                    'risk_category': student.risk_category,
                    'is_active': student.is_active
                }
                data.append(student_data)
                
            except Exception as e:
                print(f"Error processing student {student.student_id}: {e}")
                continue
        
        df = pd.DataFrame(data)
        return df
    
    def prepare_features(self, df):
        """Prepare features for ML training"""
        # Create binary target variable (1 = high risk, 0 = low/medium risk)
        df['dropout_risk'] = (df['risk_category'] == 'high').astype(int)
        
        # Encode categorical variables
        if 'gender_encoder' not in self.label_encoders:
            self.label_encoders['gender_encoder'] = LabelEncoder()
            df['gender_encoded'] = self.label_encoders['gender_encoder'].fit_transform(df['gender'])
        else:
            df['gender_encoded'] = self.label_encoders['gender_encoder'].transform(df['gender'])
        
        if 'department_encoder' not in self.label_encoders:
            self.label_encoders['department_encoder'] = LabelEncoder()
            df['department_encoded'] = self.label_encoders['department_encoder'].fit_transform(df['department'])
        else:
            df['department_encoded'] = self.label_encoders['department_encoder'].transform(df['department'])
        
        # Encode boolean variables
        df['is_hosteler_encoded'] = df['is_hosteler'].astype(int)
        
        # Handle missing values
        df = df.fillna({
            'family_income': df['family_income'].median(),
            'distance_from_home': df['distance_from_home'].median(),
            'age': 20
        })
        
        return df
    
    def train_models(self):
        """Train all ML models"""
        try:
            # Prepare data
            df = self.prepare_data_from_mongodb()
            df = self.prepare_features(df)
            
            print(f"📊 Training with {len(df)} student records")
            print(f"🎯 Target distribution: {df['dropout_risk'].value_counts().to_dict()}")
            
            # Prepare features and target
            X = df[self.feature_columns]
            y = df['dropout_risk']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            print(f"📚 Training set: {len(X_train)}, Test set: {len(X_test)}")
            
            # Train each model
            for model_name, model in self.models.items():
                print(f"🤖 Training {model_name}...")
                
                # Scale features for models that need it
                if model_name in ['logistic_regression']:
                    X_train_scaled = self.scalers[model_name].fit_transform(X_train)
                    X_test_scaled = self.scalers[model_name].transform(X_test)
                    
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                self.model_performance[model_name] = {
                    'accuracy': round(accuracy, 4),
                    'precision': round(precision, 4),
                    'recall': round(recall, 4),
                    'f1_score': round(f1, 4),
                    'training_date': datetime.now().isoformat()
                }
                
                # Feature importance (for tree-based models)
                if hasattr(model, 'feature_importances_'):
                    importance_dict = dict(zip(self.feature_columns, model.feature_importances_))
                    self.feature_importance[model_name] = importance_dict
                
                print(f"✅ {model_name} - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
            
            self.is_trained = True
            self.save_models()
            
            return {
                'success': True,
                'message': 'Models trained successfully',
                'performance': self.model_performance,
                'feature_importance': self.feature_importance,
                'training_data_size': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error training models'
            }
    
    def predict_dropout_risk(self, student_data, model_name='random_forest'):
        """Predict dropout risk for a single student"""
        try:
            if not self.is_trained:
                self.load_models()
            
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not available")
            
            # Prepare features
            features = []
            for column in self.feature_columns:
                if column == 'gender_encoded':
                    features.append(self.label_encoders['gender_encoder'].transform([student_data['gender']])[0])
                elif column == 'department_encoded':
                    features.append(self.label_encoders['department_encoder'].transform([student_data['department']])[0])
                elif column == 'is_hosteler_encoded':
                    features.append(int(student_data['is_hosteler']))
                else:
                    features.append(student_data[column.replace('_encoded', '')])
            
            X = np.array(features).reshape(1, -1)
            
            # Scale if needed
            if model_name in ['logistic_regression']:
                X = self.scalers[model_name].transform(X)
            
            # Predict
            model = self.models[model_name]
            prediction = model.predict(X)[0]
            probability = model.predict_proba(X)[0]
            
            return {
                'prediction': int(prediction),
                'probability_low_risk': round(probability[0], 4),
                'probability_high_risk': round(probability[1], 4),
                'risk_level': 'high' if prediction == 1 else 'low',
                'confidence': round(max(probability), 4),
                'model_used': model_name
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'prediction': None
            }
    
    def bulk_predict(self, student_ids=None, model_name='random_forest'):
        """Predict dropout risk for multiple students"""
        try:
            if not MONGODB_AVAILABLE:
                raise Exception("MongoDB not available")
            
            if student_ids:
                students = [Student.objects.get(student_id=sid) for sid in student_ids]
            else:
                students = list(Student.objects.all()[:50])  # Limit to 50 for performance
            
            predictions = []
            for student in students:
                # Prepare student data
                age = (date.today() - student.date_of_birth).days / 365.25 if student.date_of_birth else 20
                fee_payment_ratio = (student.paid_amount / student.total_fee_amount) if student.total_fee_amount > 0 else 1.0
                
                student_data = {
                    'current_semester': student.current_semester,
                    'cgpa': student.cgpa,
                    'attendance_percentage': student.attendance_percentage,
                    'family_income': student.family_income or 500000,
                    'distance_from_home': student.distance_from_home or 50,
                    'is_hosteler': student.is_hosteler,
                    'gender': student.gender,
                    'department': student.batch.department.code,
                    'age': age,
                    'fee_payment_ratio': fee_payment_ratio
                }
                
                prediction = self.predict_dropout_risk(student_data, model_name)
                prediction['student_id'] = student.student_id
                prediction['student_name'] = f"{student.first_name} {student.last_name}"
                predictions.append(prediction)
            
            return {
                'success': True,
                'predictions': predictions,
                'total_analyzed': len(predictions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            models_dir = 'ml_models'
            os.makedirs(models_dir, exist_ok=True)
            
            # Save models
            for name, model in self.models.items():
                joblib.dump(model, f'{models_dir}/{name}_model.pkl')
            
            # Save scalers
            for name, scaler in self.scalers.items():
                joblib.dump(scaler, f'{models_dir}/{name}_scaler.pkl')
            
            # Save label encoders
            for name, encoder in self.label_encoders.items():
                joblib.dump(encoder, f'{models_dir}/{name}.pkl')
            
            # Save performance metrics
            joblib.dump(self.model_performance, f'{models_dir}/performance_metrics.pkl')
            joblib.dump(self.feature_importance, f'{models_dir}/feature_importance.pkl')
            
            print("💾 Models saved successfully")
            
        except Exception as e:
            print(f"❌ Error saving models: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            models_dir = 'ml_models'
            
            if not os.path.exists(models_dir):
                raise Exception("No trained models found. Please train models first.")
            
            # Load models
            for name in self.models.keys():
                model_path = f'{models_dir}/{name}_model.pkl'
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
            
            # Load scalers
            for name in self.scalers.keys():
                scaler_path = f'{models_dir}/{name}_scaler.pkl'
                if os.path.exists(scaler_path):
                    self.scalers[name] = joblib.load(scaler_path)
            
            # Load label encoders
            encoder_files = ['gender_encoder.pkl', 'department_encoder.pkl']
            for encoder_file in encoder_files:
                encoder_path = f'{models_dir}/{encoder_file}'
                if os.path.exists(encoder_path):
                    encoder_name = encoder_file.replace('.pkl', '')
                    self.label_encoders[encoder_name] = joblib.load(encoder_path)
            
            # Load performance metrics
            performance_path = f'{models_dir}/performance_metrics.pkl'
            if os.path.exists(performance_path):
                self.model_performance = joblib.load(performance_path)
            
            importance_path = f'{models_dir}/feature_importance.pkl'
            if os.path.exists(importance_path):
                self.feature_importance = joblib.load(importance_path)
            
            self.is_trained = True
            print("📚 Models loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise e
    
    def get_model_info(self):
        """Get information about trained models"""
        try:
            if not self.is_trained:
                self.load_models()
            
            return {
                'is_trained': self.is_trained,
                'available_models': list(self.models.keys()),
                'performance_metrics': self.model_performance,
                'feature_importance': self.feature_importance,
                'feature_columns': self.feature_columns
            }
            
        except Exception as e:
            return {
                'is_trained': False,
                'error': str(e)
            }


# Global ML instance
ml_predictor = DropoutPredictionML()