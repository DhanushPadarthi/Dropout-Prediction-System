import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = ({ collapsed, isMobile, onClose }) => {

  const menuItems = [
    {
      path: '/dashboard',
      icon: 'fas fa-tachometer-alt',
      label: 'Dashboard',
      exact: true
    },
    {
      path: '/students',
      icon: 'fas fa-users',
      label: 'Students'
    },
    {
      path: '/analytics',
      icon: 'fas fa-chart-line',
      label: 'Analytics'
    },
    {
      path: '/ml-dashboard',
      icon: 'fas fa-brain',
      label: 'ML Dashboard',
      badge: 'AI'
    },
    {
      path: '/risk-prediction',
      icon: 'fas fa-search',
      label: 'Risk Prediction',
      badge: 'ML'
    },
    {
      path: '/notifications',
      icon: 'fas fa-bell',
      label: 'Notifications'
    },
    {
      path: '/api-test',
      icon: 'fas fa-plug',
      label: 'API Test',
      badge: 'DEV'
    },
    {
      path: '/settings',
      icon: 'fas fa-cog',
      label: 'Settings'
    }
  ];

  const handleItemClick = () => {
    if (isMobile) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isMobile && !collapsed && (
        <div 
          className="sidebar-overlay show" 
          onClick={onClose}
        ></div>
      )}
      
      <div 
        className={`sidebar ${collapsed ? 'collapsed' : ''} ${isMobile && !collapsed ? 'show' : ''}`}
      >
        {/* Logo/Brand */}
        <div className="sidebar-header p-3 border-bottom border-secondary">
          <h4 className="text-white mb-0">
            <i className="fas fa-graduation-cap me-2"></i>
            {!collapsed && <span>EduPredict</span>}
          </h4>
        </div>

        {/* Navigation Menu */}
        <nav className="sidebar-nav flex-grow-1">
          <ul className="nav nav-pills flex-column p-3">
            {menuItems.map((item) => (
              <li key={item.path} className="nav-item mb-2">
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `nav-link d-flex align-items-center text-decoration-none ${
                      isActive ? 'active bg-primary' : 'text-light'
                    }`
                  }
                  onClick={handleItemClick}
                >
                  <i className={`${item.icon} me-3`}></i>
                  {!collapsed && (
                    <span className="d-flex align-items-center justify-content-between w-100">
                      {item.label}
                      {item.badge && (
                        <span className="badge bg-warning text-dark ms-2" style={{ fontSize: '0.7rem' }}>
                          {item.badge}
                        </span>
                      )}
                    </span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* User Profile Section */}
        <div className="sidebar-footer p-3 border-top border-secondary">
          <div className="d-flex align-items-center text-light">
            <div className="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" 
                 style={{ width: '40px', height: '40px' }}>
              <i className="fas fa-user"></i>
            </div>
            {!collapsed && (
              <div className="flex-grow-1">
                <div className="small fw-bold">Admin User</div>
                <div className="text-muted small">Administrator</div>
              </div>
            )}
          </div>
          
          {!collapsed && (
            <div className="mt-2">
              <button className="btn btn-outline-light btn-sm w-100">
                <i className="fas fa-sign-out-alt me-2"></i>
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;