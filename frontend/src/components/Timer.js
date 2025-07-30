import React, { useState, useEffect, useCallback } from 'react';

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

const Timer = ({ initialTime, onTimeUpdate, onTimeEnd }) => {
  const [timeRemaining, setTimeRemaining] = useState(initialTime);
  // Using a constant instead of state since we don't need to toggle it
  const isRunning = true;

  // Update server every 10 seconds
  const SERVER_SYNC_INTERVAL = 10;

  // Callback to update time on server
  const updateServerTime = useCallback((time) => {
    if (onTimeUpdate) {
      onTimeUpdate(time);
    }
  }, [onTimeUpdate]);

  // For debugging
  

  useEffect(() => {
    let timerId;
    let syncCounter = 0;

    if (isRunning && timeRemaining > 0) {
      timerId = setInterval(() => {
        setTimeRemaining(prevTime => {
          const newTime = prevTime - 1;
          
          // Sync with server periodically
          syncCounter++;
          if (syncCounter >= SERVER_SYNC_INTERVAL) {
            syncCounter = 0;
            updateServerTime(newTime);
          }

          // Handle timer end
          if (newTime <= 0) {
            clearInterval(timerId);
            if (onTimeEnd) {
              // Use setTimeout to ensure this runs after the state update
              setTimeout(() => {
                
                onTimeEnd();
              }, 0);
              return 0; // Ensure time stops at zero
            }
          }
          
          return newTime;
        });
      }, 1000);
    }

    return () => {
      if (timerId) {
        clearInterval(timerId);
      }
    };
  }, [isRunning, timeRemaining, updateServerTime, onTimeEnd]);

  // Synchronize with initial time if it changes
  useEffect(() => {
    setTimeRemaining(initialTime);
  }, [initialTime]);

  // Removing unused function
  // const toggleTimer = () => {
  //   setIsRunning(!isRunning);
  // };

  const isLowTime = timeRemaining < 300; // Less than 5 minutes
  const isCritical = timeRemaining < 60; // Less than 1 minute

  return (
    <div className="flex items-center">
      <div 
        className={`
          flex items-center space-x-2 px-4 py-2 rounded-lg font-mono text-lg font-bold
          ${isCritical 
            ? 'bg-red-100 text-red-800 border-2 border-red-300' 
            : isLowTime 
            ? 'bg-yellow-100 text-yellow-800 border-2 border-yellow-300'
            : 'bg-blue-100 text-blue-800 border-2 border-blue-300'
          }
        `}
      >
        <svg 
          className={`w-5 h-5 ${isRunning ? 'animate-pulse' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" 
          />
        </svg>
        <span>
          {formatTime(timeRemaining)}
        </span>
      </div>
      
      {/* Removed pause button */}
    </div>
  );
};

export default Timer;
