# Multi-Stream Video Monitor

A React-based application for displaying multiple real-time video streams in a clean, organized interface.

## Features

- **4-Stream Grid Layout**: Displays up to 4 video streams in a responsive 2x2 grid
- **RTSP Stream Support**: Configurable RTSP streams for IP cameras
- **Error Handling**: Shows appropriate messages for disabled or inaccessible streams
- **Responsive Design**: Adapts to different screen sizes
- **Real-time Status**: Visual indicators for stream status

## Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Streams**:
   Edit the configuration files in the `configs/` directory:
   - `rtsp-credential-1.json` - Camera 1 configuration
   - `rtsp-credential-2.json` - Camera 2 configuration
   - `rtsp-credential-3.json` - Camera 3 configuration
   - `rtsp-credential-4.json` - Camera 4 configuration

   Each config file should contain:
   ```json
   {
     "id": 1,
     "name": "Camera 1",
     "url": "rtsp://admin:password@192.168.1.101:554/stream1",
     "enabled": true
   }
   ```

## Usage

1. **Development Server**:
   ```bash
   npm run dev
   ```

2. **Build for Production**:
   ```bash
   npm run build
   ```

3. **Preview Production Build**:
   ```bash
   npm run preview
   ```

## Configuration Options

- **id**: Unique identifier for the stream
- **name**: Display name for the camera
- **url**: RTSP URL for the video stream
- **enabled**: Whether the stream should be active (true/false)

## Stream States

The application handles different stream states:

- **Loading**: Shows "Connecting to stream..." while attempting to connect
- **Active**: Displays the live video stream
- **Disabled**: Shows "Stream Disabled" for disabled cameras
- **Error**: Shows "Stream Detected - Connection Error" for inaccessible streams
- **Not Configured**: Shows "Stream X - Not Configured" for missing config files

## Browser Compatibility

- Modern browsers with HTML5 video support
- RTSP streams require compatible video codecs (H.264 recommended)
- Some browsers may require HTTPS for camera access

## Troubleshooting

- Ensure RTSP URLs are correct and accessible
- Check network connectivity to cameras
- Verify camera credentials in configuration files
- Some browsers may block mixed content (HTTP vs HTTPS)
