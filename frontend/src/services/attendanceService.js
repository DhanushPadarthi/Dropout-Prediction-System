import APIService from './apiService';

class AttendanceService {
  // Get attendance statistics
  async getAttendanceStats() {
    return APIService.get('/api/attendance/stats/');
  }

  // Get attendance analytics
  async getAttendanceAnalytics() {
    return APIService.get('/api/attendance/analytics/');
  }

  // Get attendance by student
  async getStudentAttendance(studentId) {
    return APIService.get(`/api/attendance/student/${studentId}/`);
  }

  // Get attendance by date range
  async getAttendanceByDateRange(startDate, endDate) {
    return APIService.get(`/api/attendance/?start_date=${startDate}&end_date=${endDate}`);
  }

  // Get low attendance students
  async getLowAttendanceStudents(threshold = 75) {
    return APIService.get(`/api/attendance/low-attendance/?threshold=${threshold}`);
  }
}

const attendanceService = new AttendanceService();
export default attendanceService;