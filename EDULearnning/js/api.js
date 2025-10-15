// Base API URL (adjust port if needed)
const API_BASE_URL = 'http://localhost:5000/api';

// Authentication API Calls
export const authAPI = {
  studentSignup: async (data) => {
    return fetch(`${API_BASE_URL}/auth/student/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  },
  
  teacherSignup: async (data) => {
    return fetch(`${API_BASE_URL}/auth/teacher/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  },

  adminSignup: async (data) => {
    return fetch(`${API_BASE_URL}/auth/admin/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  },
  
  login: async (credentials) => {
    return fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
  }
};

// Course API Calls
export const courseAPI = {
  getAllCourses: async () => {
    return fetch(`${API_BASE_URL}/courses`);
  },
  
  getCourseById: async (id) => {
    return fetch(`${API_BASE_URL}/courses/${id}`);
  },
  
  createCourse: async (courseData, token) => {
    return fetch(`${API_BASE_URL}/courses`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(courseData)
    });
  }
};

// User API Calls
export const userAPI = {
  getCurrentUser: async (token) => {
    return fetch(`${API_BASE_URL}/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  getNotifications: async (token) => {
    return fetch(`${API_BASE_URL}/users/notifications`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
};

// Extended Course API Calls
courseAPI.getUserCourses = async (token) => {
  return fetch(`${API_BASE_URL}/courses/user`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};

// Assessment API Calls
export const assessmentAPI = {
  // Get all assessments for a course
  getCourseAssessments: async (courseId) => {
    return fetch(`${API_BASE_URL}/assessments/course/${courseId}`);
  },
  
  // Get assessments for a specific module
  getModuleAssessments: async (courseId, moduleId) => {
    return fetch(`${API_BASE_URL}/assessments/module/${courseId}/${moduleId}`);
  },
  
  // Get specific assessment
  getAssessment: async (assessmentId) => {
    return fetch(`${API_BASE_URL}/assessments/${assessmentId}`);
  },
  
  // Create assessment (instructor only)
  createAssessment: async (assessmentData, token) => {
    return fetch(`${API_BASE_URL}/assessments/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(assessmentData)
    });
  },
  
  // Update assessment (instructor only)
  updateAssessment: async (assessmentId, assessmentData, token) => {
    return fetch(`${API_BASE_URL}/assessments/${assessmentId}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(assessmentData)
    });
  },
  
  // Delete assessment (instructor only)
  deleteAssessment: async (assessmentId, token) => {
    return fetch(`${API_BASE_URL}/assessments/${assessmentId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
};

// Test Results API Calls
export const testResultAPI = {
  // Submit test answers
  submitTest: async (submissionData, token) => {
    return fetch(`${API_BASE_URL}/test-results/submit`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(submissionData)
    });
  },
  
  // Get user's test results for a course
  getUserCourseResults: async (userId, courseId, token) => {
    return fetch(`${API_BASE_URL}/test-results/user/${userId}/course/${courseId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  // Get results for specific assessment
  getAssessmentResults: async (assessmentId, token) => {
    return fetch(`${API_BASE_URL}/test-results/assessment/${assessmentId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  // Get best score for an assessment
  getBestScore: async (assessmentId, token) => {
    return fetch(`${API_BASE_URL}/test-results/best-score/${assessmentId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  // Get course assessment summary
  getCourseSummary: async (courseId, token) => {
    return fetch(`${API_BASE_URL}/test-results/course-summary/${courseId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  // Check certificate eligibility
  checkEligibility: async (courseId, token) => {
    return fetch(`${API_BASE_URL}/test-results/check-eligibility/${courseId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  // Grade assignment (instructor only)
  gradeAssignment: async (resultId, gradeData, token) => {
    return fetch(`${API_BASE_URL}/test-results/grade-assignment/${resultId}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(gradeData)
    });
  }
};

// Certificate API Calls
export const certificateAPI = {
  // Generate certificate
  generateCertificate: async (courseId, token) => {
    return fetch(`${API_BASE_URL}/certificates/generate`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ courseId })
    });
  },
  
  // Get user's certificates
  getUserCertificates: async (userId, token) => {
    return fetch(`${API_BASE_URL}/certificates/user/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  // Get specific certificate
  getCertificate: async (certId) => {
    return fetch(`${API_BASE_URL}/certificates/${certId}`);
  },
  
  // Download certificate PDF
  downloadCertificatePDF: async (certId, token) => {
    return fetch(`${API_BASE_URL}/certificates/${certId}/pdf`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },
  
  // Verify certificate
  verifyCertificate: async (certificateData) => {
    return fetch(`${API_BASE_URL}/certificates/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(certificateData)
    });
  },
  
  // Check certificate eligibility
  checkEligibility: async (courseId, token) => {
    return fetch(`${API_BASE_URL}/certificates/check-eligibility/${courseId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
};

// Helper function to get token from localStorage
export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

// Helper function to get current user ID
export const getCurrentUserId = () => {
  const userId = localStorage.getItem('userId');
  if (userId) return userId;

  // Fallback: try to get from user object
  const user = localStorage.getItem('user');
  if (user) {
    try {
      const userObj = JSON.parse(user);
      return userObj.id || userObj._id;
    } catch (e) {
      return null;
    }
  }
  return null;
};

// Admin API Calls
export const adminAPI = {
  // Get all users with pagination and filtering
  getAllUsers: async (params = {}, token) => {
    const queryParams = new URLSearchParams(params);
    return fetch(`${API_BASE_URL}/admin/users?${queryParams}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Get specific user
  getUser: async (userId, token) => {
    return fetch(`${API_BASE_URL}/admin/users/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Update user
  updateUser: async (userId, userData, token) => {
    return fetch(`${API_BASE_URL}/admin/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });
  },

  // Delete/deactivate user
  deleteUser: async (userId, token) => {
    return fetch(`${API_BASE_URL}/admin/users/${userId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Get admin statistics
  getStats: async (token) => {
    return fetch(`${API_BASE_URL}/admin/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
};

// Message API Calls
export const messageAPI = {
  // Get all conversations for current user
  getConversations: async (token) => {
    return fetch(`${API_BASE_URL}/messages/conversations`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Get messages in a specific conversation
  getConversationMessages: async (conversationId, token) => {
    return fetch(`${API_BASE_URL}/messages/conversation/${conversationId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Send a new message
  sendMessage: async (messageData, token) => {
    return fetch(`${API_BASE_URL}/messages/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(messageData)
    });
  },

  // Create a new conversation
  createConversation: async (recipientId, token) => {
    return fetch(`${API_BASE_URL}/messages/conversation/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ recipientId })
    });
  },

  // Get unread message count
  getUnreadCount: async (token) => {
    return fetch(`${API_BASE_URL}/messages/unread-count`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Search for users to message
  searchUsers: async (query, token) => {
    return fetch(`${API_BASE_URL}/messages/users/search?q=${encodeURIComponent(query)}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
};

// Helper function to handle API errors
export const handleAPIError = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API request failed');
  }
  return response.json();
};
