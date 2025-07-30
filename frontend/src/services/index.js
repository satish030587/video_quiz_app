import api from './api';

export const authService = {
  // Login user
  login: async (credentials) => {
    const response = await api.post('auth/token/', credentials);
    const { access, refresh } = response.data;
    
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return response.data;
  },

  // Logout user
  logout: async () => {
    try {
      await api.post('auth/users/logout/');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  // Get current user info
  getCurrentUser: async () => {
    const response = await api.get('auth/users/me/');
    return response.data;
  },

  // Update user profile
  updateProfile: async (userData) => {
    const response = await api.put('auth/users/me/', userData);
    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Get user's progress (force fresh data)
  getUserProgress: async () => {
    // Add cache-busting parameter to force fresh data
    const timestamp = new Date().getTime();
    const response = await api.get(`auth/progress/my_progress/?t=${timestamp}`);
    return response.data;
  },
};

export const videoService = {
  // Get all videos
  getAllVideos: async () => {
    const timestamp = new Date().getTime();
    const response = await api.get(`videos/videos/?t=${timestamp}`);
    return response.data;
  },

  // Get unlocked videos for current user
  getUnlockedVideos: async () => {
    const timestamp = new Date().getTime();
    const response = await api.get(`videos/videos/unlocked/?t=${timestamp}`);
    return response.data;
  },

  // Check if user can attempt a video quiz
  canAttemptVideo: async (videoId) => {
    const timestamp = new Date().getTime();
    const response = await api.get(`videos/videos/${videoId}/can_attempt/?t=${timestamp}`);
    return response.data;
  },

  // Get video details
  getVideoDetails: async (videoId) => {
    // Add cache-busting parameter to force fresh data
    const timestamp = new Date().getTime();
    const response = await api.get(`videos/videos/${videoId}/?t=${timestamp}`);
    
    return response.data;
  },
  
  // Stream video (uses the improved streaming endpoint)
  streamVideo: (videoId) => {
    const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
    return `${baseUrl}/api/videos/videos/${videoId}/stream_video/`;
  },
};

export const quizService = {
  // Get questions for a video
  getVideoQuestions: async (videoId) => {
    const response = await api.get(`quizzes/questions/by_video/?video_id=${videoId}`);
    return response.data;
  },

  // Start a new quiz attempt
  startQuizAttempt: async (videoId) => {
    try {
      
      const response = await api.post('quizzes/attempts/start/', { video_id: videoId });
      
      return response.data;
    } catch (error) {
      
      
      
      throw error;
    }
  },

  // Submit an answer
  submitAnswer: async (attemptId, questionId, answerId) => {
    const response = await api.post(`quizzes/attempts/${attemptId}/submit_answer/`, {
      question_id: questionId,
      answer_id: answerId,
    });
    return response.data;
  },

  // Get user answers for an attempt
  getUserAnswers: async (attemptId) => {
    const timestamp = new Date().getTime();
    const response = await api.get(`quizzes/attempts/${attemptId}/user_answers/?t=${timestamp}`);
    return response.data;
  },

  // Finish quiz attempt
  finishQuizAttempt: async (attemptId) => {
    const response = await api.post(`quizzes/attempts/${attemptId}/finish/`);
    return response.data;
  },

  // Update timer
  updateTimer: async (attemptId, timeRemaining) => {
    const response = await api.put(`quizzes/attempts/${attemptId}/update_timer/`, {
      time_remaining: timeRemaining,
    });
    return response.data;
  },

  // Get quiz result
  getQuizResult: async (attemptId) => {
    // Add cache-busting parameter to force fresh data
    const timestamp = new Date().getTime();
    const response = await api.get(`quizzes/attempts/${attemptId}/result/?t=${timestamp}`);
    
    // Process the data to ensure percentage is a number
    const data = response.data;
    if (data && data.percentage !== undefined) {
      // Convert percentage to a number if it's a string
      if (typeof data.percentage === 'string') {
        data.percentage = parseFloat(data.percentage);
      }
      
      // Ensure it's not NaN
      if (isNaN(data.percentage)) {
        data.percentage = 0;
      }
    }
    
    return data;
  },

  // Get user's quiz attempts
  getUserAttempts: async () => {
    const timestamp = new Date().getTime();
    const response = await api.get(`quizzes/attempts/?t=${timestamp}`);
    return response.data;
  },
};

export const certificateService = {
  // Get user's certificates
  getUserCertificates: async () => {
    const response = await api.get('auth/certificates/my_certificates/');
    return response.data;
  },

  // Generate a new certificate
  generateCertificate: async () => {
    const response = await api.post('auth/certificates/generate/');
    return response.data;
  },

  // Download certificate
  downloadCertificate: async (certificateId) => {
    const response = await api.get(`auth/certificates/${certificateId}/download/`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
