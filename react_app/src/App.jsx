import React from 'react';
import VideoStream from './VideoStream';
import './index.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Multi-Stream Video Monitor</h1>
        <p>Real-time video surveillance system</p>
      </header>

      <main className="main-content">
        <div className="video-grid">
          <VideoStream streamId={1} />
          <VideoStream streamId={2} />
          <VideoStream streamId={3} />
          <VideoStream streamId={4} />
        </div>
      </main>
    </div>
  );
}

export default App;
