import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
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
  const isRefreshingRef = useRef(false);

  // Function to fetch data
  const refreshData = useCallback(async () => {
    // Prevent multiple simultaneous calls
    if (isRefreshingRef.current) {
      console.log('AppState: Already refreshing, skipping duplicate call');
      return;
    }
    
    console.log('AppState: Starting data fetch');
    isRefreshingRef.current = true;
    
    // Clear any cached data
    localStorage.removeItem('dashboard_cache');
    
    try {
      setLoading(true);
      
      console.log('AppState: Fetching videos...');
      const videosResponse = await videoService.getAllVideos();
      console.log('AppState: Videos fetched:', videosResponse);
      
      console.log('AppState: Fetching unlocked videos...');
      const unlockedResponse = await videoService.getUnlockedVideos();
      console.log('AppState: Unlocked videos fetched:', unlockedResponse);
      
      console.log('AppState: Fetching user progress...');
      const progressResponse = await authService.getUserProgress();
      console.log('AppState: User progress fetched:', progressResponse);

      console.log('AppState: All data fetched successfully');

      setVideos(videosResponse || []);
      setUnlockedVideos(unlockedResponse || []);
      
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
      console.error('AppState: Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      
      // Set default data on error to prevent endless loading
      setVideos([]);
      setUnlockedVideos([]);
      setProgress({
        videos_passed: [],
        videos_failed: [],
        total_retries: 0,
        overall_progress: 0
      });
    } finally {
      console.log('AppState: Setting loading to false');
      setLoading(false);
      isRefreshingRef.current = false;
    }
  }, []);

  // Initial data fetch on mount
  useEffect(() => {
    console.log('AppState: Component mounted, starting initial data fetch');
    
    // Set a fallback timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      console.warn('AppState: Data fetch timeout after 15 seconds, forcing loading to false');
      setLoading(false);
      isRefreshingRef.current = false;
    }, 15000); // 15 seconds timeout
    
    refreshData().finally(() => {
      clearTimeout(timeoutId);
    });
    
    return () => clearTimeout(timeoutId);
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

  // Refresh when window gains focus (but not too frequently)
  useEffect(() => {
    let lastFocusRefresh = 0;
    
    const handleFocus = () => {
      const now = Date.now();
      // Only refresh if it's been more than 10 seconds since last focus refresh
      if (now - lastFocusRefresh > 10000) {
        console.log('Window gained focus, refreshing app data');
        lastFocusRefresh = now;
        refreshData();
      }
    };

    window.addEventListener('focus', handleFocus);
    
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, [refreshData]);

  // Refresh when page becomes visible (but not too frequently)
  useEffect(() => {
    let lastVisibilityRefresh = 0;
    
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        const now = Date.now();
        // Only refresh if it's been more than 10 seconds since last visibility refresh
        if (now - lastVisibilityRefresh > 10000) {
          console.log('Page became visible, refreshing app data');
          lastVisibilityRefresh = now;
          refreshData();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [refreshData]);

  // Auto-refresh every 60 seconds if user is active and on dashboard
  useEffect(() => {
    let intervalId;
    
    const startPolling = () => {
      intervalId = setInterval(() => {
        // Only refresh if document is visible and user is likely on dashboard
        if (!document.hidden && window.location.pathname === '/dashboard') {
          console.log('Auto-refreshing dashboard data (60s interval)');
          refreshData();
        }
      }, 60000); // 60 seconds (reduced from 30 seconds)
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
