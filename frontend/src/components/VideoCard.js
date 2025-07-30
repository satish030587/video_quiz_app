import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { videoService, quizService } from '../services';
import { useAppState } from '../contexts/AppStateContext';
import Button from './Button';

const VideoCard = ({ video, isUnlocked, isPassed, isFailed, isRecommended = false }) => {
  const [loading, setLoading] = useState(false);
  const [attemptInfo, setAttemptInfo] = useState(null);
  const [attemptsUsed, setAttemptsUsed] = useState(0);
  const [passedScore, setPassedScore] = useState(null);
  const navigate = useNavigate();
  const { triggerRefresh } = useAppState();
  
  useEffect(() => {
    const fetchAttemptData = async () => {
      try {
        if (video.id) {
          // Clear previous data to force refresh
          setAttemptsUsed(0);
          setPassedScore(null);
          setAttemptInfo(null);
          
          const response = await videoService.canAttemptVideo(video.id);
          
          // Always update attempts used from response
          if (response && response.attempts_used !== undefined) {
            setAttemptsUsed(response.attempts_used);
          }
          
          // Store attempt info for later use
          setAttemptInfo(response);
          
          // If passed through the API response, update local state
          if (response && response.status === 'passed') {
            // Get the percentage from response if available
            if (response.percentage !== undefined && response.percentage !== null) {
              setPassedScore(response.percentage);
            }
          } 
          // If passed based on prop but we need to fetch the score
          else if (isPassed && video.id) {
            try {
              const attemptsResponse = await quizService.getUserAttempts();
              const videoAttempts = attemptsResponse.filter(
                attempt => attempt.video === video.id && attempt.is_passed
              );
              if (videoAttempts.length > 0) {
                // Find highest score
                const bestAttempt = videoAttempts.reduce((prev, current) => 
                  (prev.percentage > current.percentage) ? prev : current
                );
                setPassedScore(bestAttempt.percentage);
              }
            } catch (error) {
              // Handle error silently - user attempts data not critical
            }
          }
        }
      } catch (error) {
        // Handle error silently - attempt data not critical for display
      }
    };
    
    fetchAttemptData();
    // Remove passedScore from dependency array to prevent infinite loops
  }, [video.id, video.title, isPassed, isFailed]);

  const checkAttemptStatus = async () => {
    // If already passed, don't do anything
    if (isPassed) {
      return;
    }
    
    try {
      setLoading(true);
      const response = await videoService.canAttemptVideo(video.id);
      setAttemptInfo(response);
      
      if (response.can_attempt) {
        // Trigger refresh when navigating to a quiz
        triggerRefresh();
        
        if (response.status === 'resume') {
          navigate(`/quiz/${video.id}`);
        } else {
          navigate(`/quiz/${video.id}`);
        }
      }
    } catch (error) {
      // Handle error silently
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = () => {
    if (isPassed) {
      return <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
        Passed
      </span>;
    }
    if (isFailed) {
      return <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
        Failed
      </span>;
    }
    if (!isUnlocked) {
      return <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        Locked
      </span>;
    }
    if (isRecommended) {
      return <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
        Recommended
      </span>;
    }
    return <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
      </svg>
      Available
    </span>;
  };

  const getButtonText = () => {
    if (!isUnlocked) return 'Locked';
    
    // Check if passed based on either the prop or the API response
    if (isPassed || (attemptInfo && attemptInfo.status === 'passed')) {
      return 'Completed';
    }
    
    if (isFailed || (attemptInfo && attemptInfo.status === 'max_attempts')) {
      return 'Maximum Attempts Reached';
    }
    
    // Show 'Resume Quiz' for in-progress attempts
    if (attemptInfo && attemptInfo.status === 'resume') {
      return 'Resume Quiz';
    }
    
    return 'Start Quiz';
  };

  const isButtonDisabled = () => {
    // Not unlocked or has reached maximum attempts without passing
    return !isUnlocked || 
           isPassed || 
           (attemptInfo && attemptInfo.status === 'passed') || 
           (isFailed && !isPassed) || 
           (attemptInfo && attemptInfo.status === 'max_attempts' && !isPassed);
  };

  const getRibbonInfo = () => {
    if (isPassed) {
      return {
        show: true,
        text: 'COMPLETED',
        bgColor: 'bg-green-500',
        textColor: 'text-white'
      };
    }
    
    if (isFailed) {
      return {
        show: true,
        text: 'FAILED',
        bgColor: 'bg-red-500',
        textColor: 'text-white'
      };
    }
    
    if (isRecommended) {
      return {
        show: true,
        text: 'NEXT UP',
        bgColor: 'bg-blue-500',
        textColor: 'text-white'
      };
    }
    
    if (!isUnlocked) {
      return {
        show: true,
        text: 'LOCKED',
        bgColor: 'bg-gray-500',
        textColor: 'text-white'
      };
    }
    
    return { show: false };
  };

  const ribbonInfo = getRibbonInfo();

  return (
    <div className={`bg-white border rounded-lg shadow-sm hover:shadow-md transition-all duration-300 h-full flex flex-col relative overflow-hidden
      ${isRecommended ? 'ring-2 ring-blue-500' : ''}
      ${isPassed ? 'border-green-200' : isFailed ? 'border-red-200' : !isUnlocked ? 'border-gray-200 opacity-80' : 'border-blue-200'}`}
    >
      {/* Sequence Number Tag */}
      <div className="absolute top-0 left-0 w-8 h-8 flex items-center justify-center bg-gray-800 text-white font-bold text-sm rounded-br-lg">
        {video.sequence_number}
      </div>
      
      {ribbonInfo.show && (
        <div className={`absolute -right-10 top-5 ${ribbonInfo.bgColor} ${ribbonInfo.textColor} px-12 py-1 transform rotate-45 text-xs font-bold`}>
          {ribbonInfo.text}
        </div>
      )}
      
      <div className="p-5 flex flex-col h-full">
        <div className="flex items-start justify-between mb-3">
          <h4 className="text-lg font-semibold text-gray-900 pr-2">
            {video.title}
          </h4>
          {getStatusBadge()}
        </div>
        
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {video.description}
        </p>
        
        <div className="grid grid-cols-3 gap-2 text-xs text-gray-500 mb-4">
          <div className="bg-gray-50 rounded p-2 text-center">
            <div className="font-medium">{video.time_limit}min</div>
            <div className="text-gray-400">Time</div>
          </div>
          <div className="bg-gray-50 rounded p-2 text-center">
            <div className="font-medium">{video.passing_percentage}%</div>
            <div className="text-gray-400">Pass Rate</div>
          </div>
          <div className="bg-gray-50 rounded p-2 text-center">
            <div className="font-medium">{attemptsUsed}/2</div>
            <div className="text-gray-400">Attempts</div>
          </div>
        </div>
        
        {isPassed && passedScore !== null && (
          <div className="mb-4 bg-green-50 rounded-lg p-3 flex items-center">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mr-3">
              <span className="text-green-700 font-bold">{passedScore.toFixed(0)}%</span>
            </div>
            <div>
              <div className="text-green-700 font-medium">Score</div>
              <div className="text-green-600 text-xs">Quiz passed successfully</div>
            </div>
          </div>
        )}
        
        {attemptInfo && !attemptInfo.can_attempt && !isPassed && (
          <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
            <p className="text-yellow-800 text-sm">{attemptInfo.reason}</p>
            {attemptInfo.attempts_left > 0 && (
              <p className="text-yellow-700 text-xs mt-1">
                Attempts remaining: {attemptInfo.attempts_left}
              </p>
            )}
          </div>
        )}
        
        <div className="mt-auto">
          <Button
            onClick={checkAttemptStatus}
            disabled={isButtonDisabled()}
            loading={loading}
            variant={isPassed || (attemptInfo && attemptInfo.status === 'passed') ? 'completed' : isRecommended ? 'primary' : 'secondary'}
            className={`w-full ${isRecommended ? 'py-3' : ''}`}
          >
            {loading ? 'Checking...' : getButtonText()}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;
