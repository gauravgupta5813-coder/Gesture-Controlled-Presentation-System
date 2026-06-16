# Gesture-Controlled Presentation System

A Python app that uses a webcam and hand tracking to control a PowerPoint presentation with gestures.

## Features

- Next and previous slide control with hand gestures
- Pointer mode and draw mode for PowerPoint slideshow
- Hand gesture detection using MediaPipe
- Real-time webcam preview with debug output

## Requirements

- Python 3.14 or compatible
- Webcam
- Microsoft PowerPoint
- Windows

## Install

Install the Python packages:

```bash
pip install -r requirements.txt
```

## Run

Start the app from the project folder:

```bash
python main.py
```

## Gestures

- `THUMB_UP` - Next slide
- `OPEN_PALM` - Previous slide
- `INDEX_UP` - Pointer mode
- `INDEX_MIDDLE` - Draw mode (index + middle finger)
- `FIST` - Clear markings

## Notes

- PowerPoint should be open in slideshow mode for the pointer and pen shortcuts to work correctly.
- The app uses the webcam feed and sends keyboard and mouse actions to the active PowerPoint window.
- If drawing still behaves like a dot, make sure PowerPoint is focused and the slideshow is active before testing.

## Project Files

- `main.py` - main application loop
- `hand_tracker.py` - MediaPipe hand tracking
- `gesture_detector.py` - gesture classification
- `slide_controller.py` - slide change actions
- `annotation.py` - pointer and drawing control
- `hand_landmarker.task` - MediaPipe model file
