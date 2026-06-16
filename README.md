# AI Gesture-Controlled Presentation System

A professional, modular computer vision application that allows presenters to control slideshow software (Microsoft PowerPoint, Google Slides, etc.) using real-time hand gestures captured via a standard webcam. The system runs asynchronous AI models to track hand joints and seamlessly injects operating system hotkeys and hardware mouse clicks.

---

## 🚀 Key Features
* **Zero Lag Asynchronous Pipeline**: Offloads MediaPipe AI math to a background worker thread, ensuring smooth 30+ FPS webcam rendering.
* **Dynamic Handedness Detection**: Automatically reads whether a left or right hand is active and dynamically adjusts finger tracking logic.
* **Hardware-Level Click Locking**: Utilizes native Windows API kernels (`win32api`) to eliminate pointer jitter and guarantee stable, continuous slide annotations without breaking strokes.
* **Auto-Mode Switcher**: Automatically handles switching between PowerPoint's native laser, pen, and arrow tools without manual keyboard interaction.

---

## 📊 Gesture Roadmap Specification

The application interprets a 5-digit binary array `[Thumb, Index, Middle, Ring, Pinky]` (where `1` = Raised, `0` = Folded) to execute structural commands directly on active desktop presentations:

| Hand Gesture Poses | Binary Array Pattern | System Operational Mode | Simulated Presentation Action |
| :--- | :---: | :--- | :--- |
| ✊ **Closed Fist** | `[0, 0, 0, 0, 0]` | **Erase Drawings** | Taps **`E`** (Wipes all digital ink off current slide) |
| ☝️ **Index Up** | `[0, 1, 0, 0, 0]` | **Laser Pointer Mode** | Fires **`Ctrl + L`** + Maps mouse to index tip coordinates |
| ✌️ **Index + Middle** | `[0, 1, 1, 0, 0]` | **Slide Ink Drawing** | Fires **`Ctrl + P`** + Locks **`Left-Click Down`** to write notes |
| 👍 **Thumb Up** | `[1, 0, 0, 0, 0]` | **Next Slide Transition** | Restores cursor (**`Ctrl + A`**) + Presses **`Right Arrow Key`** |
| 🖐️ **Open Palm** | `[1, 1, 1, 1, 1]` | **Previous Slide Transition** | Restores cursor (**`Ctrl + A`**) + Presses **`Left Arrow Key`** |

---

## 📁 System Project Architecture

The codebase follows a strictly modular Object-Oriented design, distributing layout components cleanly across specific single-responsibility domains:

```text
GesturePresentation/
│
├── main.py                # Central orchestrator driving OpenCV feeds and modular links
├── hand_tracker.py        # Asynchronously initializes MediaPipe Tasks and extracts coordinates
├── gesture_detector.py    # Pure logic module evaluating landmarks into semantic tokens
├── slide_controller.py    # Manages directional transitions and cooldown frame timers
├── annotation.py          # Intercepts gesture text tokens to inject system win32api hooks
├── hand_landmarker.task   # Google's offline production structural AI tracking model weights
└── requirements.txt       # Environment setup locking package dependency versions
```

---

## 🔧 Installation & Setup Guide

### 1. Download tracking model weights
Go to Google's MediaPipe official Edge Guide documentation, download the **`hand_landmarker.task`** package, and drop the bundle file directly inside your root `GesturePresentation/` project directory folder.

### 2. Environment Setup (Run as Administrator)
Open your terminal application with Elevated Administrative Privileges and run the following command to spin up all required architecture libraries:
```bash
pip install -r requirements.txt
```

---

## 🎯 How to Run & Perform Live Testing

1. Run the system orchestrator using your administrative terminal command window:
   ```bash
   python main.py
   ```
2. Minimize the terminal log while keeping your live webcam feed window visible on screen.
3. Open your presentation file deck inside **Microsoft PowerPoint**.
4. Press **`F5`** on your keyboard to drop PowerPoint into full-screen Slideshow mode view.
5. ⚠️ **CRUCIAL STEP**: Use your physical mouse to **click once directly onto the presentation slide screen layout**. This targets window focus, directing automated keys straight to your presentation.
6. A top-most webcam preview appears in the corner so you can keep your camera feed visible while the slideshow stays active. Press **`w`** during runtime to hide or show this webcam preview.
7. Step back 2–3 feet from the lens and present using your hand gestures!

---

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
=======
## 🛠️ Presentation Troubleshooting Checklist
* **Mouse moves, but ink is not drawing on screen:** Ensure you completed step 5 above. If your slideshow window isn't active, Windows drops the background click signals into thin air.
* **Slide skips 2 or 3 pages forward at once:** Your hand pose is triggering over multiple frames. Open `slide_controller.py` and change `cooldown_frames=25` to a larger buffer boundary metric like `35`.
