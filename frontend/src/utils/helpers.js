// Format time in seconds to MM:SS format
export const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// Format percentage to 1 decimal place
export const formatPercentage = (percentage) => {
  return parseFloat(percentage).toFixed(1);
};

// Generate unique ID for quiz sessions
export const generateUniqueId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// Check if a video is unlocked based on user progress
export const isVideoUnlocked = (videoIndex, unlockedVideos) => {
  if (videoIndex === 0) return true; // First video is always unlocked
  return unlockedVideos.some(video => video.sequence_number === videoIndex);
};

// Get video status based on attempts and results
export const getVideoStatus = (video, attempts = []) => {
  const videoAttempts = attempts.filter(attempt => attempt.video === video.id);
  
  if (videoAttempts.length === 0) {
    return 'not_attempted';
  }

  const passedAttempt = videoAttempts.find(attempt => attempt.is_passed);
  if (passedAttempt) {
    return 'passed';
  }

  const inProgressAttempt = videoAttempts.find(attempt => attempt.status === 'in_progress');
  if (inProgressAttempt) {
    return 'in_progress';
  }

  if (videoAttempts.length >= 2) {
    return 'max_attempts';
  }

  return 'failed';
};

// Calculate overall progress percentage
export const calculateOverallProgress = (totalVideos, passedVideos) => {
  if (totalVideos === 0) return 0;
  return Math.round((passedVideos / totalVideos) * 100);
};

// Validate quiz answer submission
export const validateAnswerSubmission = (questionId, answerId) => {
  return questionId && answerId && !isNaN(questionId) && !isNaN(answerId);
};

// Check if quiz is complete (all questions answered)
export const isQuizComplete = (questions, userAnswers) => {
  return questions.every(question => 
    userAnswers.some(answer => 
      answer.question === question.id && answer.selected_answer
    )
  );
};

// Get answered questions count
export const getAnsweredQuestionsCount = (questions, userAnswers) => {
  return questions.filter(question =>
    userAnswers.some(answer =>
      answer.question === question.id && answer.selected_answer
    )
  ).length;
};

// Local storage helpers
export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      
      return defaultValue;
    }
  },

  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      
    }
  },

  remove: (key) => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      
    }
  },

  clear: () => {
    try {
      localStorage.clear();
    } catch (error) {
      
    }
  }
};

// Debounce function for API calls
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Check if device is mobile
export const isMobile = () => {
  return window.innerWidth <= 768;
};

// Format date to readable string
export const formatDate = (dateString) => {
  const options = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  return new Date(dateString).toLocaleDateString(undefined, options);
};
