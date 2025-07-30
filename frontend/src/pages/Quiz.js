import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { quizService, videoService } from '../services';
import { useAppState } from '../contexts/AppStateContext';
import VideoPlayer from '../components/VideoPlayer';
import Timer from '../components/Timer';
import LoadingSpinner from '../components/LoadingSpinner';

const Quiz = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const { triggerRefresh } = useAppState();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [video, setVideo] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [attemptId, setAttemptId] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [quizStatus, setQuizStatus] = useState('loading'); // loading, watching, answering, submitting, completed
  const [videoWatched, setVideoWatched] = useState(false);
  const [questionVisited, setQuestionsVisited] = useState([]);

  // Fetch video and check if user can attempt it
  useEffect(() => {
    const fetchVideoAndCheckAttempt = async () => {
      try {
        setLoading(true);
        // Get video details
        const videoData = await videoService.getVideoDetails(videoId);
        setVideo(videoData);
        
        // Check if user can attempt
        const attemptCheck = await videoService.canAttemptVideo(videoId);
        
        if (!attemptCheck.can_attempt) {
          setError(attemptCheck.reason);
          setQuizStatus('error');
          return;
        }
        
        // If there's an in-progress attempt, resume it
        if (attemptCheck.status === 'resume' && attemptCheck.attempt_id) {
          setAttemptId(attemptCheck.attempt_id);
          setTimeRemaining(attemptCheck.time_remaining);
          setQuizStatus('answering');
          
          // Load previously submitted answers
          try {
            
            const userAnswers = await quizService.getUserAnswers(attemptCheck.attempt_id);
            
            
            // Get questions first, then process answers
            
            const questionsData = await quizService.getVideoQuestions(videoId);
            
            
            if (Array.isArray(questionsData) && questionsData.length > 0) {
              setQuestions(questionsData);
              
              // Build a map of question ID to selected answer ID
              const answersMap = {};
              const visitedQuestionIndices = [];
              
              userAnswers.forEach(ua => {
                if (ua.selected_answer) {
                  answersMap[ua.question] = ua.selected_answer;
                  
                  // Find the index of this question in our questions array
                  const questionIndex = questionsData.findIndex(q => q.id === ua.question);
                  if (questionIndex !== -1 && !visitedQuestionIndices.includes(questionIndex)) {
                    visitedQuestionIndices.push(questionIndex);
                  }
                }
              });
              
              setSelectedAnswers(answersMap);
              setQuestionsVisited(visitedQuestionIndices);
              
              
              
            } else {
              
              setError("No questions available for this video. Please contact support.");
              setQuizStatus('error');
            }
          } catch (err) {
            
            setError("Failed to load quiz data. Please try again later.");
          }
        } else {
          setQuizStatus('watching');
        }

        // Get questions
        try {
          
          const questionsData = await quizService.getVideoQuestions(videoId);
          
          
          if (Array.isArray(questionsData) && questionsData.length > 0) {
            setQuestions(questionsData);
          } else {
            
            setError("No questions available for this video. Please contact support.");
            setQuizStatus('error');
          }
        } catch (err) {
          
          setError("Failed to load questions. Please try again later.");
          setQuizStatus('error');
        }
        
        setLoading(false);
      } catch (err) {
        
        setError('Failed to load quiz data. Please try again later.');
        setLoading(false);
      }
    };

    fetchVideoAndCheckAttempt();
  }, [videoId]);

  // Start quiz after video is watched
  const handleVideoEnded = () => {
    
    setVideoWatched(true);
    startQuiz();
  };

  const startQuiz = async () => {
    try {
      
      setLoading(true);
      setError(null); // Clear any previous errors
      
      // Start a new quiz attempt
      const attempt = await quizService.startQuizAttempt(videoId);
      
      
      setAttemptId(attempt.id);
      setTimeRemaining(attempt.time_remaining);
      setQuizStatus('answering');
      setLoading(false);
    } catch (err) {
      
      
      
      let errorMessage = 'Failed to start quiz. Please try again later.';
      
      // Provide more specific error messages
      if (err.response?.status === 400) {
        errorMessage = err.response.data?.detail || 'Bad request - check if you have available attempts.';
      } else if (err.response?.status === 401) {
        errorMessage = 'You are not authorized. Please log in again.';
      } else if (err.response?.status === 404) {
        errorMessage = 'Video not found.';
      }
      
      setError(errorMessage);
      setLoading(false);
    }
  };

  // Save answer to server
  const handleAnswerSelect = async (questionId, answerId) => {
    try {
      // Update local state
      setSelectedAnswers(prev => ({
        ...prev,
        [questionId]: answerId
      }));

      // Add to visited questions
      if (!questionVisited.includes(currentQuestionIndex)) {
        setQuestionsVisited(prev => [...prev, currentQuestionIndex]);
      }

      // Submit answer to server
      await quizService.submitAnswer(attemptId, questionId, answerId);
    } catch (err) {
      
      // We could show a toast notification here
    }
  };

  // Update timer on server periodically
  const updateTimerOnServer = useCallback(async (timeLeft) => {
    if (attemptId && quizStatus === 'answering') {
      try {
        await quizService.updateTimer(attemptId, timeLeft);
      } catch (err) {
        
      }
    }
  }, [attemptId, quizStatus]);

  // Handle timer end
  const handleTimerEnd = async () => {
    try {
      
      setQuizStatus('submitting');
      
      // Ensure any pending answer submissions are completed
      const pendingAnswers = Object.entries(selectedAnswers).map(([questionId, answerId]) => {
        return quizService.submitAnswer(attemptId, questionId, answerId)
          .catch(err => {
            
            // Continue with other submissions even if one fails
            return null;
          });
      });
      
      // Wait for all answer submissions to complete
      await Promise.all(pendingAnswers);
      
      // Then finish the quiz attempt
      await quizService.finishQuizAttempt(attemptId);
      
      // Mark quiz as completed and trigger refresh
      localStorage.setItem('quiz_completed', Date.now().toString());
      triggerRefresh();
      
      navigate(`/quiz-result/${attemptId}`);
    } catch (err) {
      
      setError('Failed to submit quiz. Please try again.');
      setQuizStatus('answering');
    }
  };

  const handleSubmitQuiz = async () => {
    try {
      setQuizStatus('submitting');
      await quizService.finishQuizAttempt(attemptId);
      
      // Mark quiz as completed and trigger refresh
      localStorage.setItem('quiz_completed', Date.now().toString());
      triggerRefresh();
      
      navigate(`/quiz-result/${attemptId}`);
    } catch (err) {
      
      setError('Failed to submit quiz. Please try again.');
      setQuizStatus('answering');
    }
  };

  const navigateToQuestion = (index) => {
    setCurrentQuestionIndex(index);
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
          <button 
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex] || {};

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Quiz Header */}
        <div className="bg-blue-600 text-white p-4">
          <h1 className="text-xl font-bold">{video?.title || "Loading video..."}</h1>
          {quizStatus === 'answering' && (
            <div className="mt-2">
              <div className="mb-2 text-white">
                <small>Time Remaining: {timeRemaining || 0} seconds</small>
              </div>
              <Timer 
                initialTime={timeRemaining || 600} // Default to 10 minutes if undefined
                onTimeUpdate={updateTimerOnServer}
                onTimeEnd={handleTimerEnd} 
              />
            </div>
          )}
        </div>

        {/* Video Section - Show only in watching mode */}
        {quizStatus === 'watching' && (
          <div className="p-4">
            <div className="relative w-full" style={{ height: "auto", minHeight: "360px" }}>
              <VideoPlayer 
                videoUrl={{
                  video_file: video?.video_file || '',
                  video_url: video?.video_url || ''
                }} 
                onVideoEnded={handleVideoEnded} 
                isQuizActive={false}
              />
            </div>
            <div className="mt-4 text-center">
              <p className="text-gray-600 mb-4">
                Watch the video completely before attempting the quiz. 
                You will have {video?.time_limit} minutes to complete the quiz.
              </p>
              <button
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mr-4"
                onClick={() => setVideoWatched(true)}
              >
                {videoWatched ? "Video Watched" : "Mark as Watched"}
              </button>
              {videoWatched && (
                <button
                  className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={startQuiz}
                >
                  Start Quiz
                </button>
              )}
            </div>
          </div>
        )}

        {/* Quiz Section - Show only in answering mode */}
        {quizStatus === 'answering' && (
          <div className="p-4">
            {/* Question Navigation */}
            <div className="flex flex-wrap gap-2 mb-4">
              {questions.map((q, index) => (
                <button
                  key={q.id}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                    currentQuestionIndex === index
                      ? 'bg-blue-600 text-white'
                      : selectedAnswers[q.id]
                      ? 'bg-green-100 text-green-800 border border-green-500'
                      : questionVisited.includes(index)
                      ? 'bg-yellow-100 text-yellow-800 border border-yellow-500'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                  onClick={() => navigateToQuestion(index)}
                >
                  {index + 1}
                </button>
              ))}
            </div>

            {/* Current Question */}
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-4">
                Question {currentQuestionIndex + 1} of {questions.length}
              </h2>
              <p className="text-lg mb-4">{currentQuestion.question_text}</p>

              {/* Answer Options */}
              <div className="space-y-3">
                {currentQuestion.answers?.map(answer => (
                  <div
                    key={answer.id}
                    className={`p-3 rounded border ${
                      selectedAnswers[currentQuestion.id] === answer.id
                        ? 'bg-blue-100 border-blue-500'
                        : 'hover:bg-gray-100 border-gray-300'
                    } cursor-pointer`}
                    onClick={() => handleAnswerSelect(currentQuestion.id, answer.id)}
                  >
                    {answer.answer_text}
                  </div>
                ))}
              </div>
            </div>

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-6">
              <button
                className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                onClick={prevQuestion}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </button>

              {currentQuestionIndex < questions.length - 1 ? (
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={nextQuestion}
                >
                  Next
                </button>
              ) : (
                <button
                  className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  onClick={handleSubmitQuiz}
                >
                  Submit Quiz
                </button>
              )}
            </div>

            {/* Submit Button - Show only when all questions are visited */}
            {questionVisited.length === questions.length && currentQuestionIndex !== questions.length - 1 && (
              <div className="mt-6 text-center">
                <button
                  className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  onClick={handleSubmitQuiz}
                >
                  Submit Quiz
                </button>
              </div>
            )}
          </div>
        )}

        {/* Loading state while submitting */}
        {quizStatus === 'submitting' && (
          <div className="p-8 text-center">
            <LoadingSpinner />
            <p className="mt-4 text-gray-600">Submitting your answers...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Quiz;
