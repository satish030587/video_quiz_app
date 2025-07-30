import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { quizService } from '../services';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAppState } from '../contexts/AppStateContext';

const QuizResult = () => {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const { triggerRefresh } = useAppState();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        
        setLoading(true);
        const resultData = await quizService.getQuizResult(attemptId);
        
        
        // Make sure percentage is properly formatted
        if (resultData && resultData.percentage !== undefined) {
          // If percentage is a string, parse it to a number
          if (typeof resultData.percentage === 'string') {
            resultData.percentage = parseFloat(resultData.percentage);
          }
          
          
        }
        
        setResult(resultData);
        setLoading(false);
      } catch (err) {
        
        setError('Failed to load quiz result. Please try again later.');
        setLoading(false);
      }
    };

    fetchResult();
  }, [attemptId, retryCount]);

  const handleBackToDashboard = () => {
    triggerRefresh(); // Trigger refresh before navigating
    navigate('/dashboard');
  };
  
  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  // Format percentage properly
  const formatPercentage = (value) => {
    if (value === null || value === undefined) return '0.0';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    return isNaN(numValue) ? '0.0' : numValue.toFixed(1);
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4 flex flex-col items-center justify-center min-h-[50vh]">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">Loading quiz results...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg shadow-sm" role="alert">
          <h3 className="font-bold text-lg mb-2">Error Loading Results</h3>
          <p className="mb-4">{error}</p>
          <div className="flex space-x-4">
            <button 
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              onClick={handleRetry}
            >
              Try Again
            </button>
            <button 
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              onClick={handleBackToDashboard}
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Calculate some derived data for the display
  const totalQuestions = result?.total_questions || 0;
  const correctAnswers = result?.correct_answers || 0;
  const attemptNumber = result?.attempt_number || 0;
  const percentage = result?.percentage; 
  const isPassed = result?.is_passed || false;
  const passingThreshold = 70; // Default passing threshold
  
  // Ensure percentage is correctly calculated
  const displayPercentage = formatPercentage(percentage);
  const attemptsRemaining = 2 - attemptNumber;

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden max-w-4xl mx-auto">
        {/* Result Header */}
        <div className={`p-6 text-white ${isPassed ? 'bg-green-600' : 'bg-red-600'}`}>
          <h1 className="text-2xl font-bold mb-2">Quiz Results</h1>
          <div className="text-xl">
            {isPassed 
              ? 'Congratulations! You passed the quiz.' 
              : 'Sorry, you did not pass the quiz.'}
          </div>
        </div>

        {/* Score Visualization */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-center items-center">
            <div className="relative w-40 h-40 flex justify-center items-center">
              {/* Score Circle */}
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <circle 
                  cx="50" cy="50" r="45" 
                  fill="none" 
                  stroke="#eee" 
                  strokeWidth="10"
                />
                <circle 
                  cx="50" cy="50" r="45" 
                  fill="none" 
                  stroke={isPassed ? "#10B981" : "#EF4444"} 
                  strokeWidth="10"
                  strokeDasharray="282.7"
                  strokeDashoffset={282.7 - (282.7 * parseFloat(displayPercentage) / 100)}
                  transform="rotate(-90 50 50)"
                />
              </svg>
              {/* Score Text */}
              <div className="absolute inset-0 flex flex-col justify-center items-center">
                <span className={`text-3xl font-bold ${isPassed ? 'text-green-600' : 'text-red-600'}`}>
                  {displayPercentage}%
                </span>
                <span className="text-sm text-gray-500">Score</span>
              </div>
            </div>
          </div>
        </div>

        {/* Result Statistics */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-100 p-4 rounded-lg">
              <h2 className="text-lg font-semibold mb-4">Score Summary</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span>Total Questions:</span>
                  <span className="font-medium">{totalQuestions}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Questions Attempted:</span>
                  <span className="font-medium">{result?.questions_attempted || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Correct Answers:</span>
                  <span className="font-medium">{correctAnswers}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Your Score:</span>
                  <span className={`font-bold ${isPassed ? 'text-green-600' : 'text-red-600'}`}>
                    {displayPercentage}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Passing Score:</span>
                  <span className="font-medium">{passingThreshold}%</span>
                </div>

                {/* Score bar visualization */}
                <div className="mt-2">
                  <div className="h-4 w-full bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${isPassed ? 'bg-green-500' : 'bg-red-500'}`}
                      style={{ width: `${Math.min(100, parseFloat(displayPercentage))}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0%</span>
                    <span>{passingThreshold}%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-100 p-4 rounded-lg">
              <h2 className="text-lg font-semibold mb-4">Attempt Details</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span>Status:</span>
                  <span className={`font-medium px-2 py-1 rounded ${isPassed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {isPassed ? 'Passed' : 'Failed'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Attempt Number:</span>
                  <span className="font-medium">{attemptNumber}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Score Gap:</span>
                  <span className="font-medium">
                    {isPassed 
                      ? `+${(parseFloat(displayPercentage) - passingThreshold).toFixed(1)}%`
                      : `-${(passingThreshold - parseFloat(displayPercentage)).toFixed(1)}%`}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Correct Rate:</span>
                  <span className="font-medium">
                    {totalQuestions > 0 
                      ? `${(correctAnswers / totalQuestions * 100).toFixed(1)}%`
                      : '0.0%'}
                  </span>
                </div>

                {!isPassed && attemptsRemaining > 0 && (
                  <div className="mt-4 p-3 bg-yellow-100 text-yellow-800 rounded">
                    <p className="font-medium">You have {attemptsRemaining} more attempt{attemptsRemaining !== 1 ? 's' : ''} remaining for this quiz.</p>
                    <p className="text-sm mt-1">Need {(passingThreshold - parseFloat(displayPercentage)).toFixed(1)}% more to pass.</p>
                  </div>
                )}
                
                {!isPassed && attemptsRemaining <= 0 && (
                  <div className="mt-4 p-3 bg-red-100 text-red-800 rounded">
                    <p className="font-medium">You have reached the maximum number of attempts for this quiz.</p>
                    <p className="text-sm mt-1">Please contact support if you need assistance.</p>
                  </div>
                )}
                
                {isPassed && (
                  <div className="mt-4 p-3 bg-green-100 text-green-800 rounded">
                    <p className="font-medium">Congratulations on passing this quiz!</p>
                    <p className="text-sm mt-1">You scored {(parseFloat(displayPercentage) - passingThreshold).toFixed(1)}% above the requirement.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="mt-8 text-center">
            <button
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow transition-colors"
              onClick={handleBackToDashboard}
            >
              {isPassed ? 'Continue Learning' : 'Back to Dashboard'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizResult;
