import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MLDashboard = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [featureImportance, setFeatureImportance] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMLData();
  }, []);

  const fetchMLData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch model info
      const modelResponse = await axios.get('/api/students/ml/model-info/');
      setModelInfo(modelResponse.data.model_info);

      // Fetch analytics
      const analyticsResponse = await axios.get('/api/students/ml/analytics/');
      setAnalytics(analyticsResponse.data.analytics);

      // Fetch feature importance if models are trained
      if (modelResponse.data.model_info.is_trained) {
        const featureResponse = await axios.get('/api/students/ml/feature-importance/');
        setFeatureImportance(featureResponse.data.feature_analysis);

        // Fetch recent predictions
        const predictionsResponse = await axios.post('/api/students/ml/bulk-predict/', {
          limit: 10
        });
        setPredictions(predictionsResponse.data.predictions || []);
      }

    } catch (err) {
      setError('Failed to fetch ML data: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const trainModels = async () => {
    try {
      setTraining(true);
      setError(null);

      const response = await axios.post('/api/students/ml/train/');
      
      if (response.data.success) {
        await fetchMLData(); // Refresh data after training
        alert('Models trained successfully!');
      } else {
        setError('Training failed: ' + response.data.message);
      }
    } catch (err) {
      setError('Training failed: ' + (err.response?.data?.message || err.message));
    } finally {
      setTraining(false);
    }
  };

  const getRiskBadgeColor = (riskLevel) => {
    switch (riskLevel) {
      case 'high': return 'bg-danger';
      case 'medium': return 'bg-warning';
      case 'low': return 'bg-success';
      default: return 'bg-secondary';
    }
  };

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center" style={{ minHeight: '400px' }}>
        <div className="text-center">
          <div className="spinner-border text-primary mb-3" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p>Loading ML Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid px-4 py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 mb-2">
            <i className="fas fa-brain text-primary me-2"></i>
            ML Analytics Dashboard
          </h1>
          <p className="text-muted">
            Machine Learning models for dropout risk prediction and analytics
          </p>
        </div>
        
        <div className="d-flex gap-2">
          <button 
            className="btn btn-outline-primary"
            onClick={fetchMLData} 
            disabled={loading}
          >
            <i className="fas fa-sync me-2"></i>
            Refresh
          </button>
          <button 
            className="btn btn-primary"
            onClick={trainModels} 
            disabled={training}
          >
            {training ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Training...
              </>
            ) : (
              <>
                <i className="fas fa-target me-2"></i>
                Train Models
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger mb-4" role="alert">
          <i className="fas fa-exclamation-triangle me-2"></i>
          {error}
        </div>
      )}

      {/* Model Status */}
      <div className="row g-4 mb-4">
        <div className="col-md-6 col-xl-3">
          <div className="card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted small mb-1">Model Status</p>
                  <h3 className="mb-0">
                    {modelInfo?.is_trained ? (
                      <span className="text-success">
                        <i className="fas fa-check-circle me-1"></i>
                        Trained
                      </span>
                    ) : (
                      <span className="text-warning">
                        <i className="fas fa-exclamation-triangle me-1"></i>
                        Not Trained
                      </span>
                    )}
                  </h3>
                </div>
                <i className="fas fa-brain text-primary fs-2"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6 col-xl-3">
          <div className="card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted small mb-1">Available Models</p>
                  <h3 className="mb-0">{modelInfo?.available_models?.length || 0}</h3>
                </div>
                <i className="fas fa-chart-bar text-success fs-2"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6 col-xl-3">
          <div className="card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted small mb-1">High Risk Students</p>
                  <h3 className="mb-0 text-danger">
                    {analytics?.overview?.high_risk_students || 0}
                  </h3>
                </div>
                <i className="fas fa-exclamation-triangle text-danger fs-2"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6 col-xl-3">
          <div className="card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted small mb-1">Total Students</p>
                  <h3 className="mb-0">{analytics?.overview?.total_students || 0}</h3>
                </div>
                <i className="fas fa-users text-primary fs-2"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Model Performance */}
      {modelInfo?.is_trained && modelInfo?.performance_metrics && (
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="card-title mb-0">
              <i className="fas fa-chart-line me-2"></i>
              Model Performance
            </h5>
          </div>
          <div className="card-body">
            <div className="row g-4">
              {Object.entries(modelInfo.performance_metrics).map(([modelName, metrics]) => (
                <div key={modelName} className="col-lg-4">
                  <div className="border rounded p-3">
                    <h6 className="fw-bold mb-3 text-capitalize">
                      {modelName.replace('_', ' ')}
                    </h6>
                    <div className="row g-2">
                      <div className="col-6">
                        <small className="text-muted">Accuracy:</small>
                        <div className="fw-semibold">{(metrics.accuracy * 100).toFixed(1)}%</div>
                      </div>
                      <div className="col-6">
                        <small className="text-muted">Precision:</small>
                        <div className="fw-semibold">{(metrics.precision * 100).toFixed(1)}%</div>
                      </div>
                      <div className="col-6">
                        <small className="text-muted">Recall:</small>
                        <div className="fw-semibold">{(metrics.recall * 100).toFixed(1)}%</div>
                      </div>
                      <div className="col-6">
                        <small className="text-muted">F1 Score:</small>
                        <div className="fw-semibold">{(metrics.f1_score * 100).toFixed(1)}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Feature Importance */}
      {featureImportance?.average_importance && (
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="card-title mb-0">
              <i className="fas fa-chart-bar me-2"></i>
              Feature Importance
            </h5>
          </div>
          <div className="card-body">
            <div className="row g-3">
              {Object.entries(featureImportance.average_importance)
                .slice(0, 8)
                .map(([feature, importance]) => (
                <div key={feature} className="col-12">
                  <div className="d-flex align-items-center justify-content-between">
                    <span className="fw-medium text-capitalize">
                      {feature.replace('_', ' ').replace('encoded', '')}
                    </span>
                    <div className="d-flex align-items-center">
                      <div className="progress me-2" style={{ width: '120px', height: '8px' }}>
                        <div 
                          className="progress-bar bg-primary" 
                          role="progressbar"
                          style={{ width: `${importance * 100}%` }}
                        ></div>
                      </div>
                      <small className="text-muted" style={{ minWidth: '40px' }}>
                        {(importance * 100).toFixed(1)}%
                      </small>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recent Predictions */}
      {predictions.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h5 className="card-title mb-0">
              <i className="fas fa-target me-2"></i>
              Recent High-Risk Predictions
            </h5>
          </div>
          <div className="card-body">
            <div className="row g-3">
              {predictions
                .filter(p => p.risk_level === 'high')
                .slice(0, 5)
                .map((prediction, index) => (
                <div key={index} className="col-12">
                  <div className="d-flex justify-content-between align-items-center p-3 border rounded">
                    <div>
                      <div className="fw-medium">{prediction.student_name}</div>
                      <small className="text-muted">ID: {prediction.student_id}</small>
                    </div>
                    <div className="text-end">
                      <span className={`badge ${getRiskBadgeColor(prediction.risk_level)} mb-1`}>
                        {prediction.risk_level} Risk
                      </span>
                      <div>
                        <small className="text-muted">
                          Confidence: {(prediction.confidence * 100).toFixed(1)}%
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Department Analysis */}
      {analytics?.department_analysis && (
        <div className="card mt-4">
          <div className="card-header">
            <h5 className="card-title mb-0">Department-wise Risk Analysis</h5>
          </div>
          <div className="card-body">
            <div className="row g-4">
              {analytics.department_analysis.map((dept, index) => (
                <div key={index} className="col-md-6">
                  <div className="border rounded p-3">
                    <h6 className="fw-semibold mb-3">{dept.department}</h6>
                    <div className="row g-2 small">
                      <div className="col-6">
                        <span className="text-muted">Total Students:</span>
                        <div className="fw-medium">{dept.total_students}</div>
                      </div>
                      <div className="col-6">
                        <span className="text-muted">High Risk:</span>
                        <div className="fw-medium text-danger">{dept.high_risk}</div>
                      </div>
                      <div className="col-6">
                        <span className="text-muted">Risk Percentage:</span>
                        <div className="fw-medium">{dept.high_risk_percentage}%</div>
                      </div>
                      <div className="col-6">
                        <span className="text-muted">Avg CGPA:</span>
                        <div className="fw-medium">{dept.average_cgpa}</div>
                      </div>
                      <div className="col-12">
                        <span className="text-muted">Avg Attendance:</span>
                        <div className="fw-medium">{dept.average_attendance}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MLDashboard;