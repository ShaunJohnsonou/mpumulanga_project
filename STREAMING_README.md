# Video Streaming System Setup

This guide explains how to set up and run the complete video streaming system with your React application.

## 🏗️ System Architecture

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   Python        │◄────────────────►│   React App     │
│   Stream        │    MJPEG Stream  │   (Browser)     │
│   Server        │                 │                 │
│   (Flask)       │                 │   2x2 Grid      │
│                 │                 │   Display       │
└─────────────────┘                 └─────────────────┘
         │                                     │
         ▼                                     ▼
┌─────────────────┐    ┌─────────────────┐
│   OpenCV        │    │   Video Files   │
│   YOLO Object   │    │   (demo_videos) │
│   Detection     │    │                 │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
# Start both servers automatically
python start_system.py
```

This will:
- Start the Flask video streaming server on `http://localhost:5000`
- Start the React development server on `http://localhost:5173`
- Open your browser to view the application

### Option 2: Manual Startup

**Terminal 1 - Start Video Stream Server:**
```bash
python stream_server.py
```
Server will run on: `http://localhost:5000`

**Terminal 2 - Start React App:**
```bash
cd react_app
npm run dev
```
React app will run on: `http://localhost:5173`

**Open Browser:**
Navigate to `http://localhost:5173` to view your 4-camera grid display.

## 📁 File Structure

```
mpumulanga_project/
├── stream_server.py          # Flask video streaming server
├── start_system.py           # Automated startup script
├── main.py                   # Original video processing (reference)
├── react_app/                # React application
│   ├── configs/              # Stream configuration files
│   └── src/                  # React components
└── demo_videos/              # Your video files
```

## ⚙️ Configuration

### Stream Configuration

Edit the JSON files in `react_app/configs/` to configure your streams:

```json
{
  "id": 1,
  "name": "Camera 1",
  "url": "http://localhost:5000/video_feed",
  "enabled": true
}
```

### Video Processing

The `stream_server.py` includes all your original video processing:
- YOLO object detection
- Vehicle tracking
- Region-based filtering
- Speed monitoring

## 🌐 Access Points

- **React App**: `http://localhost:5173` - Main 4-camera interface
- **Stream Server**: `http://localhost:5000` - Direct stream access
- **Video Feed**: `http://localhost:5000/video_feed` - MJPEG stream
- **Current Frame**: `http://localhost:5000/current_frame.jpg` - Single frame

## 🔧 Customization

### Adding Multiple Video Sources

To add different video files or camera sources:

1. **Multiple Video Files**: Modify `stream_server.py` to handle multiple video sources
2. **Live Cameras**: Replace `cv2.VideoCapture(PATH_TO_VIDEO)` with camera indices or RTSP URLs
3. **Different Processing**: Customize the frame processing logic in `generate_frames()`

### Changing Video Resolution

Edit these variables in `stream_server.py`:
```python
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
```

### Adjusting Frame Rate

Modify the sleep interval in `generate_frames()`:
```python
time.sleep(0.033)  # ~30 FPS
time.sleep(0.066)  # ~15 FPS (reduce CPU usage)
```

## 🛠️ Troubleshooting

### Stream Not Loading
- Ensure Flask server is running on port 5000
- Check that video files exist in `demo_videos/`
- Verify region_points.json exists or has valid coordinates

### React App Issues
- Run `npm install` in the `react_app/` directory
- Check browser console for JavaScript errors
- Ensure Vite dev server is running

### Performance Issues
- Reduce frame rate by increasing sleep time
- Lower video resolution (IMAGE_WIDTH/HEIGHT)
- Use smaller YOLO model (yolov8n.pt vs yolov8x.pt)

## 📝 Development Notes

- The React app uses MJPEG streaming for real-time video display
- Video processing runs on the Python server, not in the browser
- All object detection and tracking happens server-side
- The React app only handles display and user interface

## 🔒 Security Considerations

- Currently configured for localhost development
- For production deployment, consider:
  - HTTPS encryption
  - Authentication for stream access
  - Network security for camera connections
  - Firewall configuration for server ports

## 📚 Next Steps

1. **Multiple Camera Support**: Extend server to handle multiple video sources
2. **WebRTC Integration**: For lower latency streaming
3. **Recording Features**: Add video recording capabilities
4. **Alert System**: Implement motion detection alerts
5. **Mobile Optimization**: Responsive design improvements

---

🎉 **Your video streaming system is now ready!** The React app will display your processed video streams in a clean 4-camera grid layout.
