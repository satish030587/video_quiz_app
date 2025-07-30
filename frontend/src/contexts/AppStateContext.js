import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { videoService, authService } from '../services';

// Create the context
const AppStateContext = createContext();

// Create a custom hook to use the context
export const useAppState = () => useContext(AppStateContext);

// Provider component
export const AppStateProvider = ({ children }) => {
  const [videos, setVideos] = useState([]);
  const [unlockedVideos, setUnlockedVideos] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(Date.now());

  // Function to fetch data
  const refreshData = useCallback(async () => {
    console.log('AppState: Fetching fresh data');
    // Clear any cached data
    localStorage.removeItem('dashboard_cache');
    
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [videosResponse, unlockedResponse, progressResponse] = await Promise.all([
        videoService.getAllVideos(),
        videoService.getUnlockedVideos(),
        authService.getUserProgress(),
      ]);

      console.log('AppState: Data fetched successfully');

      setVideos(videosResponse);
      setUnlockedVideos(unlockedResponse);
      
      // Format progress data
      if (progressResponse && typeof progressResponse === 'object') {
        // Ensure overall_progress is a number
        if (progressResponse.overall_progress && 
            typeof progressResponse.overall_progress !== 'number') {
          progressResponse.overall_progress = parseFloat(progressResponse.overall_progress) || 0;
        }
        
        setProgress(progressResponse);
      } else {
        setProgress({
          videos_passed: [],
          videos_failed: [],
          total_retries: 0,
          overall_progress: 0
        });
      }
      
      // Update last updated timestamp
      setLastUpdated(Date.now());
    } catch (error) {
      console.error('AppState: Error fetching data:', error);
      // Set default progress on error
      setProgress({
        videos_passed: [],
        videos_failed: [],
        total_retries: 0,
        overall_progress: 0
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch on mount
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Listen for data change events (e.g., quiz completion)
  useEffect(() => {
    const handleDataChange = () => {
      console.log('Data change event detected, refreshing app data');
      refreshData();
    };

    // Listen for custom event
    window.addEventListener('dataChanged', handleDataChange);
    
    // Also listen for storage events for cross-tab updates
    const handleStorageChange = (e) => {
      if (e.key === 'quiz_completed' && e.newValue) {
        console.log('Quiz completion detected from storage, refreshing data');
        localStorage.removeItem('quiz_completed'); // Clean up
        refreshData();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('dataChanged', handleDataChange);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [refreshData]);

  // Refresh when window gains focus
  useEffect(() => {
    const handleFocus = () => {
      console.log('Window gained focus, refreshing app data');
      refreshData();
    };

    window.addEventListener('focus', handleFocus);
    
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, [refreshData]);

  // Refresh when page becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('Page became visible, refreshing app data');
        refreshData();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [refreshData]);

  // Auto-refresh every 30 seconds if user is active and on dashboard
  useEffect(() => {
    let intervalId;
    
    const startPolling = () => {
      intervalId = setInterval(() => {
        // Only refresh if document is visible and user is likely on dashboard
        if (!document.hidden && window.location.pathname === '/dashboard') {
          console.log('Auto-refreshing dashboard data (30s interval)');
          refreshData();
        }
      }, 30000); // 30 seconds
    };
    
    const stopPolling = () => {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
    };
    
    // Start polling when page becomes visible
    if (!document.hidden) {
      startPolling();
    }
    
    const handleVisibilityChangePolling = () => {
      if (document.hidden) {
        stopPolling();
      } else {
        startPolling();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChangePolling);
    
    return () => {
      stopPolling();
      document.removeEventListener('visibilitychange', handleVisibilityChangePolling);
    };
  }, [refreshData]);



  // The context value
  const value = {
    videos,
    unlockedVideos,
    progress,
    loading,
    refreshData,
    lastUpdated,
    // Utility function to trigger refresh from anywhere
    triggerRefresh: () => {
      console.log('Triggering manual data refresh');
      window.dispatchEvent(new CustomEvent('dataChanged'));
    }
  };

  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  );
};

export default AppStateContext;
