// Export all services from a central location
import APIService from './apiService';
import StudentService from './studentService';
import AttendanceService from './attendanceService';

export { default as APIService } from './apiService';
export { default as StudentService } from './studentService';
export { default as AttendanceService } from './attendanceService';

// Re-export for convenience
const services = {
  API: APIService,
  Student: StudentService,
  Attendance: AttendanceService,
};

export default services;