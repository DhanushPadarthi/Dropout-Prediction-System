import React, { useState, useEffect } from 'react';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js';
import APIService from '../services/apiService';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    totalStudents: 0,
    highRiskStudents: 0,
    mediumRiskStudents: 0,
    lowRiskStudents: 0,
    attendanceAlerts: 0,
    academicAlerts: 0,
    financialAlerts: 0
  });

  const [, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load dashboard statistics
      const stats = await APIService.get('/api/students/dashboard-stats/');
      if (stats.success && stats.data) {
        setDashboardData({
          totalStudents: stats.data.total_students || 0,
          highRiskStudents: stats.data.high_risk_students || 0,
          mediumRiskStudents: stats.data.medium_risk_students || 0,
          lowRiskStudents: stats.data.low_risk_students || 0,
          attendanceAlerts: 0, // Will be updated when attendance data is available
          academicAlerts: 0, // Placeholder for backlog data
          financialAlerts: 0 // Placeholder for future implementation
        });
      }

      // Load analytics data
      const analytics = await APIService.get('/api/students/ml/analytics/');
      if (analytics.success) {
        setAnalyticsData(analytics);
      }

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data. Please check if the backend server is running.');
      
      // Set fallback data in case of error
      setDashboardData({
        totalStudents: 0,
        highRiskStudents: 0,
        mediumRiskStudents: 0,
        lowRiskStudents: 0,
        attendanceAlerts: 0,
        academicAlerts: 0,
        financialAlerts: 0
      });
    } finally {
      setLoading(false);
    }
  };

  // Risk Distribution Chart Data
  const riskDistributionData = {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [
      {
        data: [dashboardData.lowRiskStudents, dashboardData.mediumRiskStudents, dashboardData.highRiskStudents],
        backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
        borderColor: ['#1e7e34', '#e0a800', '#c82333'],
        borderWidth: 2
      }
    ]
  };

  // Trend Chart Data
  const trendData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'High Risk Students',
        data: [65, 72, 80, 85, 89, 89],
        borderColor: '#dc3545',
        backgroundColor: 'rgba(220, 53, 69, 0.1)',
        tension: 0.4
      },
      {
        label: 'Medium Risk Students',
        data: [140, 145, 152, 158, 160, 156],
        borderColor: '#ffc107',
        backgroundColor: 'rgba(255, 193, 7, 0.1)',
        tension: 0.4
      }
    ]
  };

  // Alert Types Chart Data
  const alertTypesData = {
    labels: ['Attendance', 'Academic', 'Financial'],
    datasets: [
      {
        label: 'Number of Alerts',
        data: [dashboardData.attendanceAlerts, dashboardData.academicAlerts, dashboardData.financialAlerts],
        backgroundColor: ['#17a2b8', '#6f42c1', '#fd7e14'],
        borderColor: ['#138496', '#5a2d91', '#e8690b'],
        borderWidth: 1
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-container d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <div className="text-center">
          <div className="spinner-border text-primary mb-3" role="status" style={{ width: '3rem', height: '3rem' }}>
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="text-muted">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Error Alert */}
      {error && (
        <div className="alert alert-warning alert-dismissible fade show mb-4" role="alert">
          <i className="fas fa-exclamation-triangle me-2"></i>
          {error}
          <button 
            type="button" 
            className="btn-close" 
            onClick={() => setError(null)}
            aria-label="Close"
          ></button>
        </div>
      )}

      {/* Connection Status */}
      <div className="row mb-3">
        <div className="col-12">
          <div className={`alert ${error ? 'alert-danger' : 'alert-success'} mb-0 py-2`}>
            <i className={`fas ${error ? 'fa-times-circle' : 'fa-check-circle'} me-2`}></i>
            Backend Status: {error ? 'Disconnected' : 'Connected'}
            {!error && (
              <button 
                className="btn btn-sm btn-outline-success ms-2"
                onClick={loadDashboardData}
                title="Refresh data"
              >
                <i className="fas fa-sync-alt"></i>
              </button>
            )}
          </div>
        </div>
      </div>
      {/* Summary Cards */}
      <div className="row mb-4">
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="card stat-card h-100" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <div className="card-body text-center text-white">
              <h3>{dashboardData.totalStudents}</h3>
              <p>Total Students</p>
              <i className="fas fa-users fa-2x opacity-50"></i>
            </div>
          </div>
        </div>
        
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="card stat-card h-100" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <div className="card-body text-center text-white">
              <h3>{dashboardData.highRiskStudents}</h3>
              <p>High Risk</p>
              <i className="fas fa-exclamation-triangle fa-2x opacity-50"></i>
            </div>
          </div>
        </div>
        
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="card stat-card h-100" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <div className="card-body text-center text-white">
              <h3>{dashboardData.mediumRiskStudents}</h3>
              <p>Medium Risk</p>
              <i className="fas fa-exclamation-circle fa-2x opacity-50"></i>
            </div>
          </div>
        </div>
        
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="card stat-card h-100" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
            <div className="card-body text-center text-white">
              <h3>{dashboardData.lowRiskStudents}</h3>
              <p>Low Risk</p>
              <i className="fas fa-check-circle fa-2x opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="row mb-4">
        {/* Risk Distribution */}
        <div className="col-lg-4 mb-3">
          <div className="chart-container">
            <h4>Risk Distribution</h4>
            <div style={{ height: '300px' }}>
              <Doughnut data={riskDistributionData} options={chartOptions} />
            </div>
          </div>
        </div>
        
        {/* Risk Trend */}
        <div className="col-lg-8 mb-3">
          <div className="chart-container">
            <h4>Risk Trend Analysis</h4>
            <div style={{ height: '300px' }}>
              <Line data={trendData} options={chartOptions} />
            </div>
          </div>
        </div>
      </div>

      {/* Alert Summary and Recent Activities */}
      <div className="row">
        {/* Alert Types */}
        <div className="col-lg-6 mb-3">
          <div className="chart-container">
            <h4>Alert Categories</h4>
            <div style={{ height: '300px' }}>
              <Bar data={alertTypesData} options={chartOptions} />
            </div>
          </div>
        </div>
        
        {/* Recent Alerts */}
        <div className="col-lg-6 mb-3">
          <div className="card h-100">
            <div className="card-header">
              <h5 className="mb-0">Recent Alerts</h5>
            </div>
            <div className="card-body">
              <div className="list-group list-group-flush">
                <div className="list-group-item d-flex justify-content-between align-items-start border-0 px-0">
                  <div className="me-auto">
                    <div className="fw-bold">High Risk Alert</div>
                    <small className="text-muted">Student ID: ST001234 - Attendance below 60%</small>
                  </div>
                  <span className="badge bg-danger rounded-pill">High</span>
                </div>
                
                <div className="list-group-item d-flex justify-content-between align-items-start border-0 px-0">
                  <div className="me-auto">
                    <div className="fw-bold">Academic Performance</div>
                    <small className="text-muted">Student ID: ST001567 - CGPA dropped to 5.8</small>
                  </div>
                  <span className="badge bg-warning rounded-pill">Medium</span>
                </div>
                
                <div className="list-group-item d-flex justify-content-between align-items-start border-0 px-0">
                  <div className="me-auto">
                    <div className="fw-bold">Fee Payment Overdue</div>
                    <small className="text-muted">Student ID: ST001890 - 45 days overdue</small>
                  </div>
                  <span className="badge bg-warning rounded-pill">Medium</span>
                </div>
                
                <div className="list-group-item d-flex justify-content-between align-items-start border-0 px-0">
                  <div className="me-auto">
                    <div className="fw-bold">Multiple Backlogs</div>
                    <small className="text-muted">Student ID: ST002134 - 3 active backlogs</small>
                  </div>
                  <span className="badge bg-danger rounded-pill">High</span>
                </div>
                
                <div className="list-group-item d-flex justify-content-between align-items-start border-0 px-0">
                  <div className="me-auto">
                    <div className="fw-bold">Counseling Required</div>
                    <small className="text-muted">Student ID: ST001455 - Emotional support needed</small>
                  </div>
                  <span className="badge bg-info rounded-pill">Info</span>
                </div>
              </div>
            </div>
            <div className="card-footer bg-transparent">
              <a href="/notifications" className="btn btn-outline-primary btn-sm w-100">
                View All Alerts
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Quick Actions</h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-3 col-sm-6 mb-3">
                  <button className="btn btn-outline-primary w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i className="fas fa-plus fa-2x mb-2"></i>
                    <span>Add Student</span>
                  </button>
                </div>
                <div className="col-md-3 col-sm-6 mb-3">
                  <button className="btn btn-outline-success w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i className="fas fa-calendar-check fa-2x mb-2"></i>
                    <span>Mark Attendance</span>
                  </button>
                </div>
                <div className="col-md-3 col-sm-6 mb-3">
                  <button className="btn btn-outline-warning w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i className="fas fa-bell fa-2x mb-2"></i>
                    <span>Send Alert</span>
                  </button>
                </div>
                <div className="col-md-3 col-sm-6 mb-3">
                  <button className="btn btn-outline-info w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i className="fas fa-file-export fa-2x mb-2"></i>
                    <span>Generate Report</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;