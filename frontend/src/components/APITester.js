import React, { useState, useEffect } from 'react';
import { APIService, StudentService, AttendanceService } from '../services';

const APITester = () => {
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(false);

  const runAPITests = async () => {
    setLoading(true);
    const results = {};

    try {
      // Test API Health
      try {
        const healthData = await APIService.healthCheck();
        results.health = { success: true, data: healthData };
      } catch (error) {
        results.health = { success: false, error: error.message };
      }

      // Test API Root
      try {
        const apiInfo = await APIService.getAPIInfo();
        results.apiInfo = { success: true, data: apiInfo };
      } catch (error) {
        results.apiInfo = { success: false, error: error.message };
      }

      // Test Student Dashboard Stats
      try {
        const dashboardStats = await StudentService.getDashboardStats();
        results.dashboardStats = { success: true, data: dashboardStats };
      } catch (error) {
        results.dashboardStats = { success: false, error: error.message };
      }

      // Test Student Analytics
      try {
        const analytics = await StudentService.getAnalytics();
        results.analytics = { success: true, data: analytics };
      } catch (error) {
        results.analytics = { success: false, error: error.message };
      }

      // Test Students List
      try {
        const students = await StudentService.getStudents();
        results.students = { success: true, data: students };
      } catch (error) {
        results.students = { success: false, error: error.message };
      }

      // Test Departments
      try {
        const departments = await StudentService.getDepartments();
        results.departments = { success: true, data: departments };
      } catch (error) {
        results.departments = { success: false, error: error.message };
      }

      // Test Attendance Stats
      try {
        const attendanceStats = await AttendanceService.getAttendanceStats();
        results.attendanceStats = { success: true, data: attendanceStats };
      } catch (error) {
        results.attendanceStats = { success: false, error: error.message };
      }

      setTestResults(results);
    } catch (error) {
      console.error('Test execution failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAPITests();
  }, []);

  const renderTestResult = (testName, result) => {
    if (!result) return null;

    return (
      <div key={testName} className="card mb-3">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h6 className="mb-0">{testName}</h6>
          <span className={`badge ${result.success ? 'bg-success' : 'bg-danger'}`}>
            {result.success ? 'PASS' : 'FAIL'}
          </span>
        </div>
        <div className="card-body">
          {result.success ? (
            <div>
              <div className="text-success mb-2">
                <i className="fas fa-check-circle me-2"></i>
                API endpoint working correctly
              </div>
              <details>
                <summary className="text-muted" style={{ cursor: 'pointer' }}>
                  View Response Data
                </summary>
                <pre className="mt-2 p-2 bg-light rounded" style={{ fontSize: '0.8rem', maxHeight: '200px', overflow: 'auto' }}>
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              </details>
            </div>
          ) : (
            <div className="text-danger">
              <i className="fas fa-times-circle me-2"></i>
              Error: {result.error}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="api-tester">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>API Connection Tester</h4>
        <button 
          className="btn btn-primary"
          onClick={runAPITests}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status"></span>
              Testing...
            </>
          ) : (
            <>
              <i className="fas fa-sync-alt me-2"></i>
              Run Tests
            </>
          )}
        </button>
      </div>

      <div className="alert alert-info">
        <i className="fas fa-info-circle me-2"></i>
        This page tests all API endpoints to ensure proper connection between frontend and backend.
        Make sure your Django server is running on <strong>http://127.0.0.1:8000</strong>
      </div>

      {loading && (
        <div className="text-center my-4">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Running tests...</span>
          </div>
          <p className="mt-2 text-muted">Testing API endpoints...</p>
        </div>
      )}

      <div className="test-results">
        {Object.entries(testResults).map(([testName, result]) => 
          renderTestResult(testName, result)
        )}
      </div>

      {Object.keys(testResults).length > 0 && (
        <div className="summary-card mt-4">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Test Summary</h6>
            </div>
            <div className="card-body">
              <div className="row text-center">
                <div className="col-md-4">
                  <div className="text-success">
                    <i className="fas fa-check-circle fa-2x mb-2"></i>
                    <h5>{Object.values(testResults).filter(r => r?.success).length}</h5>
                    <small>Passed</small>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="text-danger">
                    <i className="fas fa-times-circle fa-2x mb-2"></i>
                    <h5>{Object.values(testResults).filter(r => !r?.success).length}</h5>
                    <small>Failed</small>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="text-info">
                    <i className="fas fa-list fa-2x mb-2"></i>
                    <h5>{Object.keys(testResults).length}</h5>
                    <small>Total</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APITester;