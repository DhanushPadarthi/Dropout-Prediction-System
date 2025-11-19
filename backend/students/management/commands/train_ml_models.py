from django.core.management.base import BaseCommand
from ml_models.dropout_prediction import ml_predictor


class Command(BaseCommand):
    help = 'Train machine learning models for dropout prediction'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retrain even if models already exist',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        force = options['force']
        verbose = options['verbose']
        
        self.stdout.write("🚀 Starting ML model training...")
        
        try:
            # Check if models already exist
            if not force:
                try:
                    info = ml_predictor.get_model_info()
                    if info['is_trained']:
                        self.stdout.write(
                            self.style.WARNING(
                                'Models already trained. Use --force to retrain.'
                            )
                        )
                        self.stdout.write("📊 Current model performance:")
                        for model_name, metrics in info['performance_metrics'].items():
                            self.stdout.write(f"  {model_name}: Accuracy {metrics['accuracy']}, F1 {metrics['f1_score']}")
                        return
                except:
                    pass  # Models not trained yet
            
            # Train models
            result = ml_predictor.train_models()
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS('✅ ML models trained successfully!')
                )
                
                self.stdout.write(f"📊 Training completed with {result['training_data_size']} student records")
                self.stdout.write("🎯 Model Performance:")
                
                for model_name, metrics in result['performance'].items():
                    self.stdout.write(f"  📈 {model_name.replace('_', ' ').title()}:")
                    self.stdout.write(f"    • Accuracy: {metrics['accuracy']}")
                    self.stdout.write(f"    • Precision: {metrics['precision']}")
                    self.stdout.write(f"    • Recall: {metrics['recall']}")
                    self.stdout.write(f"    • F1 Score: {metrics['f1_score']}")
                    self.stdout.write("")
                
                if verbose and 'feature_importance' in result:
                    self.stdout.write("🔍 Feature Importance (Random Forest):")
                    rf_importance = result['feature_importance'].get('random_forest', {})
                    sorted_features = sorted(rf_importance.items(), key=lambda x: x[1], reverse=True)
                    
                    for feature, importance in sorted_features[:8]:  # Top 8 features
                        self.stdout.write(f"  • {feature}: {importance:.4f}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Training failed: {result["message"]}')
                )
                if 'error' in result:
                    self.stdout.write(f"Error details: {result['error']}")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error during training: {str(e)}')
            )