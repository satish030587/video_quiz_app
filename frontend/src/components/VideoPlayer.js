import React, { useRef, useEffect, useState } from 'react';
import YouTube from 'react-youtube';

const VideoPlayer = ({ videoUrl, onEnded, autoplay = false }) => {
  const videoRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [videoType, setVideoType] = useState(null); // 'mp4' or 'youtube'
  const [youtubeId, setYoutubeId] = useState(null);
  
  // Extract YouTube ID from URL
  const getYoutubeId = (url) => {
    if (!url) return null;
    
    // Regular expression to extract YouTube ID from various YouTube URL formats
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length === 11) ? match[7] : null;
  };
  
  // Get the actual video URL from the videoUrl prop (which might be an object or string)
  const getActualVideoUrl = () => {
    if (!videoUrl) return '';
    
    // If videoUrl is an object with video_url or video_file properties
    if (typeof videoUrl === 'object' && videoUrl !== null) {
      return videoUrl.video_url || videoUrl.video_file || '';
    }
    
    // If videoUrl is already a string
    if (typeof videoUrl === 'string') {
      return videoUrl;
    }
    
    return '';
  };
  
  // Determine the video type and format URL when component mounts or URL changes
  useEffect(() => {
    // Get the actual video URL from the videoUrl prop (which might be an object or string)
    const getActualVideoUrl = () => {
      if (!videoUrl) return '';
      
      // If videoUrl is an object with video_url or video_file properties
      if (typeof videoUrl === 'object' && videoUrl !== null) {
        return videoUrl.video_url || videoUrl.video_file || '';
      }
      
      // If videoUrl is already a string
      if (typeof videoUrl === 'string') {
        return videoUrl;
      }
      
      return '';
    };
    
    const actualUrl = getActualVideoUrl();
    
    if (!actualUrl) {
      setVideoType(null);
      return;
    }

    // Check if it's a YouTube URL
    const ytId = getYoutubeId(actualUrl);
    if (ytId) {
      console.log('YouTube video detected, ID:', ytId);
      setVideoType('youtube');
      setYoutubeId(ytId);
      return;
    }
    
    // Otherwise it's a regular video file
    console.log('MP4 video detected:', actualUrl);
    setVideoType('mp4');
    
  }, [videoUrl]);
  
  // Format the URL for MP4 videos
  const getFormattedVideoUrl = () => {
    const actualUrl = getActualVideoUrl();
    
    if (!actualUrl || videoType === 'youtube') return null;
    
    // If URL is already a full URL (http/https), use it as is
    if (actualUrl.startsWith('http://') || actualUrl.startsWith('https://')) {
      return actualUrl;
    }
    
    // If it's a relative path, prefix with API base URL
    return `http://localhost:8000${actualUrl}`;
  };

  // YouTube player options
  const youtubeOpts = {
    height: '100%',
    width: '100%',
    playerVars: {
      autoplay: autoplay ? 1 : 0,
      controls: 1,
      disablekb: 0,
      rel: 0, // Don't show related videos
      modestbranding: 1,
    },
  };

  // Handle YouTube player state changes
  const handleYoutubeStateChange = (event) => {
    // YouTube state 0 is "ended"
    if (event.data === 0 && onEnded) {
      onEnded();
    }
    
    // YouTube state -1 is "unstarted"
    // YouTube state 1 is "playing"
    if (event.data === 1) {
      setLoading(false);
    }
  };

  // Handle YouTube player errors
  const handleYoutubeError = (event) => {
    console.error('YouTube error:', event);
    setError('Failed to load YouTube video. Please try again later.');
    setLoading(false);
  };

  // Handle YouTube player ready
  const handleYoutubeReady = (event) => {
    setLoading(false);
  };

  // Set up event listeners for MP4 video
  useEffect(() => {
    if (videoType !== 'mp4') return;
    
    const videoElement = videoRef.current;
    if (!videoElement) return;
    
    // Add event listeners
    if (onEnded) {
      videoElement.addEventListener('ended', onEnded);
    }
    
    videoElement.addEventListener('loadeddata', () => {
      setLoading(false);
    });
    
    videoElement.addEventListener('error', (e) => {
      console.error('Video error:', e);
      setError('Failed to load video. Please try again later.');
      setLoading(false);
    });
    
    // Clean up event listeners on unmount
    return () => {
      if (onEnded) {
        videoElement.removeEventListener('ended', onEnded);
      }
      videoElement.removeEventListener('loadeddata', () => {
        setLoading(false);
      });
      videoElement.removeEventListener('error', () => {
        setError('Failed to load video. Please try again later.');
        setLoading(false);
      });
    };
  }, [videoType, onEnded]);

  // Get the formatted URL for MP4 videos
  const formattedVideoUrl = getFormattedVideoUrl();

  // Log debugging info
  useEffect(() => {
    console.log('VideoPlayer debug:', {
      videoUrl,
      videoType,
      youtubeId,
      formattedVideoUrl
    });
  }, [videoUrl, videoType, youtubeId, formattedVideoUrl]);

  return (
    <div className="relative w-full aspect-video bg-gray-900 rounded-lg overflow-hidden shadow-lg">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-10">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
        </div>
      )}
      
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-10">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p>{error}</p>
          </div>
        </div>
      )}
      
      {videoType === 'youtube' && youtubeId ? (
        <div className="w-full h-full">
          <YouTube
            videoId={youtubeId}
            opts={youtubeOpts}
            onStateChange={handleYoutubeStateChange}
            onReady={handleYoutubeReady}
            onError={handleYoutubeError}
            className="w-full h-full"
          />
        </div>
      ) : formattedVideoUrl ? (
        <div>
          <video
            ref={videoRef}
            className="w-full h-full"
            controls
            autoPlay={autoplay}
            controlsList="nodownload"
            onContextMenu={(e) => e.preventDefault()} // Prevent right-click
            playsInline // Better mobile support
          >
            <source src={formattedVideoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      ) : (
        <div className="w-full h-full flex items-center justify-center text-white">
          <p>No video available</p>
        </div>
      )}
      
      <div className="absolute bottom-4 right-4 flex space-x-2">
        {process.env.NODE_ENV === 'development' && (
          <button
            onClick={onEnded}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            Skip Video (Dev Only)
          </button>
        )}
      </div>
    </div>
  );
};

export default VideoPlayer;
