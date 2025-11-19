import React, { useState, useEffect } from 'react';
import APIService from '../services/apiService';

const Students = () => {
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [departments, setDepartments] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStudents();
    fetchDepartments();
  }, []);

  useEffect(() => {
    filterStudents();
  }, [students, searchTerm, riskFilter, departmentFilter]);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await APIService.get('/api/students/students/');
      if (response.success) {
        setStudents(response.students);
      } else {
        setError('Failed to fetch students');
      }
    } catch (error) {
      console.error('Error fetching students:', error);
      setError('Error fetching students');
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await APIService.get('/api/students/departments/');
      if (response.success) {
        setDepartments(response.departments);
      }
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
  };

  const filterStudents = () => {
    let filtered = [...students];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(student => 
        student.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by risk level
    if (riskFilter !== 'all') {
      filtered = filtered.filter(student => {
        const riskScore = student.dropout_risk_score || 0;
        if (riskFilter === 'high') return riskScore >= 0.7;
        if (riskFilter === 'medium') return riskScore >= 0.3 && riskScore < 0.7;
        if (riskFilter === 'low') return riskScore < 0.3;
        return true;
      });
    }

    // Filter by department
    if (departmentFilter !== 'all') {
      filtered = filtered.filter(student => 
        student.department_name === departmentFilter
      );
    }

    setFilteredStudents(filtered);
  };

  const getRiskBadge = (riskScore) => {
    if (riskScore >= 0.7) {
      return <span className="badge bg-danger">High Risk</span>;
    } else if (riskScore >= 0.3) {
      return <span className="badge bg-warning">Medium Risk</span>;
    } else {
      return <span className="badge bg-success">Low Risk</span>;
    }
  };

  const predictStudentRisk = async (studentId) => {
    try {
      const response = await APIService.post('/api/students/ml/predict/', {
        student_id: studentId
      });
      if (response.success) {
        // Update the student's risk in the local state
        setStudents(prev => 
          prev.map(student => 
            student.student_id === studentId 
              ? { ...student, ml_prediction: response.prediction }
              : student
          )
        );
      }
    } catch (error) {
      console.error('Error predicting risk:', error);
    }
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
        <button className="btn btn-outline-danger" onClick={fetchStudents}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="students-page">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Student Management</h2>
        <div>
          <button className="btn btn-outline-primary me-2">
            <i className="fas fa-download me-2"></i>
            Export
          </button>
          <button className="btn btn-primary">
            <i className="fas fa-plus me-2"></i>
            Add Student
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row">
            <div className="col-md-4">
              <label className="form-label">Search Students</label>
              <input
                type="text"
                className="form-control"
                placeholder="Search by ID, name, or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <label className="form-label">Risk Level</label>
              <select
                className="form-select"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
              >
                <option value="all">All Risk Levels</option>
                <option value="high">High Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="low">Low Risk</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Department</label>
              <select
                className="form-select"
                value={departmentFilter}
                onChange={(e) => setDepartmentFilter(e.target.value)}
              >
                <option value="all">All Departments</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.name}>{dept.name}</option>
                ))}
              </select>
            </div>
            <div className="col-md-2 d-flex align-items-end">
              <button 
                className="btn btn-outline-secondary w-100"
                onClick={() => {
                  setSearchTerm('');
                  setRiskFilter('all');
                  setDepartmentFilter('all');
                }}
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Students Table */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Students ({filteredStudents.length})</h5>
        </div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="table table-hover mb-0">
              <thead className="table-light">
                <tr>
                  <th>Student ID</th>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Semester</th>
                  <th>CGPA</th>
                  <th>Attendance</th>
                  <th>Risk Level</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map(student => (
                  <tr key={student.student_id}>
                    <td>
                      <span className="fw-medium">{student.student_id}</span>
                    </td>
                    <td>
                      <div>
                        <div className="fw-medium">{student.full_name}</div>
                        <small className="text-muted">{student.email}</small>
                      </div>
                    </td>
                    <td>{student.department_name}</td>
                    <td>{student.current_semester}</td>
                    <td>
                      <span className={`badge ${student.cgpa >= 8 ? 'bg-success' : student.cgpa >= 6 ? 'bg-warning' : 'bg-danger'}`}>
                        {student.cgpa?.toFixed(2) || 'N/A'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${student.attendance_percentage >= 75 ? 'bg-success' : student.attendance_percentage >= 65 ? 'bg-warning' : 'bg-danger'}`}>
                        {student.attendance_percentage?.toFixed(1) || 'N/A'}%
                      </span>
                    </td>
                    <td>
                      {getRiskBadge(student.dropout_risk_score)}
                      {student.ml_prediction && (
                        <div className="small text-muted mt-1">
                          ML: {student.ml_prediction.risk_level} ({(student.ml_prediction.confidence * 100).toFixed(1)}%)
                        </div>
                      )}
                    </td>
                    <td>
                      <div className="btn-group btn-group-sm">
                        <button
                          className="btn btn-outline-primary"
                          onClick={() => predictStudentRisk(student.student_id)}
                          title="Predict Risk"
                        >
                          <i className="fas fa-brain"></i>
                        </button>
                        <button className="btn btn-outline-info" title="View Details">
                          <i className="fas fa-eye"></i>
                        </button>
                        <button className="btn btn-outline-secondary" title="Edit">
                          <i className="fas fa-edit"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {filteredStudents.length === 0 && !loading && (
        <div className="text-center py-5">
          <div className="text-muted">
            <i className="fas fa-users fa-3x mb-3"></i>
            <p>No students found matching your criteria.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Students;