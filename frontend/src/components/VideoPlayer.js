import React, { useEffect, useRef, useState } from 'react';
import ReactPlayer from 'react-player';
import './VideoPlayer.css';
import { videoService } from '../services';

const VideoPlayer = ({ 
  videoUrl, 
  onVideoEnded, 
  onTimeUpdate, 
  isQuizActive,
  resetVideoOnNewQuiz = false 
}) => {
  const videoRef = useRef(null);
  const reactPlayerRef = useRef(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [videoSource, setVideoSource] = useState('');
  const [currentSourceIndex, setCurrentSourceIndex] = useState(0);
  const [sources, setSources] = useState([]);
  const [isYouTube, setIsYouTube] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);
  
  // Check fullscreen status
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);
  
  // Process video sources on component mount or when videoUrl changes
  useEffect(() => {
    
    setLoading(true);
    setError(null);
    setInitialLoadComplete(false); // Reset on new video load
    
    // Create an array of potential video sources with local files prioritized
    let videoSources = [];
    
    // Handle case when videoUrl is an object containing video_file and video_url
    if (typeof videoUrl === 'object') {
      // Prioritize local file over external URL - this is crucial
      if (videoUrl.video_file) {
        videoSources.push(videoUrl.video_file);
      }
      if (videoUrl.video_url && videoUrl.video_url !== videoUrl.video_file) {
        videoSources.push(videoUrl.video_url);
      }
    } 
    // Handle case when videoUrl is a string
    else if (typeof videoUrl === 'string' && videoUrl) {
      videoSources.push(videoUrl);
    }
    
    // If no sources found, set error
    if (videoSources.length === 0) {
      
      setError("No video URL provided");
      setLoading(false);
      return;
    }
    
    // Process each URL to ensure they are properly formatted
    const processedSources = videoSources.map(url => {
      // If it's a relative URL (starts with /media) or just a filename, construct the full URL
      if (url.startsWith('/media') || (!url.startsWith('http') && !url.startsWith('/'))) {
        // For media files, use the streaming endpoint
        if (typeof videoUrl === 'object' && videoUrl.id) {
          return videoService.streamVideo(videoUrl.id);
        }
        
        // Fallback to direct URL if no video ID
        const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
        let processedUrl = `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
        
        // Add a cache-busting parameter for local files
        const timestamp = new Date().getTime();
        return `${processedUrl}?t=${timestamp}`;
      }
      return url;
    });
    
    setSources(processedSources);
    setCurrentSourceIndex(0); // Reset to first source
    
    
  }, [videoUrl]);
  
  // Function to get video blob
  const loadFullVideo = async (url) => {
    if (!url || isYouTube) return; // Skip for YouTube videos
    
    try {
      
      setLoading(true);
      
      // Fetch the video as a blob
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Range': 'bytes=0-', // Request the full video
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch video: ${response.status} ${response.statusText}`);
      }
      
      const videoBlob = await response.blob();
      const videoBlobUrl = URL.createObjectURL(videoBlob);
      
      
      setVideoSource(videoBlobUrl);
      setLoading(false);
      setInitialLoadComplete(true);
    } catch (error) {
      
      // Fall back to streaming if full download fails
      
    }
  };

  // Update video source when sources array or currentSourceIndex changes
  useEffect(() => {
    if (sources.length > 0 && currentSourceIndex < sources.length) {
      const source = sources[currentSourceIndex];
      
      // Check if the source is a YouTube or other streaming video
      // YouTube URLs can be in multiple formats, so check specifically for these patterns
      const isYouTubeUrl = source.includes('youtube.com') || source.includes('youtu.be');
      setIsYouTube(isYouTubeUrl);
      
      
      
      
      if (isYouTubeUrl) {
        // For YouTube, just set the source directly
        setVideoSource(source);
      } else {
        // For local videos, try to preload the full video
        loadFullVideo(source).catch(() => {
          // If preloading fails, fall back to regular streaming
          setVideoSource(source);
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sources, currentSourceIndex]);

  // Set up video event listeners
  useEffect(() => {
    const videoElement = videoRef.current;
    
    if (!videoElement || isYouTube) return;
    
    const handleVideoLoaded = () => {
      
      setLoading(false);
      setInitialLoadComplete(true);
    };
    
    const handleVideoError = (e) => {
      
      setError(`Error loading video: ${e.target.error ? e.target.error.message : 'Unknown error'}`);
      setLoading(false);
      
      // Try next source if available
      if (currentSourceIndex < sources.length - 1) {
        setCurrentSourceIndex(prevIndex => prevIndex + 1);
      }
    };
    
    const handleEnded = () => {
      
      if (onVideoEnded) onVideoEnded();
    };
    
    const handleTimeUpdate = () => {
      if (onTimeUpdate) onTimeUpdate(videoElement.currentTime);
    };
    
    // Add event listeners
    videoElement.addEventListener('loadeddata', handleVideoLoaded);
    videoElement.addEventListener('error', handleVideoError);
    videoElement.addEventListener('ended', handleEnded);
    videoElement.addEventListener('timeupdate', handleTimeUpdate);
    
    // Clean up event listeners on unmount
    return () => {
      videoElement.removeEventListener('loadeddata', handleVideoLoaded);
      videoElement.removeEventListener('error', handleVideoError);
      videoElement.removeEventListener('ended', handleEnded);
      videoElement.removeEventListener('timeupdate', handleTimeUpdate);
    };
  }, [onVideoEnded, onTimeUpdate, currentSourceIndex, sources, isYouTube]);

  // Reset video when a new quiz becomes active (if enabled)
  useEffect(() => {
    if (resetVideoOnNewQuiz && !isQuizActive) {
      if (isYouTube && reactPlayerRef.current) {
        reactPlayerRef.current.seekTo(0);
        // Don't attempt to autoplay - let user start playback
      } else if (videoRef.current) {
        videoRef.current.currentTime = 0;
        // Don't attempt autoplay - browsers will block it
        // videoRef.current.play().catch(e => );
      }
    }
  }, [isQuizActive, resetVideoOnNewQuiz, isYouTube]);

  // Try the next source manually
  const tryNextSource = () => {
    if (currentSourceIndex < sources.length - 1) {
      setCurrentSourceIndex(prevIndex => prevIndex + 1);
      setError(null);
      setLoading(true);
      setInitialLoadComplete(false); // Reset on new source
    }
  };

  return (
    <div className="relative w-full h-full video-container">
      {/* Debug info */}
      <div className="mb-2 p-2 bg-gray-100 text-xs">
        <div>Available sources: {sources.length}</div>
        <div>Current source: {currentSourceIndex + 1}/{sources.length}</div>
        <div>Current URL: {videoSource || 'None'}</div>
        <div>Type: {isYouTube ? 'YouTube/Streaming' : 'Local File'}</div>
        {error && <div className="text-red-500">Error: {error}</div>}
      </div>
      
      {/* Loading state - only show on initial load, not during buffering after video has started playing */}
      {loading && !initialLoadComplete && (
        <div className={isFullscreen ? "fullscreen-spinner" : "absolute inset-0 flex items-center justify-center bg-gray-200 bg-opacity-50 z-50"}>
          <div className={isFullscreen ? "spinner-container" : "text-center"}>
            <div className={isFullscreen ? "spinner" : "inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"}></div>
            <p className={isFullscreen ? "spinner-text" : "mt-2 font-medium"}>Loading video...</p>
          </div>
        </div>
      )}
      
      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-100 border border-red-300 rounded">
          <p className="text-red-700">{error}</p>
          <p className="text-sm mt-2">Failed to load: {videoSource}</p>
          {currentSourceIndex < sources.length - 1 && (
            <button 
              className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
              onClick={tryNextSource}
            >
              Try next source
            </button>
          )}
        </div>
      )}
      
      {/* Video element - conditionally render ReactPlayer for YouTube/streaming or regular video tag for local files */}
      {videoSource && isYouTube ? (
        <ReactPlayer
          ref={reactPlayerRef}
          url={videoSource}
          className="w-full rounded-lg shadow-lg react-player"
          width="100%"
          height="auto"
          controls={true}
          playing={false} // Changed from !isQuizActive to false to prevent autoplay errors
          onEnded={onVideoEnded}
          onProgress={(state) => {
            if (onTimeUpdate) onTimeUpdate(state.playedSeconds);
          }}
          onError={(e) => {
            
            setError(`Error loading streaming video: ${e?.message || 'Unknown error'}`);
            setLoading(false);
          }}
          onBuffer={() => {
            // Only set loading if initial load hasn't completed
            if (!initialLoadComplete) setLoading(true);
          }}
          onBufferEnd={() => setLoading(false)}
          onReady={() => {
            setLoading(false);
            setInitialLoadComplete(true);
          }}
          config={{
            youtube: {
              playerVars: { 
                origin: window.location.origin,
                modestbranding: 1,
                rel: 0,
                // Enable preloading for YouTube videos
                preload: 1
              }
            },
            file: {
              attributes: {
                crossOrigin: "anonymous",
                preload: "auto"
              },
              forceVideo: true,
              forcedPreload: true
            }
          }}
        />
      ) : (
        <video
          ref={videoRef}
          className="w-full rounded-lg shadow-lg"
          controls
          src={videoSource}
          autoPlay={false} // Changed from true to false to prevent autoplay errors
          preload="auto" // Force preloading of the entire video
          onCanPlayThrough={() => {
            setLoading(false);
            setInitialLoadComplete(true);
          }}
          onLoadStart={() => {
            // Only set loading for initial load
            if (!initialLoadComplete) setLoading(true);
          }}
          onWaiting={() => {
            // Only set loading for initial load
            if (!initialLoadComplete) setLoading(true);
          }}
          onPlaying={() => {
            setLoading(false);
            setInitialLoadComplete(true);
          }}
          key={videoSource} // Important: Re-mount video when source changes
        >
          Your browser does not support the video tag.
        </video>
      )}
    </div>
  );
};

export default VideoPlayer;
