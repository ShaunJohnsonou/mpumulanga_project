import React, { useState, useEffect, useRef } from 'react';

const VideoStream = ({ streamId }) => {
  const [config, setConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef(null);

  useEffect(() => {
    // Load configuration for this stream
    const loadConfig = async () => {
      try {
        const configPath = `/configs/rtsp-credential-${streamId}.json`;
        const response = await fetch(configPath);
        if (response.ok) {
          const configData = await response.json();
          setConfig(configData);
        } else {
          // Configuration file doesn't exist or can't be loaded
          setHasError(true);
          setIsLoading(false);
        }
      } catch (error) {
        console.error(`Error loading config for stream ${streamId}:`, error);
        setHasError(true);
        setIsLoading(false);
      }
    };

    loadConfig();
  }, [streamId]);

  useEffect(() => {
    if (config && config.enabled) {
      // For HTTP streams, we'll use an img element instead of video
      setIsLoading(true);
      setHasError(false);

      // Test if the stream is accessible
      const testImage = new Image();
      testImage.onload = () => {
        setIsLoading(false);
        setHasError(false);
      };
      testImage.onerror = () => {
        setIsLoading(false);
        setHasError(true);
      };

      // Set a timestamp to force reload and avoid caching
      const timestamp = new Date().getTime();
      testImage.src = `${config.url}?t=${timestamp}`;

      const interval = setInterval(() => {
        if (imgRef.current) {
          const timestamp = new Date().getTime();
          imgRef.current.src = `${config.url}?t=${timestamp}`;
        }
      }, 100); // Update every 100ms

      return () => clearInterval(interval);
    }
  }, [config]);

  if (!config) {
    return (
      <div className="video-container">
        <div className="video-placeholder">
          Stream {streamId} - Not Configured
        </div>
      </div>
    );
  }

  if (!config.enabled) {
    return (
      <div className="video-container">
        <div className="video-header">{config.name}</div>
        <div className="video-placeholder">
          Stream Disabled
        </div>
      </div>
    );
  }

  return (
    <div className="video-container">
      <div className="video-header">{config.name}</div>
      {isLoading && (
        <div className="video-loading">
          Connecting to stream...
        </div>
      )}
      {hasError ? (
        <div className="video-placeholder">
          Stream Detected - Connection Error
        </div>
      ) : (
        <img
          ref={imgRef}
          className="video-stream"
          alt={`Stream ${streamId}`}
          style={{ display: isLoading ? 'none' : 'block' }}
        />
      )}
    </div>
  );
};

export default VideoStream;
