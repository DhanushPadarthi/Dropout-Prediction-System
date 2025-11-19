import React, { useState, useEffect } from 'react';
import APIService from '../services/apiService';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('current');

  useEffect(() => {
    fetchAnalytics();
    fetchModelInfo();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await APIService.get('/api/students/ml/analytics/');
      if (response.success) {
        setAnalytics(response);
      } else {
        setError('Failed to fetch analytics data');
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setError('Error fetching analytics data');
    } finally {
      setLoading(false);
    }
  };

  const fetchModelInfo = async () => {
    try {
      const response = await APIService.get('/api/students/ml/model-info/');
      if (response.success) {
        setModelInfo(response);
      }
    } catch (error) {
      console.error('Error fetching model info:', error);
    }
  };

  const getRiskDistributionPercentage = (riskLevel) => {
    if (!analytics || !analytics.analytics || !analytics.analytics.overview) return 0;
    const overview = analytics.analytics.overview;
    const total = overview.total_students || 0;
    if (total === 0) return 0;
    
    let count = 0;
    if (riskLevel === 'high') count = overview.high_risk_students || 0;
    else if (riskLevel === 'medium') count = overview.medium_risk_students || 0;
    else if (riskLevel === 'low') count = overview.low_risk_students || 0;
    
    return ((count / total) * 100).toFixed(1);
  };

  const getModelAccuracyColor = (accuracy) => {
    if (accuracy >= 0.9) return 'success';
    if (accuracy >= 0.8) return 'warning';
    return 'danger';
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        <h4 className="alert-heading">Error</h4>
        <p>{error}</p>
        <button className="btn btn-outline-danger" onClick={fetchAnalytics}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Analytics & Reports</h2>
        <div>
          <select 
            className="form-select d-inline-block w-auto me-2"
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
          >
            <option value="current">Current Semester</option>
            <option value="last6months">Last 6 Months</option>
            <option value="lastyear">Last Year</option>
            <option value="all">All Time</option>
          </select>
          <button className="btn btn-outline-primary">
            <i className="fas fa-download me-2"></i>
            Export Report
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4>{analytics?.analytics?.overview?.total_students || 0}</h4>
                  <p className="mb-0">Total Students</p>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-users fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-danger text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4>{analytics?.analytics?.overview?.high_risk_students || 0}</h4>
                  <p className="mb-0">High Risk Students</p>
                  <small>{getRiskDistributionPercentage('high')}% of total</small>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-exclamation-triangle fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4>{analytics?.analytics?.overview?.medium_risk_students || 0}</h4>
                  <p className="mb-0">Medium Risk Students</p>
                  <small>{getRiskDistributionPercentage('medium')}% of total</small>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-exclamation-circle fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h4>{analytics?.analytics?.overview?.low_risk_students || 0}</h4>
                  <p className="mb-0">Low Risk Students</p>
                  <small>{getRiskDistributionPercentage('low')}% of total</small>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-check-circle fa-2x opacity-75"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Risk Distribution Chart */}
        <div className="col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Risk Distribution</h5>
            </div>
            <div className="card-body">
              <div className="row text-center">
                <div className="col-4">
                  <div className="mb-2">
                    <div className="progress" style={{ height: '8px' }}>
                      <div 
                        className="progress-bar bg-success" 
                        style={{ width: `${getRiskDistributionPercentage('low')}%` }}
                      ></div>
                    </div>
                  </div>
                  <h6 className="text-success">{getRiskDistributionPercentage('low')}%</h6>
                  <small className="text-muted">Low Risk</small>
                </div>
                <div className="col-4">
                  <div className="mb-2">
                    <div className="progress" style={{ height: '8px' }}>
                      <div 
                        className="progress-bar bg-warning" 
                        style={{ width: `${getRiskDistributionPercentage('medium')}%` }}
                      ></div>
                    </div>
                  </div>
                  <h6 className="text-warning">{getRiskDistributionPercentage('medium')}%</h6>
                  <small className="text-muted">Medium Risk</small>
                </div>
                <div className="col-4">
                  <div className="mb-2">
                    <div className="progress" style={{ height: '8px' }}>
                      <div 
                        className="progress-bar bg-danger" 
                        style={{ width: `${getRiskDistributionPercentage('high')}%` }}
                      ></div>
                    </div>
                  </div>
                  <h6 className="text-danger">{getRiskDistributionPercentage('high')}%</h6>
                  <small className="text-muted">High Risk</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Department Performance */}
        <div className="col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Department Performance</h5>
            </div>
            <div className="card-body">
              {analytics?.analytics?.department_analysis && analytics.analytics.department_analysis.map((data) => (
                <div key={data.code} className="mb-3">
                  <div className="d-flex justify-content-between align-items-center mb-1">
                    <span className="fw-medium">{data.department}</span>
                    <span className="text-muted">{data.total_students} students</span>
                  </div>
                  <div className="progress" style={{ height: '6px' }}>
                    <div 
                      className={`progress-bar bg-${data.average_cgpa >= 8 ? 'success' : data.average_cgpa >= 6 ? 'warning' : 'danger'}`}
                      style={{ width: `${(data.average_cgpa / 10) * 100}%` }}
                    ></div>
                  </div>
                  <small className="text-muted">Avg CGPA: {data.average_cgpa?.toFixed(2)} | Attendance: {data.average_attendance?.toFixed(1)}%</small>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ML Model Performance */}
      {modelInfo && (
        <div className="row">
          <div className="col-12 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">ML Model Performance</h5>
              </div>
              <div className="card-body">
                <div className="row">
                  {Object.entries(modelInfo.model_info?.performance_metrics || {}).map(([modelName, modelData]) => (
                    <div key={modelName} className="col-md-4 mb-3">
                      <div className="card border-0 bg-light">
                        <div className="card-body text-center">
                          <h6 className="text-capitalize">{modelName.replace('_', ' ')}</h6>
                          <h4 className={`text-${getModelAccuracyColor(modelData.accuracy)}`}>
                            {(modelData.accuracy * 100).toFixed(1)}%
                          </h4>
                          <p className="text-muted mb-2">Accuracy</p>
                          <div className="row text-center">
                            <div className="col-6">
                              <small className="text-muted">Precision</small>
                              <div className="fw-medium">{(modelData.precision * 100).toFixed(1)}%</div>
                            </div>
                            <div className="col-6">
                              <small className="text-muted">Recall</small>
                              <div className="fw-medium">{(modelData.recall * 100).toFixed(1)}%</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-3">
                  {(() => {
                    const metrics = modelInfo.model_info?.performance_metrics || {};
                    const bestModel = Object.entries(metrics).reduce((best, [name, data]) => 
                      !best || data.f1_score > best.data.f1_score ? { name, data } : best
                    , null);
                    
                    return bestModel ? (
                      <p className="text-muted mb-1">
                        <strong>Best Performing Model:</strong> {bestModel.name.replace('_', ' ')} 
                        ({(bestModel.data.accuracy * 100).toFixed(1)}% accuracy, {(bestModel.data.f1_score * 100).toFixed(1)}% F1)
                      </p>
                    ) : null;
                  })()}
                  <p className="text-muted mb-0">
                    <strong>Last Updated:</strong> {new Date().toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Importance */}
      {modelInfo?.model_info?.feature_importance?.random_forest && (
        <div className="row">
          <div className="col-12 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Feature Importance (Random Forest Model)</h5>
              </div>
              <div className="card-body">
                <p className="text-muted mb-3">Factors most influencing dropout prediction:</p>
                {Object.entries(modelInfo.model_info.feature_importance.random_forest)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 8)
                  .map(([feature, importance]) => (
                    <div key={feature} className="mb-2">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <span className="text-capitalize">{feature.replace('_', ' ')}</span>
                        <span className="text-muted">{(importance * 100).toFixed(1)}%</span>
                      </div>
                      <div className="progress" style={{ height: '4px' }}>
                        <div 
                          className="progress-bar bg-primary"
                          style={{ width: `${importance * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">AI Recommendations</h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-4">
                  <div className="text-center p-3 border rounded">
                    <i className="fas fa-bell text-warning fa-2x mb-2"></i>
                    <h6>Immediate Attention</h6>
                    <p className="text-muted small">
                      {analytics?.analytics?.overview?.high_risk_students || 0} students need immediate intervention
                    </p>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="text-center p-3 border rounded">
                    <i className="fas fa-eye text-info fa-2x mb-2"></i>
                    <h6>Monitor Closely</h6>
                    <p className="text-muted small">
                      {analytics?.analytics?.overview?.medium_risk_students || 0} students should be monitored for early signs
                    </p>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="text-center p-3 border rounded">
                    <i className="fas fa-chart-line text-success fa-2x mb-2"></i>
                    <h6>Performing Well</h6>
                    <p className="text-muted small">
                      {analytics?.analytics?.overview?.low_risk_students || 0} students are on track for success
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;