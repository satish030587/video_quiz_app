// This file contains direct service functions to use in the dashboard
// dashboardService.js

import axios from 'axios';

// Create a function to get the token
const getToken = () => localStorage.getItem('access_token');

// Function to fetch all required dashboard data
export const fetchDashboardData = async () => {
  try {
    // Create the auth header
    const token = getToken();
    if (!token) {
      
      return {
        videos: [],
        unlockedVideos: [],
        progress: {
          videos_passed: [],
          videos_failed: [],
          total_retries: 0,
          overall_progress: 0
        }
      };
    }
    
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    };
    
    // Add timestamp to prevent caching
    const timestamp = Date.now();
    
    
    
    // Make parallel requests
    const [videosRes, unlockedRes, progressRes] = await Promise.all([
      axios.get(`http://localhost:8000/api/videos/videos/?t=${timestamp}`, { headers }),
      axios.get(`http://localhost:8000/api/videos/videos/unlocked/?t=${timestamp}`, { headers }),
      axios.get(`http://localhost:8000/api/auth/progress/my_progress/?t=${timestamp}`, { headers })
    ]);
    
    // Log the responses
    
    
    
    
    // Format the progress data
    let formattedProgress = progressRes.data;
    if (formattedProgress.overall_progress !== undefined && 
        typeof formattedProgress.overall_progress !== 'number') {
      formattedProgress.overall_progress = parseFloat(formattedProgress.overall_progress) || 0;
    }
    
    return {
      videos: videosRes.data || [],
      unlockedVideos: unlockedRes.data || [],
      progress: formattedProgress || {
        videos_passed: [],
        videos_failed: [],
        total_retries: 0,
        overall_progress: 0
      }
    };
  } catch (error) {
    
    
    
    // Return default data
    return {
      videos: [],
      unlockedVideos: [],
      progress: {
        videos_passed: [],
        videos_failed: [],
        total_retries: 0,
        overall_progress: 0
      }
    };
  }
};
