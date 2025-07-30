import React, { useState } from 'react';
import VideoPlayer from '../components/VideoPlayer';

const VideoTest = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [showPlayer, setShowPlayer] = useState(false);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    setShowPlayer(true);
  };
  
  const handleVideoEnded = () => {
    console.log('Video ended in test component');
    alert('Video ended!');
  };
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Video Player Test</h1>
      
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="Enter video URL or path"
            className="border rounded p-2 flex-grow"
          />
          <button 
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Load Video
          </button>
        </div>
      </form>
      
      {showPlayer && (
        <div className="mt-4">
          <h2 className="text-xl font-bold mb-2">Video Player</h2>
          <VideoPlayer 
            videoUrl={videoUrl} 
            onVideoEnded={handleVideoEnded}
            isQuizActive={false}
          />
        </div>
      )}
    </div>
  );
};

export default VideoTest;
