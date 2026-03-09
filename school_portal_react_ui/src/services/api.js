import axios from 'axios';

// Base URL for Odoo API - empty to use Vite proxy
const BASE_URL = '';

// Create axios instance
const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Session expired - redirect to login
      const currentPath = window.location.pathname;
      if (currentPath !== '/login') {
        window.location.href = '/login?expired=true';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (db, login, password) => {
    const response = await api.post('/api/v2/auth/login', {
      db,
      login,
      password,
    });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/api/v2/auth/logout');
    return response.data;
  },

  checkSession: async () => {
    const response = await api.get('/api/v2/auth/check');
    return response.data;
  },
};

// Student API
export const studentAPI = {
  getProfile: async (studentCode) => {
    const response = await api.post('/api/v2/student/profile', {
      student_code: studentCode,
    });
    return response.data;
  },

  listStudents: async (filters = {}) => {
    const response = await api.post('/api/v2/student/list', filters);
    return response.data;
  },
};

// Fee API
export const feeAPI = {
  getStudentFees: async (studentCode) => {
    const response = await api.post('/api/v2/fees/student', {
      student_code: studentCode,
    });
    return response.data;
  },

  recordPayment: async (feeId, amount, paymentReference, paymentDate, journalId = null) => {
    const payload = {
      fee_id: feeId,
      amount,
      payment_reference: paymentReference,
      payment_date: paymentDate,
    };
    if (journalId) {
      payload.journal_id = journalId;
    }
    const response = await api.post('/api/v2/fees/payment/record', payload);
    return response.data;
  },
};

// Attendance API
export const attendanceAPI = {
  getStudentAttendance: async (studentCode, dateFrom = null, dateTo = null) => {
    const payload = { student_code: studentCode };
    if (dateFrom) payload.date_from = dateFrom;
    if (dateTo) payload.date_to = dateTo;
    
    const response = await api.post('/api/v2/attendance/student', payload);
    return response.data;
  },
};

// Grades API
export const gradesAPI = {
  getStudentGrades: async (studentCode, academicYearId = null, term = null) => {
    const payload = { student_code: studentCode };
    if (academicYearId) payload.academic_year_id = academicYearId;
    if (term) payload.term = term;
    
    const response = await api.post('/api/v2/grades/student', payload);
    return response.data;
  },
};

export default api;
