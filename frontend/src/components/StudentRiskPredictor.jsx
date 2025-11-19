import React, { useState, useEffect } from 'react';
import axios from 'axios';

const StudentRiskPredictor = () => {
  const [studentId, setStudentId] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [bulkPredictions, setBulkPredictions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState('random_forest');

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await axios.get('/api/students/dashboard-stats/');
      if (response.data.success && response.data.students) {
        setStudents(response.data.students.slice(0, 20));
      }
    } catch (err) {
      console.error('Error fetching students:', err);
    }
  };

  const predictSingleStudent = async () => {
    if (!studentId.trim()) {
      setError('Please enter a student ID');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setPrediction(null);

      const response = await axios.post('/api/students/ml/predict/', {
        student_id: studentId,
        model_name: selectedModel
      });

      if (response.data.success) {
        setPrediction(response.data);
      } else {
        setError(response.data.message || 'Prediction failed');
      }
    } catch (err) {
      setError('Error making prediction: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const predictBulkStudents = async () => {
    try {
      setBulkLoading(true);
      setError(null);

      const response = await axios.post('/api/students/ml/bulk-predict/', {
        model_name: selectedModel,
        limit: 20
      });

      if (response.data.success) {
        const sortedPredictions = response.data.predictions.sort((a, b) => {
          if (a.risk_level === 'high' && b.risk_level !== 'high') return -1;
          if (a.risk_level !== 'high' && b.risk_level === 'high') return 1;
          return b.probability_high_risk - a.probability_high_risk;
        });
        setBulkPredictions(sortedPredictions);
      } else {
        setError(response.data.message || 'Bulk prediction failed');
      }
    } catch (err) {
      setError('Error making bulk predictions: ' + (err.response?.data?.message || err.message));
    } finally {
      setBulkLoading(false);
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

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-success';
    if (confidence >= 0.6) return 'text-warning';
    return 'text-danger';
  };

  return (
    <div className="container-fluid px-4 py-4">
      <div className="mb-4">
        <h1 className="h2 mb-2">
          <i className="fas fa-target text-primary me-2"></i>
          Student Risk Prediction
        </h1>
        <p className="text-muted">
          Predict dropout risk for individual students or analyze multiple students at once
        </p>
      </div>

      {error && (
        <div className="alert alert-danger mb-4" role="alert">
          <i className="fas fa-exclamation-triangle me-2"></i>
          {error}
        </div>
      )}

      {/* Model Selection */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="card-title mb-0">Model Selection</h5>
        </div>
        <div className="card-body">
          <div className="d-flex gap-4">
            <div className="form-check">
              <input
                className="form-check-input"
                type="radio"
                id="random_forest"
                name="model"
                value="random_forest"
                checked={selectedModel === 'random_forest'}
                onChange={(e) => setSelectedModel(e.target.value)}
              />
              <label className="form-check-label" htmlFor="random_forest">
                Random Forest
              </label>
            </div>
            <div className="form-check">
              <input
                className="form-check-input"
                type="radio"
                id="gradient_boosting"
                name="model"
                value="gradient_boosting"
                checked={selectedModel === 'gradient_boosting'}
                onChange={(e) => setSelectedModel(e.target.value)}
              />
              <label className="form-check-label" htmlFor="gradient_boosting">
                Gradient Boosting
              </label>
            </div>
            <div className="form-check">
              <input
                className="form-check-input"
                type="radio"
                id="logistic_regression"
                name="model"
                value="logistic_regression"
                checked={selectedModel === 'logistic_regression'}
                onChange={(e) => setSelectedModel(e.target.value)}
              />
              <label className="form-check-label" htmlFor="logistic_regression">
                Logistic Regression
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4">
        {/* Single Student Prediction */}
        <div className="col-lg-6">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">
                <i className="fas fa-user me-2"></i>
                Single Student Prediction
              </h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label htmlFor="studentId" className="form-label">Student ID</label>
                <div className="input-group">
                  <input
                    type="text"
                    className="form-control"
                    id="studentId"
                    placeholder="Enter student ID (e.g., CS2021001)"
                    value={studentId}
                    onChange={(e) => setStudentId(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && predictSingleStudent()}
                  />
                  <button 
                    className="btn btn-primary"
                    onClick={predictSingleStudent}
                    disabled={loading}
                  >
                    {loading ? (
                      <span className="spinner-border spinner-border-sm" role="status"></span>
                    ) : (
                      <i className="fas fa-search"></i>
                    )}
                  </button>
                </div>
              </div>

              {/* Quick select from available students */}
              {students.length > 0 && (
                <div className="mb-3">
                  <label className="form-label">Quick Select:</label>
                  <div className="d-flex flex-wrap gap-2">
                    {students.slice(0, 6).map((student) => (
                      <button
                        key={student.student_id}
                        className="btn btn-outline-secondary btn-sm"
                        onClick={() => setStudentId(student.student_id)}
                      >
                        {student.student_id}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Single Student Result */}
              {prediction && (
                <div className="border rounded p-3 bg-light">
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <div>
                      <h6 className="fw-semibold mb-1">{prediction.student_name}</h6>
                      <small className="text-muted">ID: {prediction.student_id}</small>
                    </div>
                    <span className={`badge ${getRiskBadgeColor(prediction.prediction.risk_level)}`}>
                      <i className="fas fa-exclamation-triangle me-1"></i>
                      {prediction.prediction.risk_level} Risk
                    </span>
                  </div>

                  <div className="row g-3 small">
                    <div className="col-6">
                      <span className="text-muted">High Risk Probability:</span>
                      <div className="fw-medium text-danger">
                        {(prediction.prediction.probability_high_risk * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="col-6">
                      <span className="text-muted">Low Risk Probability:</span>
                      <div className="fw-medium text-success">
                        {(prediction.prediction.probability_low_risk * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="col-6">
                      <span className="text-muted">Confidence:</span>
                      <div className={`fw-medium ${getConfidenceColor(prediction.prediction.confidence)}`}>
                        {(prediction.prediction.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="col-6">
                      <span className="text-muted">Model Used:</span>
                      <div className="fw-medium text-capitalize">
                        {prediction.prediction.model_used.replace('_', ' ')}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bulk Predictions */}
        <div className="col-lg-6">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">
                <i className="fas fa-users me-2"></i>
                Bulk Predictions
              </h5>
            </div>
            <div className="card-body">
              <button 
                className="btn btn-primary w-100 mb-3"
                onClick={predictBulkStudents}
                disabled={bulkLoading}
              >
                {bulkLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Analyzing Students...
                  </>
                ) : (
                  <>
                    <i className="fas fa-chart-line me-2"></i>
                    Analyze Top 20 Students
                  </>
                )}
              </button>

              {/* Bulk Results */}
              {bulkPredictions.length > 0 && (
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {bulkPredictions.map((pred, index) => (
                    <div key={index} className="border rounded p-2 mb-2 bg-light">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <div>
                          <div className="fw-medium small">{pred.student_name}</div>
                          <small className="text-muted">ID: {pred.student_id}</small>
                        </div>
                        <span className={`badge ${getRiskBadgeColor(pred.risk_level)} small`}>
                          {pred.risk_level}
                        </span>
                      </div>
                      
                      <div className="row g-2">
                        <div className="col-6">
                          <small className="text-muted">High Risk:</small>
                          <span className="fw-medium text-danger ms-1 small">
                            {(pred.probability_high_risk * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="col-6">
                          <small className="text-muted">Confidence:</small>
                          <span className={`fw-medium ms-1 small ${getConfidenceColor(pred.confidence)}`}>
                            {(pred.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Summary Statistics */}
      {bulkPredictions.length > 0 && (
        <div className="card mt-4">
          <div className="card-header">
            <h5 className="card-title mb-0">Prediction Summary</h5>
          </div>
          <div className="card-body">
            <div className="row g-4">
              <div className="col-md-3 text-center">
                <div className="h2 text-danger mb-1">
                  {bulkPredictions.filter(p => p.risk_level === 'high').length}
                </div>
                <small className="text-muted">High Risk</small>
              </div>
              <div className="col-md-3 text-center">
                <div className="h2 text-warning mb-1">
                  {bulkPredictions.filter(p => p.risk_level === 'medium').length}
                </div>
                <small className="text-muted">Medium Risk</small>
              </div>
              <div className="col-md-3 text-center">
                <div className="h2 text-success mb-1">
                  {bulkPredictions.filter(p => p.risk_level === 'low').length}
                </div>
                <small className="text-muted">Low Risk</small>
              </div>
              <div className="col-md-3 text-center">
                <div className="h2 text-primary mb-1">
                  {bulkPredictions.length}
                </div>
                <small className="text-muted">Total Analyzed</small>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentRiskPredictor;