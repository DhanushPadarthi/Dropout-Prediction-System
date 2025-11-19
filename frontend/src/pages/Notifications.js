import React, { useState, useEffect } from 'react';
import APIService from '../services/apiService';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [highRiskStudents, setHighRiskStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('alerts');
  const [notificationSettings, setNotificationSettings] = useState({
    emailEnabled: true,
    smsEnabled: false,
    whatsappEnabled: false,
    highRiskThreshold: 0.7,
    mediumRiskThreshold: 0.3,
    autoNotify: true
  });

  useEffect(() => {
    fetchNotifications();
    fetchHighRiskStudents();
  }, []);

  const fetchNotifications = async () => {
    try {
      // Mock notifications for now - will be implemented in backend
      const mockNotifications = [
        {
          id: 1,
          type: 'high_risk_alert',
          title: 'High Risk Student Alert',
          message: 'Student 23ECE015 has been identified as high risk for dropout',
          student_id: '23ECE015',
          student_name: 'Arjun Kumar',
          risk_score: 0.85,
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
          status: 'unread',
          channels: ['email', 'dashboard']
        },
        {
          id: 2,
          type: 'attendance_alert',
          title: 'Low Attendance Warning',
          message: 'Student 23CSE032 attendance dropped below 65%',
          student_id: '23CSE032', 
          student_name: 'Priya Sharma',
          risk_score: 0.45,
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
          status: 'read',
          channels: ['email']
        },
        {
          id: 3,
          type: 'cgpa_alert',
          title: 'Academic Performance Alert',
          message: 'Student 23ME021 CGPA dropped below 6.0',
          student_id: '23ME021',
          student_name: 'Rahul Singh',
          risk_score: 0.72,
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
          status: 'read',
          channels: ['email', 'sms']
        }
      ];
      setNotifications(mockNotifications);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHighRiskStudents = async () => {
    try {
      const response = await APIService.get('/api/students/students/');
      if (response.success) {
        const highRisk = response.students.filter(student => 
          (student.dropout_risk_score || 0) >= notificationSettings.highRiskThreshold
        );
        setHighRiskStudents(highRisk);
      }
    } catch (error) {
      console.error('Error fetching high risk students:', error);
    }
  };

  const sendBulkNotifications = async () => {
    try {
      // Mock function - will be implemented in backend
      alert(`Sending notifications to ${highRiskStudents.length} high-risk students...`);
      // Add mock notifications to the list
      const newNotifications = highRiskStudents.map((student, index) => ({
        id: Date.now() + index,
        type: 'bulk_alert',
        title: 'Counseling Session Invitation',
        message: `Invitation sent to ${student.full_name} for counseling session`,
        student_id: student.student_id,
        student_name: student.full_name,
        risk_score: student.dropout_risk_score,
        timestamp: new Date(),
        status: 'sent',
        channels: ['email']
      }));
      setNotifications(prev => [...newNotifications, ...prev]);
    } catch (error) {
      console.error('Error sending bulk notifications:', error);
    }
  };

  const markAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId 
          ? { ...notif, status: 'read' }
          : notif
      )
    );
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'high_risk_alert':
        return 'fas fa-exclamation-triangle text-danger';
      case 'attendance_alert':
        return 'fas fa-calendar-times text-warning';
      case 'cgpa_alert':
        return 'fas fa-chart-line text-warning';
      case 'bulk_alert':
        return 'fas fa-bullhorn text-info';
      default:
        return 'fas fa-bell text-primary';
    }
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));
    
    if (hours > 24) {
      return `${Math.floor(hours / 24)} days ago`;
    } else if (hours > 0) {
      return `${hours} hours ago`;
    } else if (minutes > 0) {
      return `${minutes} minutes ago`;
    } else {
      return 'Just now';
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

  return (
    <div className="notifications-page">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Notifications & Alerts</h2>
        <div>
          <button 
            className="btn btn-primary me-2"
            onClick={sendBulkNotifications}
            disabled={highRiskStudents.length === 0}
          >
            <i className="fas fa-paper-plane me-2"></i>
            Send Bulk Alerts ({highRiskStudents.length})
          </button>
          <button className="btn btn-outline-secondary">
            <i className="fas fa-cog me-2"></i>
            Settings
          </button>
        </div>
      </div>

      {/* Tabs */}
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button 
            className={`nav-link ${selectedTab === 'alerts' ? 'active' : ''}`}
            onClick={() => setSelectedTab('alerts')}
          >
            <i className="fas fa-bell me-2"></i>
            Recent Alerts
            {notifications.filter(n => n.status === 'unread').length > 0 && (
              <span className="badge bg-danger ms-2">
                {notifications.filter(n => n.status === 'unread').length}
              </span>
            )}
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${selectedTab === 'high-risk' ? 'active' : ''}`}
            onClick={() => setSelectedTab('high-risk')}
          >
            <i className="fas fa-exclamation-triangle me-2"></i>
            High Risk Students ({highRiskStudents.length})
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${selectedTab === 'templates' ? 'active' : ''}`}
            onClick={() => setSelectedTab('templates')}
          >
            <i className="fas fa-file-alt me-2"></i>
            Templates
          </button>
        </li>
      </ul>

      {/* Alerts Tab */}
      {selectedTab === 'alerts' && (
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">Recent Notifications</h5>
          </div>
          <div className="card-body p-0">
            {notifications.length === 0 ? (
              <div className="text-center py-5">
                <i className="fas fa-bell-slash fa-3x text-muted mb-3"></i>
                <p className="text-muted">No notifications yet</p>
              </div>
            ) : (
              <div className="list-group list-group-flush">
                {notifications.map(notification => (
                  <div 
                    key={notification.id} 
                    className={`list-group-item ${notification.status === 'unread' ? 'bg-light border-start border-primary border-3' : ''}`}
                  >
                    <div className="d-flex justify-content-between align-items-start">
                      <div className="d-flex">
                        <div className="me-3 mt-1">
                          <i className={getNotificationIcon(notification.type)}></i>
                        </div>
                        <div className="flex-grow-1">
                          <h6 className="mb-1">{notification.title}</h6>
                          <p className="mb-1">{notification.message}</p>
                          <div className="d-flex align-items-center">
                            <small className="text-muted me-3">
                              <i className="fas fa-user me-1"></i>
                              {notification.student_name} ({notification.student_id})
                            </small>
                            <small className="text-muted me-3">
                              <i className="fas fa-clock me-1"></i>
                              {getTimeAgo(notification.timestamp)}
                            </small>
                            {notification.risk_score && (
                              <span className={`badge ${notification.risk_score >= 0.7 ? 'bg-danger' : notification.risk_score >= 0.3 ? 'bg-warning' : 'bg-success'} me-2`}>
                                Risk: {(notification.risk_score * 100).toFixed(0)}%
                              </span>
                            )}
                            <div className="d-flex">
                              {notification.channels.map(channel => (
                                <span key={channel} className="badge bg-secondary me-1">
                                  {channel}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="dropdown">
                        <button className="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                          Actions
                        </button>
                        <ul className="dropdown-menu">
                          {notification.status === 'unread' && (
                            <li>
                              <button 
                                className="dropdown-item"
                                onClick={() => markAsRead(notification.id)}
                              >
                                <i className="fas fa-check me-2"></i>Mark as Read
                              </button>
                            </li>
                          )}
                          <li>
                            <button className="dropdown-item">
                              <i className="fas fa-eye me-2"></i>View Student
                            </button>
                          </li>
                          <li>
                            <button className="dropdown-item">
                              <i className="fas fa-reply me-2"></i>Send Follow-up
                            </button>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* High Risk Students Tab */}
      {selectedTab === 'high-risk' && (
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">Students Requiring Immediate Attention</h5>
          </div>
          <div className="card-body">
            {highRiskStudents.length === 0 ? (
              <div className="text-center py-5">
                <i className="fas fa-check-circle fa-3x text-success mb-3"></i>
                <p className="text-muted">No high-risk students at the moment</p>
              </div>
            ) : (
              <div className="row">
                {highRiskStudents.map(student => (
                  <div key={student.student_id} className="col-md-6 mb-3">
                    <div className="card border-danger">
                      <div className="card-body">
                        <div className="d-flex justify-content-between align-items-start mb-2">
                          <h6 className="card-title mb-0">{student.full_name}</h6>
                          <span className="badge bg-danger">
                            {(student.dropout_risk_score * 100).toFixed(0)}% Risk
                          </span>
                        </div>
                        <p className="text-muted mb-2">
                          {student.student_id} • {student.department_name} • Sem {student.current_semester}
                        </p>
                        <div className="row text-center">
                          <div className="col-4">
                            <small className="text-muted">CGPA</small>
                            <div className={`fw-bold ${student.cgpa >= 6 ? 'text-warning' : 'text-danger'}`}>
                              {student.cgpa?.toFixed(2) || 'N/A'}
                            </div>
                          </div>
                          <div className="col-4">
                            <small className="text-muted">Attendance</small>
                            <div className={`fw-bold ${student.attendance_percentage >= 65 ? 'text-warning' : 'text-danger'}`}>
                              {student.attendance_percentage?.toFixed(1) || 'N/A'}%
                            </div>
                          </div>
                          <div className="col-4">
                            <small className="text-muted">Contact</small>
                            <div className="d-flex justify-content-center">
                              <button className="btn btn-sm btn-outline-primary me-1" title="Email">
                                <i className="fas fa-envelope"></i>
                              </button>
                              <button className="btn btn-sm btn-outline-success" title="WhatsApp">
                                <i className="fab fa-whatsapp"></i>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {selectedTab === 'templates' && (
        <div className="card">
          <div className="card-header">
            <div className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Notification Templates</h5>
              <button className="btn btn-primary btn-sm">
                <i className="fas fa-plus me-2"></i>Add Template
              </button>
            </div>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-6 mb-3">
                <div className="card border-warning">
                  <div className="card-body">
                    <h6 className="card-title">High Risk Alert</h6>
                    <p className="card-text small text-muted">
                      Dear {'{student_name}'}, our AI system has identified you as at-risk for dropout. 
                      Please schedule a counseling session to discuss support options.
                    </p>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="badge bg-warning">Email Template</span>
                      <div>
                        <button className="btn btn-sm btn-outline-primary me-1">
                          <i className="fas fa-edit"></i>
                        </button>
                        <button className="btn btn-sm btn-outline-danger">
                          <i className="fas fa-trash"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-md-6 mb-3">
                <div className="card border-info">
                  <div className="card-body">
                    <h6 className="card-title">Attendance Warning</h6>
                    <p className="card-text small text-muted">
                      Your attendance has dropped to {'{attendance_percentage}'}%. 
                      Please improve attendance to avoid academic issues.
                    </p>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="badge bg-info">SMS Template</span>
                      <div>
                        <button className="btn btn-sm btn-outline-primary me-1">
                          <i className="fas fa-edit"></i>
                        </button>
                        <button className="btn btn-sm btn-outline-danger">
                          <i className="fas fa-trash"></i>
                        </button>
                      </div>
                    </div>
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

export default Notifications;