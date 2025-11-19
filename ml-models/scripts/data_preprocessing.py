"""
Data preprocessing module for dropout prediction ML pipeline
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
import joblib
import logging
from typing import Tuple, Dict, Any
from config import *

# Set up logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Comprehensive data preprocessing pipeline for student dropout prediction
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.numerical_imputer = SimpleImputer(strategy=DATA_CONFIG['missing_value_strategy']['numerical'])
        self.categorical_imputer = SimpleImputer(strategy=DATA_CONFIG['missing_value_strategy']['categorical'])
        self.feature_columns = []
        self.target_column = 'dropout_risk'
        
    def load_data(self, file_path: str = None) -> pd.DataFrame:
        """Load data from CSV file or generate sample data"""
        if file_path and os.path.exists(file_path):
            df = pd.read_csv(file_path)
            logger.info(f"Loaded data from {file_path} with shape {df.shape}")
        else:
            df = self.generate_sample_data()
            logger.info(f"Generated sample data with shape {df.shape}")
        return df
    
    def generate_sample_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate sample student data for training"""
        np.random.seed(42)
        
        data = {}
        
        # Attendance features
        attendance_pct = np.random.normal(75, 15, n_samples)
        data['overall_attendance_percentage'] = np.clip(attendance_pct, 0, 100)
        data['recent_attendance_trend'] = np.random.normal(0, 5, n_samples)
        data['consecutive_absences'] = np.random.poisson(2, n_samples)
        data['attendance_variation'] = np.random.exponential(5, n_samples)
        
        # Academic features
        data['current_cgpa'] = np.random.normal(7.5, 1.2, n_samples)
        data['current_cgpa'] = np.clip(data['current_cgpa'], 0, 10)
        data['semester_gpa'] = data['current_cgpa'] + np.random.normal(0, 0.5, n_samples)
        data['semester_gpa'] = np.clip(data['semester_gpa'], 0, 10)
        data['grade_trend'] = np.random.normal(0, 0.3, n_samples)
        data['failed_subjects'] = np.random.poisson(0.5, n_samples)
        data['backlog_count'] = np.random.poisson(0.8, n_samples)
        data['academic_consistency'] = np.random.exponential(1, n_samples)
        
        # Financial features
        data['fee_payment_percentage'] = np.random.normal(85, 20, n_samples)
        data['fee_payment_percentage'] = np.clip(data['fee_payment_percentage'], 0, 100)
        data['payment_delay_days'] = np.random.exponential(10, n_samples)
        data['financial_assistance'] = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        data['fee_payment_pattern'] = np.random.normal(0.8, 0.2, n_samples)
        
        # Behavioral features
        data['mentor_meeting_frequency'] = np.random.exponential(2, n_samples)
        data['library_usage'] = np.random.exponential(3, n_samples)
        data['extracurricular_participation'] = np.random.exponential(1, n_samples)
        data['disciplinary_actions'] = np.random.poisson(0.2, n_samples)
        
        # Demographic features
        data['semester'] = np.random.choice(range(1, 9), n_samples)
        data['department_dropout_rate'] = np.random.normal(0.1, 0.05, n_samples)
        data['batch_performance'] = np.random.normal(7.2, 0.8, n_samples)
        data['distance_from_home'] = np.random.exponential(50, n_samples)
        
        # Create target variable based on risk factors
        risk_score = self.calculate_risk_score(data)
        data['dropout_risk'] = (risk_score > 50).astype(int)  # Binary classification
        data['risk_score'] = risk_score
        
        df = pd.DataFrame(data)
        
        # Add some missing values to simulate real-world data
        missing_cols = ['mentor_meeting_frequency', 'library_usage', 'extracurricular_participation']
        for col in missing_cols:
            missing_idx = np.random.choice(df.index, size=int(0.1 * len(df)), replace=False)
            df.loc[missing_idx, col] = np.nan
        
        return df
    
    def calculate_risk_score(self, data: Dict) -> np.ndarray:
        """Calculate risk score based on multiple factors"""
        risk_score = np.zeros(len(data['overall_attendance_percentage']))
        
        # Attendance risk (30% weight)
        attendance_risk = np.where(data['overall_attendance_percentage'] < 60, 30,
                                 np.where(data['overall_attendance_percentage'] < 75, 15, 0))
        risk_score += attendance_risk
        
        # Academic risk (35% weight)
        academic_risk = np.where(data['current_cgpa'] < 6, 35,
                               np.where(data['current_cgpa'] < 7, 20, 0))
        risk_score += academic_risk
        
        # Backlog risk (20% weight)
        backlog_risk = np.where(data['backlog_count'] >= 3, 20,
                              np.where(data['backlog_count'] >= 1, 10, 0))
        risk_score += backlog_risk
        
        # Financial risk (15% weight)
        fee_risk = np.where(data['fee_payment_percentage'] < 50, 15,
                          np.where(data['fee_payment_percentage'] < 80, 8, 0))
        risk_score += fee_risk
        
        # Add some randomness
        risk_score += np.random.normal(0, 5, len(risk_score))
        
        return np.clip(risk_score, 0, 100)
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the data"""
        logger.info("Starting data cleaning process")
        
        # Remove duplicates
        initial_shape = df.shape
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows")
        
        # Handle outliers using IQR method
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if col not in ['dropout_risk', 'semester']:  # Don't process target and categorical
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_before = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                df[col] = df[col].clip(lower_bound, upper_bound)
                logger.info(f"Clipped {outliers_before} outliers in {col}")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        logger.info("Handling missing values")
        
        # Separate numerical and categorical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # Handle numerical missing values
        if len(numerical_cols) > 0:
            df[numerical_cols] = self.numerical_imputer.fit_transform(df[numerical_cols])
        
        # Handle categorical missing values
        if len(categorical_cols) > 0:
            df[categorical_cols] = self.categorical_imputer.fit_transform(df[categorical_cols])
        
        logger.info(f"Handled missing values for {len(numerical_cols)} numerical and {len(categorical_cols)} categorical columns")
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create new features from existing ones"""
        logger.info("Starting feature engineering")
        
        # Academic performance ratios
        df['gpa_to_attendance_ratio'] = df['current_cgpa'] / (df['overall_attendance_percentage'] + 1e-5)
        df['performance_consistency'] = df['current_cgpa'] / (df['academic_consistency'] + 1e-5)
        
        # Risk interaction features
        df['attendance_academic_risk'] = (100 - df['overall_attendance_percentage']) * (10 - df['current_cgpa'])
        df['financial_academic_risk'] = (100 - df['fee_payment_percentage']) * (10 - df['current_cgpa'])
        
        # Behavioral engagement score
        df['engagement_score'] = (
            df['mentor_meeting_frequency'] + 
            df['library_usage'] + 
            df['extracurricular_participation']
        ) / 3
        
        # Time-based features
        df['semester_progress'] = df['semester'] / 8.0  # Normalize to 0-1
        df['critical_semester'] = (df['semester'].isin([3, 4, 7, 8])).astype(int)
        
        # Log transforms for skewed features
        for col in DATA_CONFIG['feature_engineering']['log_transform']:
            if col in df.columns:
                df[f'{col}_log'] = np.log1p(df[col])
        
        logger.info(f"Created {len(df.columns) - len(self.feature_columns)} new features")
        return df
    
    def scale_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame = None) -> Tuple[np.ndarray, np.ndarray]:
        """Scale numerical features"""
        logger.info("Scaling features")
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            return X_train_scaled, X_test_scaled
        
        return X_train_scaled
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Complete data preparation pipeline"""
        logger.info("Starting complete data preparation pipeline")
        
        # Clean data
        df = self.clean_data(df)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Separate features and target
        if self.target_column in df.columns:
            y = df[self.target_column].values
            X = df.drop([self.target_column, 'risk_score'], axis=1, errors='ignore')
        else:
            raise ValueError(f"Target column '{self.target_column}' not found in data")
        
        # Store feature columns
        self.feature_columns = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=TRAINING_CONFIG['test_size'], 
            random_state=TRAINING_CONFIG['random_state'],
            stratify=y
        )
        
        # Scale features
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        
        logger.info(f"Data preparation complete. Training set: {X_train_scaled.shape}, Test set: {X_test_scaled.shape}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def save_preprocessors(self):
        """Save fitted preprocessors"""
        joblib.dump(self.scaler, MODEL_PATHS['scaler'])
        joblib.dump(self.numerical_imputer, MODELS_DIR / 'numerical_imputer.joblib')
        joblib.dump(self.categorical_imputer, MODELS_DIR / 'categorical_imputer.joblib')
        
        # Save feature columns
        with open(MODELS_DIR / 'feature_columns.txt', 'w') as f:
            f.write('\n'.join(self.feature_columns))
        
        logger.info("Preprocessors saved successfully")
    
    def load_preprocessors(self):
        """Load fitted preprocessors"""
        try:
            self.scaler = joblib.load(MODEL_PATHS['scaler'])
            self.numerical_imputer = joblib.load(MODELS_DIR / 'numerical_imputer.joblib')
            self.categorical_imputer = joblib.load(MODELS_DIR / 'categorical_imputer.joblib')
            
            # Load feature columns
            with open(MODELS_DIR / 'feature_columns.txt', 'r') as f:
                self.feature_columns = [line.strip() for line in f.readlines()]
            
            logger.info("Preprocessors loaded successfully")
        except FileNotFoundError as e:
            logger.error(f"Preprocessor files not found: {e}")
            raise


def main():
    """Main function to test preprocessing pipeline"""
    preprocessor = DataPreprocessor()
    
    # Generate and save sample data
    df = preprocessor.generate_sample_data(n_samples=2000)
    df.to_csv(DATA_PATHS['sample_data'], index=False)
    logger.info(f"Sample data saved to {DATA_PATHS['sample_data']}")
    
    # Prepare data
    X_train, X_test, y_train, y_test = preprocessor.prepare_data(df)
    
    # Save preprocessors
    preprocessor.save_preprocessors()
    
    # Save processed data
    train_data = pd.DataFrame(X_train, columns=preprocessor.feature_columns)
    train_data['dropout_risk'] = y_train
    train_data.to_csv(DATA_PATHS['training_data'], index=False)
    
    test_data = pd.DataFrame(X_test, columns=preprocessor.feature_columns)
    test_data['dropout_risk'] = y_test
    test_data.to_csv(DATA_PATHS['test_data'], index=False)
    
    logger.info("Data preprocessing pipeline completed successfully")


if __name__ == "__main__":
    main()