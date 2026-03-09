import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    checkSession();
  }, []);

  useEffect(() => {
    // Set selected student when user changes
    if (user?.student_code) {
      setSelectedStudent(user.student_code);
    }
  }, [user]);

  const checkSession = async () => {
    try {
      const response = await authAPI.checkSession();
      if (response.status === 'authenticated') {
        setUser(response);
      }
    } catch (err) {
      console.log('No active session');
    } finally {
      setLoading(false);
    }
  };

  const login = async (db, username, password) => {
    try {
      setError(null);
      const response = await authAPI.login(db, username, password);
      
      if (response.status === 'success') {
        setUser(response);
        return { success: true };
      } else {
        throw new Error('Login failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      setSelectedStudent(null);
    }
  };

  const switchStudent = (studentCode) => {
    setSelectedStudent(studentCode);
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
    selectedStudent,
    switchStudent,
    students: user?.students || [],
    isParent: user?.is_parent || false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
