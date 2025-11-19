import React, { useState, useEffect } from 'react';
import APIService from '../services/apiService';

const Settings = () => {
  const [settings, setSettings] = useState({
    // Risk Thresholds
    highRiskThreshold: 0.7,
    mediumRiskThreshold: 0.3,
    
    // ML Model Settings
    selectedModel: 'random_forest',
    autoRetrain: true,
    retrainFrequency: 'weekly',
    minTrainingData: 100,
    
    // Notification Settings
    emailNotifications: true,
    smsNotifications: false,
    whatsappNotifications: false,
    notificationFrequency: 'immediate',
    
    // System Settings
    dataRetentionDays: 365,
    backupFrequency: 'daily',
    systemMaintenance: 'auto',
    
    // Dashboard Settings
    defaultView: 'overview',
    chartsEnabled: true,
    realTimeUpdates: true,
    maxStudentsPerPage: 50
  });
  
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [activeTab, setActiveTab] = useState('ml');

  useEffect(() => {
    fetchModelInfo();
    loadSettings();
  }, []);

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

  const loadSettings = () => {
    // Load settings from localStorage or API
    const savedSettings = localStorage.getItem('systemSettings');
    if (savedSettings) {
      setSettings(prevSettings => ({
        ...prevSettings,
        ...JSON.parse(savedSettings)
      }));
    }
  };

  const saveSettings = async () => {
    setLoading(true);
    try {
      // Save to localStorage (in real app, would save to backend)
      localStorage.setItem('systemSettings', JSON.stringify(settings));
      setSaveMessage('Settings saved successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage('Error saving settings');
    } finally {
      setLoading(false);
    }
  };

  const retrainModels = async () => {
    setLoading(true);
    try {
      const response = await APIService.post('/api/students/ml/train/', {});
      if (response.success) {
        setSaveMessage('Models retrained successfully!');
        fetchModelInfo(); // Refresh model info
      } else {
        setSaveMessage('Error retraining models');
      }
    } catch (error) {
      console.error('Error retraining models:', error);
      setSaveMessage('Error retraining models');
    } finally {
      setLoading(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  const handleSettingChange = (category, field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const resetToDefaults = () => {
    if (window.confirm('Are you sure you want to reset all settings to default values?')) {
      setSettings({
        highRiskThreshold: 0.7,
        mediumRiskThreshold: 0.3,
        selectedModel: 'random_forest',
        autoRetrain: true,
        retrainFrequency: 'weekly',
        minTrainingData: 100,
        emailNotifications: true,
        smsNotifications: false,
        whatsappNotifications: false,
        notificationFrequency: 'immediate',
        dataRetentionDays: 365,
        backupFrequency: 'daily',
        systemMaintenance: 'auto',
        defaultView: 'overview',
        chartsEnabled: true,
        realTimeUpdates: true,
        maxStudentsPerPage: 50
      });
    }
  };

  return (
    <div className="settings-page">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>System Settings</h2>
        <div>
          {saveMessage && (
            <span className={`me-3 ${saveMessage.includes('Error') ? 'text-danger' : 'text-success'}`}>
              {saveMessage}
            </span>
          )}
          <button 
            className="btn btn-outline-secondary me-2" 
            onClick={resetToDefaults}
          >
            Reset to Defaults
          </button>
          <button 
            className="btn btn-primary" 
            onClick={saveSettings}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2"></span>
                Saving...
              </>
            ) : (
              <>
                <i className="fas fa-save me-2"></i>
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'ml' ? 'active' : ''}`}
            onClick={() => setActiveTab('ml')}
          >
            <i className="fas fa-brain me-2"></i>
            ML & Risk Settings
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            <i className="fas fa-bell me-2"></i>
            Notifications
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'system' ? 'active' : ''}`}
            onClick={() => setActiveTab('system')}
          >
            <i className="fas fa-cog me-2"></i>
            System
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <i className="fas fa-tachometer-alt me-2"></i>
            Dashboard
          </button>
        </li>
      </ul>

      {/* ML & Risk Settings Tab */}
      {activeTab === 'ml' && (
        <div className="row">
          <div className="col-md-8">
            <div className="card mb-4">
              <div className="card-header">
                <h5 className="mb-0">Risk Thresholds</h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label">High Risk Threshold</label>
                    <input
                      type="range"
                      className="form-range"
                      min="0.5"
                      max="1"
                      step="0.05"
                      value={settings.highRiskThreshold}
                      onChange={(e) => handleSettingChange('risk', 'highRiskThreshold', parseFloat(e.target.value))}
                    />
                    <div className="d-flex justify-content-between">
                      <small className="text-muted">50%</small>
                      <strong className="text-danger">{(settings.highRiskThreshold * 100).toFixed(0)}%</strong>
                      <small className="text-muted">100%</small>
                    </div>
                  </div>
                  <div className="col-md-6 mb-3">
                    <label className="form-label">Medium Risk Threshold</label>
                    <input
                      type="range"
                      className="form-range"
                      min="0.1"
                      max="0.6"
                      step="0.05"
                      value={settings.mediumRiskThreshold}
                      onChange={(e) => handleSettingChange('risk', 'mediumRiskThreshold', parseFloat(e.target.value))}
                    />
                    <div className="d-flex justify-content-between">
                      <small className="text-muted">10%</small>
                      <strong className="text-warning">{(settings.mediumRiskThreshold * 100).toFixed(0)}%</strong>
                      <small className="text-muted">60%</small>
                    </div>
                  </div>
                </div>
                <div className="alert alert-info">
                  <small>
                    <strong>Note:</strong> Students with risk scores above {(settings.highRiskThreshold * 100).toFixed(0)}% 
                    will be classified as high-risk, between {(settings.mediumRiskThreshold * 100).toFixed(0)}% and {(settings.highRiskThreshold * 100).toFixed(0)}% 
                    as medium-risk, and below {(settings.mediumRiskThreshold * 100).toFixed(0)}% as low-risk.
                  </small>
                </div>
              </div>
            </div>

            <div className="card mb-4">
              <div className="card-header">
                <h5 className="mb-0">ML Model Configuration</h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label">Primary Model</label>
                    <select
                      className="form-select"
                      value={settings.selectedModel}
                      onChange={(e) => handleSettingChange('ml', 'selectedModel', e.target.value)}
                    >
                      <option value="random_forest">Random Forest</option>
                      <option value="gradient_boosting">Gradient Boosting</option>
                      <option value="logistic_regression">Logistic Regression</option>
                      <option value="decision_tree">Decision Tree</option>
                      <option value="support_vector_machine">Support Vector Machine</option>
                      <option value="neural_network">Neural Network</option>
                      <option value="naive_bayes">Naive Bayes</option>
                    </select>
                  </div>
                  <div className="col-md-6 mb-3">
                    <label className="form-label">Retrain Frequency</label>
                    <select
                      className="form-select"
                      value={settings.retrainFrequency}
                      onChange={(e) => handleSettingChange('ml', 'retrainFrequency', e.target.value)}
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="manual">Manual Only</option>
                    </select>
                  </div>
                </div>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label className="form-label">Minimum Training Data</label>
                    <input
                      type="number"
                      className="form-control"
                      min="50"
                      max="1000"
                      value={settings.minTrainingData}
                      onChange={(e) => handleSettingChange('ml', 'minTrainingData', parseInt(e.target.value))}
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <div className="form-check mt-4">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        checked={settings.autoRetrain}
                        onChange={(e) => handleSettingChange('ml', 'autoRetrain', e.target.checked)}
                      />
                      <label className="form-check-label">
                        Enable automatic retraining
                      </label>
                    </div>
                  </div>
                </div>
                <button 
                  className="btn btn-primary"
                  onClick={retrainModels}
                  disabled={loading}
                >
                  <i className="fas fa-sync me-2"></i>
                  Retrain Models Now
                </button>
              </div>
            </div>
          </div>

          <div className="col-md-4">
            {modelInfo && (
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0">Current Model Status</h5>
                </div>
                <div className="card-body">
                  {(() => {
                    const metrics = modelInfo.model_info?.performance_metrics || {};
                    const bestModel = Object.entries(metrics).reduce((best, [name, data]) => 
                      !best || data.f1_score > best.data.f1_score ? { name, data } : best
                    , null);
                    
                    return bestModel ? (
                      <>
                        <div className="mb-3">
                          <label className="text-muted">Best Performing Model</label>
                          <div className="fw-bold text-capitalize">{bestModel.name.replace('_', ' ')}</div>
                        </div>
                        <div className="mb-3">
                          <label className="text-muted">Accuracy</label>
                          <div className="fw-bold text-success">
                            {(bestModel.data.accuracy * 100).toFixed(1)}%
                          </div>
                        </div>
                        <div className="mb-3">
                          <label className="text-muted">F1 Score</label>
                          <div className="fw-bold text-success">
                            {(bestModel.data.f1_score * 100).toFixed(1)}%
                          </div>
                        </div>
                        <div className="mb-3">
                          <label className="text-muted">Last Trained</label>
                          <div className="fw-bold">
                            {new Date(bestModel.data.training_date).toLocaleDateString()}
                          </div>
                        </div>
                      </>
                    ) : null;
                  })()}
                  <div className="mb-3">
                    <label className="text-muted">Available Models</label>
                    <div className="fw-bold">{modelInfo.model_info?.available_models?.length || 0} models</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">Notification Settings</h5>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-6">
                <h6>Notification Channels</h6>
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.emailNotifications}
                    onChange={(e) => handleSettingChange('notifications', 'emailNotifications', e.target.checked)}
                  />
                  <label className="form-check-label">
                    <i className="fas fa-envelope me-2"></i>Email Notifications
                  </label>
                </div>
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.smsNotifications}
                    onChange={(e) => handleSettingChange('notifications', 'smsNotifications', e.target.checked)}
                  />
                  <label className="form-check-label">
                    <i className="fas fa-sms me-2"></i>SMS Notifications
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.whatsappNotifications}
                    onChange={(e) => handleSettingChange('notifications', 'whatsappNotifications', e.target.checked)}
                  />
                  <label className="form-check-label">
                    <i className="fab fa-whatsapp me-2"></i>WhatsApp Notifications
                  </label>
                </div>
              </div>
              <div className="col-md-6">
                <h6>Notification Frequency</h6>
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="notificationFrequency"
                    checked={settings.notificationFrequency === 'immediate'}
                    onChange={() => handleSettingChange('notifications', 'notificationFrequency', 'immediate')}
                  />
                  <label className="form-check-label">Immediate</label>
                </div>
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="notificationFrequency"
                    checked={settings.notificationFrequency === 'hourly'}
                    onChange={() => handleSettingChange('notifications', 'notificationFrequency', 'hourly')}
                  />
                  <label className="form-check-label">Hourly Digest</label>
                </div>
                <div className="form-check mb-3">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="notificationFrequency"
                    checked={settings.notificationFrequency === 'daily'}
                    onChange={() => handleSettingChange('notifications', 'notificationFrequency', 'daily')}
                  />
                  <label className="form-check-label">Daily Summary</label>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Tab */}
      {activeTab === 'system' && (
        <div className="row">
          <div className="col-md-6">
            <div className="card mb-4">
              <div className="card-header">
                <h5 className="mb-0">Data Management</h5>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <label className="form-label">Data Retention (Days)</label>
                  <input
                    type="number"
                    className="form-control"
                    min="30"
                    max="3650"
                    value={settings.dataRetentionDays}
                    onChange={(e) => handleSettingChange('system', 'dataRetentionDays', parseInt(e.target.value))}
                  />
                  <small className="form-text text-muted">How long to keep student data</small>
                </div>
                <div className="mb-3">
                  <label className="form-label">Backup Frequency</label>
                  <select
                    className="form-select"
                    value={settings.backupFrequency}
                    onChange={(e) => handleSettingChange('system', 'backupFrequency', e.target.value)}
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6">
            <div className="card mb-4">
              <div className="card-header">
                <h5 className="mb-0">System Maintenance</h5>
              </div>
              <div className="card-body">
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="systemMaintenance"
                    checked={settings.systemMaintenance === 'auto'}
                    onChange={() => handleSettingChange('system', 'systemMaintenance', 'auto')}
                  />
                  <label className="form-check-label">Automatic maintenance</label>
                </div>
                <div className="form-check mb-3">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="systemMaintenance"
                    checked={settings.systemMaintenance === 'manual'}
                    onChange={() => handleSettingChange('system', 'systemMaintenance', 'manual')}
                  />
                  <label className="form-check-label">Manual maintenance only</label>
                </div>
                <button className="btn btn-outline-primary btn-sm me-2">
                  <i className="fas fa-tools me-1"></i>Run Maintenance
                </button>
                <button className="btn btn-outline-success btn-sm">
                  <i className="fas fa-download me-1"></i>Backup Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">Dashboard Preferences</h5>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Default View</label>
                  <select
                    className="form-select"
                    value={settings.defaultView}
                    onChange={(e) => handleSettingChange('dashboard', 'defaultView', e.target.value)}
                  >
                    <option value="overview">Overview</option>
                    <option value="students">Students</option>
                    <option value="analytics">Analytics</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label className="form-label">Students Per Page</label>
                  <select
                    className="form-select"
                    value={settings.maxStudentsPerPage}
                    onChange={(e) => handleSettingChange('dashboard', 'maxStudentsPerPage', parseInt(e.target.value))}
                  >
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </div>
              </div>
              <div className="col-md-6">
                <h6>Display Options</h6>
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.chartsEnabled}
                    onChange={(e) => handleSettingChange('dashboard', 'chartsEnabled', e.target.checked)}
                  />
                  <label className="form-check-label">Enable charts and graphs</label>
                </div>
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.realTimeUpdates}
                    onChange={(e) => handleSettingChange('dashboard', 'realTimeUpdates', e.target.checked)}
                  />
                  <label className="form-check-label">Real-time updates</label>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;