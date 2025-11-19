import React from 'react';
import { useParams } from 'react-router-dom';

const StudentDetail = () => {
  const { studentId } = useParams();
  
  return (
    <div className="student-detail-page">
      <h2 className="mb-4">Student Details - {studentId}</h2>
      
      <div className="card">
        <div className="card-body">
          <p className="text-muted">Individual student detail functionality will be implemented here.</p>
          <p>Features to include:</p>
          <ul>
            <li>Complete student profile</li>
            <li>Risk assessment details</li>
            <li>Attendance history</li>
            <li>Academic performance</li>
            <li>Counseling history</li>
            <li>Action plans and interventions</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default StudentDetail;