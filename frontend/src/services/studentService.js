import APIService from './apiService';

class StudentService {
  // Dashboard statistics
  async getDashboardStats() {
    return APIService.get('/api/students/dashboard-stats/');
  }

  // Analytics data
  async getAnalytics() {
    return APIService.get('/api/students/analytics/');
  }

  // Students CRUD operations
  async getStudents(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/students/students/?${queryString}` : '/api/students/students/';
    return APIService.get(endpoint);
  }

  async getStudent(id) {
    return APIService.get(`/api/students/students/${id}/`);
  }

  async createStudent(studentData) {
    return APIService.post('/api/students/students/', studentData);
  }

  async updateStudent(id, studentData) {
    return APIService.put(`/api/students/students/${id}/`, studentData);
  }

  async deleteStudent(id) {
    return APIService.delete(`/api/students/students/${id}/`);
  }

  // Departments
  async getDepartments() {
    return APIService.get('/api/students/departments/');
  }

  async createDepartment(departmentData) {
    return APIService.post('/api/students/departments/', departmentData);
  }

  // Batches
  async getBatches(departmentId = null) {
    const endpoint = departmentId 
      ? `/api/students/batches/?department=${departmentId}` 
      : '/api/students/batches/';
    return APIService.get(endpoint);
  }

  async createBatch(batchData) {
    return APIService.post('/api/students/batches/', batchData);
  }

  // Student Backlogs
  async getBacklogs(studentId = null) {
    const endpoint = studentId 
      ? `/api/students/backlogs/?student=${studentId}` 
      : '/api/students/backlogs/';
    return APIService.get(endpoint);
  }

  async createBacklog(backlogData) {
    return APIService.post('/api/students/backlogs/', backlogData);
  }

  // Student Mentors
  async getMentorships(studentId = null) {
    const endpoint = studentId 
      ? `/api/students/mentors/?student=${studentId}` 
      : '/api/students/mentors/';
    return APIService.get(endpoint);
  }

  async createMentorship(mentorshipData) {
    return APIService.post('/api/students/mentors/', mentorshipData);
  }

  // Student Notes
  async getNotes(studentId = null) {
    const endpoint = studentId 
      ? `/api/students/notes/?student=${studentId}` 
      : '/api/students/notes/';
    return APIService.get(endpoint);
  }

  async createNote(noteData) {
    return APIService.post('/api/students/notes/', noteData);
  }

  // Search students
  async searchStudents(query) {
    return APIService.get(`/api/students/students/?search=${encodeURIComponent(query)}`);
  }

  // Get high-risk students
  async getHighRiskStudents() {
    return APIService.get('/api/students/students/?risk_level=HIGH&ordering=-risk_score');
  }

  // Get students by department
  async getStudentsByDepartment(departmentId) {
    return APIService.get(`/api/students/students/?department=${departmentId}`);
  }

  // Get students by risk level
  async getStudentsByRiskLevel(riskLevel) {
    return APIService.get(`/api/students/students/?risk_level=${riskLevel}`);
  }
}

const studentService = new StudentService();
export default studentService;