import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAppState } from '../contexts/AppStateContext';
import Navbar from '../components/Navbar';
import VideoCard from '../components/VideoCard';
import StatsCard from '../components/StatsCard';
import LoadingSpinner from '../components/LoadingSpinner';

// Import demo utility for testing (remove in production)
const Dashboard = () => {
  const { user } = useAuth();
  const { videos, unlockedVideos, progress, loading, lastUpdated } = useAppState();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  const totalVideos = videos.length;
  const passedVideos = progress?.videos_passed?.length || 0;
  const failedVideos = progress?.videos_failed?.length || 0;
  const totalRetries = progress?.total_retries || 0;
  const overallProgress = typeof progress?.overall_progress === 'number' ? progress.overall_progress : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg shadow-lg px-6 py-8 mb-8 text-white">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold">
                Welcome back, {user?.username}!
              </h1>
              <p className="mt-2 text-blue-100">
                Track your progress and continue learning
              </p>
              
              {/* Learning Status Section */}
              <div className="mt-4 pt-4 border-t border-blue-400 border-opacity-30">
                <div className="flex items-center">
                  <div className="w-full bg-blue-200 bg-opacity-30 rounded-full h-4 mr-2">
                    <div 
                      className="bg-white rounded-full h-4 transition-all duration-500 ease-out"
                      style={{ width: `${overallProgress}%` }}
                    ></div>
                  </div>
                  <span className="text-white font-medium whitespace-nowrap">
                    {overallProgress.toFixed(1)}% Complete
                  </span>
                </div>
                <p className="mt-2 text-xs text-blue-100 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Last updated: {new Date(lastUpdated).toLocaleTimeString()}
                </p>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="w-24 h-24 rounded-full bg-white bg-opacity-10 flex items-center justify-center border-4 border-blue-300 border-opacity-30">
                <div className="text-center">
                  <div className="text-3xl font-bold">{passedVideos}</div>
                  <div className="text-xs">Completed</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <StatsCard
            title="Total Videos"
            value={totalVideos}
            icon="📹"
            color="blue"
            description="Total video quizzes available"
          />
          <StatsCard
            title="Quizzes Passed"
            value={passedVideos}
            icon="✅"
            color="green"
            description={`${(passedVideos/totalVideos*100).toFixed(0)}% success rate`}
          />
          <StatsCard
            title="Quizzes Failed"
            value={failedVideos}
            icon="❌"
            color="red"
            description={`${totalRetries} total retries`}
          />
          <StatsCard
            title="Progress Status"
            value={`${overallProgress.toFixed(1)}%`}
            icon="📊"
            color="purple"
            description={`${totalVideos - passedVideos - failedVideos} quizzes remaining`}
          />
        </div>

        {/* Videos Section */}
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="border-b border-gray-200 px-6 py-4 flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Available Video Quizzes
              </h3>
              <p className="text-sm text-gray-500">Complete all quizzes to earn your certificate</p>
            </div>
            <div className="text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded-full font-medium flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {passedVideos} of {totalVideos} completed
            </div>
          </div>
          
          <div className="px-6 py-5">
            {videos.length === 0 ? (
              <div className="text-center py-10">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <p className="mt-2 text-gray-500 font-medium">No videos available yet</p>
                <p className="text-gray-400 text-sm">Check back later for new content</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {videos.map((video, index) => {
                  // Check if video exists in passed or failed arrays
                  const isPassed = Array.isArray(progress?.videos_passed) && 
                    progress.videos_passed.some(pv => pv.id === video.id);
                  const isFailed = Array.isArray(progress?.videos_failed) && 
                    progress.videos_failed.some(fv => fv.id === video.id);
                  
                  // Get the next video to determine if this should be unlocked
                  const isCurrentUnlocked = unlockedVideos.some(uv => uv.id === video.id);
                  
                  // Find the first unlocked video that hasn't been completed
                  const nextAvailableVideo = videos.find(v => {
                    const vIsUnlocked = unlockedVideos.some(uv => uv.id === v.id);
                    const vIsPassed = Array.isArray(progress?.videos_passed) && 
                      progress.videos_passed.some(pv => pv.id === v.id);
                    const vIsFailed = Array.isArray(progress?.videos_failed) && 
                      progress.videos_failed.some(fv => fv.id === v.id);
                    return vIsUnlocked && !vIsPassed && !vIsFailed;
                  });
                  
                  // This is the next recommended video if it's the first available one
                  const isNextRecommended = nextAvailableVideo && nextAvailableVideo.id === video.id;
                  
                  // Debug logging
                  if (video.id === 13) {
                    
                  }
                    
                  return (
                    <VideoCard
                      key={`${video.id}`}
                      video={video}
                      isUnlocked={isCurrentUnlocked}
                      isPassed={isPassed}
                      isFailed={isFailed}
                      isRecommended={isNextRecommended}
                    />
                  );
                })}
              </div>
            )}
          </div>
          
          {/* Additional Info Section */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center text-sm text-gray-500">
              <div className="flex items-center mb-2 sm:mb-0">
                <span className="inline-flex items-center mr-4">
                  <span className="w-3 h-3 rounded-full bg-green-500 mr-1"></span>
                  Passed
                </span>
                <span className="inline-flex items-center mr-4">
                  <span className="w-3 h-3 rounded-full bg-red-500 mr-1"></span>
                  Failed
                </span>
                <span className="inline-flex items-center">
                  <span className="w-3 h-3 rounded-full bg-gray-300 mr-1"></span>
                  Locked
                </span>
              </div>
              <div>
                <button className="text-blue-600 hover:text-blue-700 font-medium">
                  Need help? Contact support
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
