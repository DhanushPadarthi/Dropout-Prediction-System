import React from 'react';
import { useLocation } from 'react-router-dom';

const Header = ({ onToggleSidebar, sidebarCollapsed }) => {
  const location = useLocation();

  // Get page title based on current route
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/':
      case '/dashboard':
        return 'Dashboard';
      case '/students':
        return 'Student Management';
      case '/analytics':
        return 'Analytics & Reports';
      case '/notifications':
        return 'Notifications';
      case '/settings':
        return 'Settings';
      default:
        if (location.pathname.startsWith('/students/')) {
          return 'Student Details';
        }
        return 'EduPredict System';
    }
  };

  const getPageDescription = () => {
    switch (location.pathname) {
      case '/':
      case '/dashboard':
        return 'Overview of student risk analytics and system performance';
      case '/students':
        return 'Manage student profiles and monitor dropout risks';
      case '/analytics':
        return 'Detailed analytics and performance insights';
      case '/notifications':
        return 'System alerts and communication management';
      case '/settings':
        return 'System configuration and user preferences';
      default:
        if (location.pathname.startsWith('/students/')) {
          return 'Detailed student information and risk assessment';
        }
        return 'AI-Based Dropout Prediction & Counseling System';
    }
  };

  return (
    <header className="app-header d-flex justify-content-between align-items-center">
      <div className="d-flex align-items-center">
        {/* Toggle Button */}
        <button
          className="btn btn-outline-secondary me-3 d-lg-none"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          <i className="fas fa-bars"></i>
        </button>

        {/* Desktop Toggle Button */}
        <button
          className="btn btn-outline-secondary me-3 d-none d-lg-block"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          <i className={`fas ${sidebarCollapsed ? 'fa-indent' : 'fa-outdent'}`}></i>
        </button>

        {/* Page Title */}
        <div>
          <h1 className="h3 mb-0 text-dark">{getPageTitle()}</h1>
          <p className="text-muted mb-0 small d-none d-md-block">
            {getPageDescription()}
          </p>
        </div>
      </div>

      {/* Header Actions */}
      <div className="d-flex align-items-center">
        {/* Search Bar - Hidden on mobile */}
        <div className="me-3 d-none d-lg-block">
          <div className="input-group" style={{ width: '300px' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Search students..."
              aria-label="Search"
            />
            <button className="btn btn-outline-secondary" type="button">
              <i className="fas fa-search"></i>
            </button>
          </div>
        </div>

        {/* Notification Bell */}
        <div className="me-3 position-relative">
          <button className="btn btn-outline-secondary position-relative">
            <i className="fas fa-bell"></i>
            <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style={{ fontSize: '0.6rem' }}>
              3
              <span className="visually-hidden">unread notifications</span>
            </span>
          </button>
        </div>

        {/* User Dropdown */}
        <div className="dropdown">
          <button
            className="btn btn-outline-secondary dropdown-toggle d-flex align-items-center"
            type="button"
            id="userDropdown"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <div className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2"
                 style={{ width: '32px', height: '32px' }}>
              <i className="fas fa-user"></i>
            </div>
            <span className="d-none d-md-inline">Admin</span>
          </button>
          <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
            <li>
              <a className="dropdown-item" href="#profile">
                <i className="fas fa-user me-2"></i>
                Profile
              </a>
            </li>
            <li>
              <a className="dropdown-item" href="#settings">
                <i className="fas fa-cog me-2"></i>
                Settings
              </a>
            </li>
            <li><hr className="dropdown-divider" /></li>
            <li>
              <a className="dropdown-item text-danger" href="#logout">
                <i className="fas fa-sign-out-alt me-2"></i>
                Logout
              </a>
            </li>
          </ul>
        </div>
      </div>
    </header>
  );
};

export default Header;