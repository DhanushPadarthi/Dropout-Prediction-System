"""
Model training module for dropout prediction ML pipeline
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import joblib
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Any
from data_preprocessing import DataPreprocessor
from config import *

# Set up logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class DropoutPredictor:
    """
    Main class for training and managing dropout prediction models
    """
    
    def __init__(self):
        self.models = {}
        self.ensemble_model = None
        self.preprocessor = DataPreprocessor()
        self.feature_importance = {}
        self.model_performance = {}
        
    def initialize_models(self):
        """Initialize individual models with configured parameters"""
        logger.info("Initializing models")
        
        # Logistic Regression
        self.models['logistic_regression'] = LogisticRegression(
            **MODEL_CONFIG['logistic_regression']['params']
        )
        
        # Decision Tree
        self.models['decision_tree'] = DecisionTreeClassifier(
            **MODEL_CONFIG['decision_tree']['params']
        )
        
        logger.info(f"Initialized {len(self.models)} models")
    
    def tune_hyperparameters(self, X_train: np.ndarray, y_train: np.ndarray):
        """Perform hyperparameter tuning for each model"""
        logger.info("Starting hyperparameter tuning")
        
        # Logistic Regression parameter grid
        lr_param_grid = {
            'C': [0.001, 0.01, 0.1, 1, 10, 100],
            'solver': ['liblinear', 'saga'],
            'penalty': ['l1', 'l2']
        }
        
        # Decision Tree parameter grid
        dt_param_grid = {
            'max_depth': [3, 5, 7, 10, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'criterion': ['gini', 'entropy']
        }
        
        param_grids = {
            'logistic_regression': lr_param_grid,
            'decision_tree': dt_param_grid
        }
        
        tuned_models = {}
        
        for model_name, model in self.models.items():
            logger.info(f"Tuning {model_name}")
            
            grid_search = GridSearchCV(
                model, 
                param_grids[model_name],
                cv=TRAINING_CONFIG['cv_folds'],
                scoring=TRAINING_CONFIG['scoring_metric'],
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            tuned_models[model_name] = grid_search.best_estimator_
            
            logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
            logger.info(f"Best score for {model_name}: {grid_search.best_score_:.4f}")
        
        self.models = tuned_models
        return tuned_models
    
    def train_individual_models(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train individual models"""
        logger.info("Training individual models")
        
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name}")
            
            # Train the model
            model.fit(X_train, y_train)
            
            # Cross-validation score
            cv_scores = cross_val_score(
                model, X_train, y_train, 
                cv=TRAINING_CONFIG['cv_folds'],
                scoring=TRAINING_CONFIG['scoring_metric']
            )
            
            self.model_performance[model_name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'cv_scores': cv_scores
            }
            
            logger.info(f"{model_name} CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            # Extract feature importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[model_name] = model.feature_importances_
            elif hasattr(model, 'coef_'):
                self.feature_importance[model_name] = np.abs(model.coef_[0])
    
    def create_ensemble(self):
        """Create ensemble model using voting classifier"""
        logger.info("Creating ensemble model")
        
        # Create weighted voting classifier
        estimators = [(name, model) for name, model in self.models.items()]
        
        self.ensemble_model = VotingClassifier(
            estimators=estimators,
            voting='soft'  # Use probability voting
        )
        
        logger.info("Ensemble model created")
    
    def train_ensemble(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the ensemble model"""
        logger.info("Training ensemble model")
        
        self.ensemble_model.fit(X_train, y_train)
        
        # Cross-validation for ensemble
        cv_scores = cross_val_score(
            self.ensemble_model, X_train, y_train,
            cv=TRAINING_CONFIG['cv_folds'],
            scoring=TRAINING_CONFIG['scoring_metric']
        )
        
        self.model_performance['ensemble'] = {
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_scores': cv_scores
        }
        
        logger.info(f"Ensemble CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    def evaluate_models(self, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate all models on test set"""
        logger.info("Evaluating models on test set")
        
        evaluation_results = {}
        
        # Evaluate individual models
        for model_name, model in self.models.items():
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            evaluation_results[model_name] = {
                'accuracy': model.score(X_test, y_test),
                'roc_auc': roc_auc_score(y_test, y_pred_proba),
                'classification_report': classification_report(y_test, y_pred),
                'confusion_matrix': confusion_matrix(y_test, y_pred)
            }
            
            logger.info(f"{model_name} Test Accuracy: {evaluation_results[model_name]['accuracy']:.4f}")
            logger.info(f"{model_name} Test ROC-AUC: {evaluation_results[model_name]['roc_auc']:.4f}")
        
        # Evaluate ensemble model
        if self.ensemble_model:
            y_pred_ensemble = self.ensemble_model.predict(X_test)
            y_pred_proba_ensemble = self.ensemble_model.predict_proba(X_test)[:, 1]
            
            evaluation_results['ensemble'] = {
                'accuracy': self.ensemble_model.score(X_test, y_test),
                'roc_auc': roc_auc_score(y_test, y_pred_proba_ensemble),
                'classification_report': classification_report(y_test, y_pred_ensemble),
                'confusion_matrix': confusion_matrix(y_test, y_pred_ensemble)
            }
            
            logger.info(f"Ensemble Test Accuracy: {evaluation_results['ensemble']['accuracy']:.4f}")
            logger.info(f"Ensemble Test ROC-AUC: {evaluation_results['ensemble']['roc_auc']:.4f}")
        
        return evaluation_results
    
    def predict_dropout_risk(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict dropout risk for a single student
        
        Args:
            student_data: Dictionary containing student features
            
        Returns:
            Dictionary with risk score, category, and individual model predictions
        """
        # Convert to DataFrame for preprocessing
        df = pd.DataFrame([student_data])
        
        # Preprocess the data
        # Note: In production, you'd need to handle this more carefully
        # to ensure consistent feature engineering
        
        # Get predictions from individual models
        predictions = {}
        probabilities = {}
        
        for model_name, model in self.models.items():
            pred = model.predict(df)[0]
            pred_proba = model.predict_proba(df)[0, 1]
            
            predictions[model_name] = pred
            probabilities[model_name] = pred_proba
        
        # Get ensemble prediction
        if self.ensemble_model:
            ensemble_pred = self.ensemble_model.predict(df)[0]
            ensemble_proba = self.ensemble_model.predict_proba(df)[0, 1]
            
            predictions['ensemble'] = ensemble_pred
            probabilities['ensemble'] = ensemble_proba
        
        # Calculate weighted risk score
        weights = PREDICTION_CONFIG['weights']
        weighted_score = (
            probabilities['logistic_regression'] * weights['logistic_regression'] +
            probabilities['decision_tree'] * weights['decision_tree']
        )
        
        # Convert to 0-100 scale
        risk_score = weighted_score * 100
        
        # Determine risk category
        if risk_score <= PREDICTION_CONFIG['risk_categories']['low'][1]:
            risk_category = 'low'
        elif risk_score <= PREDICTION_CONFIG['risk_categories']['medium'][1]:
            risk_category = 'medium'
        else:
            risk_category = 'high'
        
        return {
            'risk_score': risk_score,
            'risk_category': risk_category,
            'individual_predictions': predictions,
            'individual_probabilities': probabilities,
            'confidence': max(probabilities.values()) - min(probabilities.values())
        }
    
    def save_models(self):
        """Save trained models to disk"""
        logger.info("Saving models")
        
        # Save individual models
        for model_name, model in self.models.items():
            model_path = MODEL_PATHS[model_name]
            joblib.dump(model, model_path)
            logger.info(f"Saved {model_name} to {model_path}")
        
        # Save ensemble model
        if self.ensemble_model:
            ensemble_path = MODELS_DIR / 'ensemble_model.joblib'
            joblib.dump(self.ensemble_model, ensemble_path)
            logger.info(f"Saved ensemble model to {ensemble_path}")
        
        # Save feature importance
        importance_path = MODELS_DIR / 'feature_importance.joblib'
        joblib.dump(self.feature_importance, importance_path)
        
        # Save model performance
        performance_path = MODELS_DIR / 'model_performance.joblib'
        joblib.dump(self.model_performance, performance_path)
        
        logger.info("All models saved successfully")
    
    def load_models(self):
        """Load trained models from disk"""
        logger.info("Loading models")
        
        try:
            # Load individual models
            for model_name in MODEL_CONFIG.keys():
                model_path = MODEL_PATHS[model_name]
                self.models[model_name] = joblib.load(model_path)
                logger.info(f"Loaded {model_name} from {model_path}")
            
            # Load ensemble model
            ensemble_path = MODELS_DIR / 'ensemble_model.joblib'
            if ensemble_path.exists():
                self.ensemble_model = joblib.load(ensemble_path)
                logger.info(f"Loaded ensemble model from {ensemble_path}")
            
            # Load feature importance
            importance_path = MODELS_DIR / 'feature_importance.joblib'
            if importance_path.exists():
                self.feature_importance = joblib.load(importance_path)
            
            # Load model performance
            performance_path = MODELS_DIR / 'model_performance.joblib'
            if performance_path.exists():
                self.model_performance = joblib.load(performance_path)
            
            logger.info("Models loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Model files not found: {e}")
            raise
    
    def plot_feature_importance(self, feature_names: list):
        """Plot feature importance for all models"""
        if not self.feature_importance:
            logger.warning("No feature importance data available")
            return
        
        n_models = len(self.feature_importance)
        fig, axes = plt.subplots(1, n_models, figsize=(15, 5))
        
        if n_models == 1:
            axes = [axes]
        
        for idx, (model_name, importance) in enumerate(self.feature_importance.items()):
            # Get top 10 features
            top_indices = np.argsort(importance)[-10:]
            top_features = [feature_names[i] for i in top_indices]
            top_importance = importance[top_indices]
            
            axes[idx].barh(range(len(top_features)), top_importance)
            axes[idx].set_yticks(range(len(top_features)))
            axes[idx].set_yticklabels(top_features)
            axes[idx].set_title(f'{model_name} Feature Importance')
            axes[idx].set_xlabel('Importance')
        
        plt.tight_layout()
        plt.savefig(MODELS_DIR / 'feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def full_training_pipeline(self, data_path: str = None):
        """Complete training pipeline"""
        logger.info("Starting full training pipeline")
        
        # Load and prepare data
        df = self.preprocessor.load_data(data_path)
        X_train, X_test, y_train, y_test = self.preprocessor.prepare_data(df)
        
        # Initialize models
        self.initialize_models()
        
        # Tune hyperparameters
        self.tune_hyperparameters(X_train, y_train)
        
        # Train individual models
        self.train_individual_models(X_train, y_train)
        
        # Create and train ensemble
        self.create_ensemble()
        self.train_ensemble(X_train, y_train)
        
        # Evaluate models
        evaluation_results = self.evaluate_models(X_test, y_test)
        
        # Save everything
        self.save_models()
        self.preprocessor.save_preprocessors()
        
        # Plot feature importance
        self.plot_feature_importance(self.preprocessor.feature_columns)
        
        logger.info("Full training pipeline completed successfully")
        
        return evaluation_results


def main():
    """Main function to run the training pipeline"""
    predictor = DropoutPredictor()
    
    # Run full training pipeline
    results = predictor.full_training_pipeline()
    
    # Print summary
    print("\n" + "="*50)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("="*50)
    
    for model_name, metrics in results.items():
        print(f"\n{model_name.upper()} RESULTS:")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    
    print("\nModels saved to:", MODELS_DIR)


if __name__ == "__main__":
    main()