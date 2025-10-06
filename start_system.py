#!/usr/bin/env python3
"""
System startup script for the video streaming application.
This script starts both the video stream server and opens the React app.
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

def start_stream_server():
    """Start the Flask video streaming server"""
    print("Starting video stream server...")
    try:
        subprocess.run([sys.executable, "stream_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting stream server: {e}")
    except KeyboardInterrupt:
        print("Stream server stopped by user")

def start_react_app():
    """Start the React development server"""
    print("Starting React application...")
    react_dir = "react_app"
    try:
        subprocess.run(["npm", "run", "dev"], cwd=react_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting React app: {e}")
    except KeyboardInterrupt:
        print("React app stopped by user")

def open_browser():
    """Open the browser to view the application"""
    time.sleep(3)  # Wait for servers to start
    print("Opening browser...")
    webbrowser.open("http://localhost:5173")  # Vite dev server default port

if __name__ == "__main__":
    print("🚀 Starting Video Streaming System")
    print("=" * 50)

    # Start stream server in a separate thread
    stream_thread = threading.Thread(target=start_stream_server, daemon=True)
    stream_thread.start()

    # Start React app in a separate thread
    react_thread = threading.Thread(target=start_react_app, daemon=True)
    react_thread.start()

    # Open browser
    open_browser()

    print("\n✅ System started!")
    print("📹 Video stream: http://localhost:5000")
    print("🖥️  React app: http://localhost:5173")
    print("\nPress Ctrl+C to stop all servers")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down system...")
        print("Goodbye!")
