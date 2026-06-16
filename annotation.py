import cv2
import pyautogui

# Optimize PyAutoGUI settings for fast, real-time response
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

class AnnotationManager:
    def __init__(self):
        self.pointer_color = (0, 0, 255)  # Bright Red in BGR
        self.pointer_radius = 12          # Size of the laser center
        self.glow_radius = 24             # Size of the outer soft glow radius
        
        
        self.draw_color = (255, 0 ,0)  #BGR
        self.line_thickness = 5
        
        self.draw_points = []
        
        self.screen_w, self.screen_h = pyautogui.size()  # Dynamic screen resolution check
        self.is_pen_down = False                          # Mouse dragging status tracker
        self.last_activated_mode = "NONE"                 # Tracks active PowerPoint state

        self.prev_x, self.prev_y = None, None
        self.smooth_alpha = 0.22
        self.jitter_threshold = 2
        self.non_draw_frames = 0
        self.release_after_frames = 6
        self.release_gestures = {"THUMB_UP", "OPEN_PALM", "FIST"}
        self.gesture_history = []
        self.history_length = 5
        # How many pixels to spread the simulated cursor moves to thicken ink
        self.pen_spread = 2
        
        
         
    def update_canvas(self, frame, landmarks, gesture):

        if not landmarks or len(landmarks) < 21:
            # Safe Release: Lift the virtual pen up if the hand leaves the camera frame
            if self.is_pen_down:
                pyautogui.mouseUp()
                self.is_pen_down = False
            self.prev_x, self.prev_y = None, None
            return

        # Stable gesture smoothing
        self.gesture_history.append(gesture)
        if len(self.gesture_history) > self.history_length:
            self.gesture_history.pop(0)
        gesture = max(set(self.gesture_history), key=self.gesture_history.count)

        # We'll always use the index fingertip (id 8) as the drawing cursor
        draw_tip = landmarks[8]
        target_x = int(draw_tip.x * self.screen_w)
        target_y = int(draw_tip.y * self.screen_h)

        # --- Exponential Moving Average smoothing ---
        if self.prev_x is None or self.prev_y is None:
            screen_x, screen_y = target_x, target_y
        else:
            screen_x = int(self.prev_x + self.smooth_alpha * (target_x - self.prev_x))
            screen_y = int(self.prev_y + self.smooth_alpha * (target_y - self.prev_y))

        screen_x = max(0, min(screen_x, self.screen_w - 1))
        screen_y = max(0, min(screen_y, self.screen_h - 1))

        # Determine middle finger raised/folded state using landmarks (tip 12, pip 10)
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        middle_raised = middle_tip.y < middle_pip.y

        # --- STATE MACHINE & HOTKEY LAYER ---

        # POINTER mode (index up)
        if gesture == "INDEX_UP":
            # If drawing was active, handle graceful lift
            if self.is_pen_down:
                self.non_draw_frames += 1
                if gesture in self.release_gestures or self.non_draw_frames >= self.release_after_frames:
                    pyautogui.mouseUp()
                    self.is_pen_down = False
                    self.non_draw_frames = 0
                else:
                    if abs(screen_x - self.prev_x) > self.jitter_threshold or abs(screen_y - self.prev_y) > self.jitter_threshold:
                        pyautogui.moveTo(screen_x, screen_y)
                        self.prev_x, self.prev_y = screen_x, screen_y
                return

            self.non_draw_frames = 0
            if self.last_activated_mode != "POINTER":
                print("⚡ Action: Activating PowerPoint Laser Pointer (Ctrl + L)")
                pyautogui.hotkey('ctrl', 'l')
                self.last_activated_mode = "POINTER"

            if self.prev_x is None or abs(screen_x - self.prev_x) > self.jitter_threshold or abs(screen_y - self.prev_y) > self.jitter_threshold:
                pyautogui.moveTo(screen_x, screen_y)
                self.prev_x, self.prev_y = screen_x, screen_y

        # DRAW mode: entered when user shows index+middle gesture, but actual drawing occurs
        # only when the middle finger is folded (middle_raised == False). The index
        # fingertip is used as the drawing cursor.
        elif gesture == "INDEX_MIDDLE":
            self.non_draw_frames = 0
            if self.last_activated_mode != "DRAW":
                print("⚡ Action: Activating PowerPoint Drawing Pen (Ctrl + P)")
                pyautogui.hotkey('ctrl', 'p')
                self.last_activated_mode = "DRAW"

            # Always move cursor to index tip while in draw mode
            if self.prev_x is None or abs(screen_x - self.prev_x) > self.jitter_threshold or abs(screen_y - self.prev_y) > self.jitter_threshold:
                pyautogui.moveTo(screen_x, screen_y)
                self.prev_x, self.prev_y = screen_x, screen_y

                if not self.is_pen_down:
                 pyautogui.mouseDown(button='left')
                self.is_pen_down = True
            
                pyautogui.mouseDown(button='left')
                self.is_pen_down = True
                self.prev_x, self.prev_y = screen_x, screen_y

            # If middle finger is raised while drawing, lift the pen
            pass

            # When drawing, keep moving the cursor with index tip
            if self.is_pen_down:
                if abs(screen_x - self.prev_x) > self.jitter_threshold or abs(screen_y - self.prev_y) > self.jitter_threshold:
                    # Move to center first
                    pyautogui.moveTo(screen_x, screen_y)
                    # Simulate small offset moves while pen is down to thicken stroke
                    spread = max(1, int(self.pen_spread))
                    offsets = [(spread,0),(-spread,0),(0,spread),(0,-spread),(spread,spread),(-spread,-spread)]
                    for dx, dy in offsets:
                        try:
                            pyautogui.moveTo(screen_x + dx, screen_y + dy)
                        except Exception:
                            pass
                    # Return to center
                    pyautogui.moveTo(screen_x, screen_y)
                    self.prev_x, self.prev_y = screen_x, screen_y

        else:
            # Other gestures: handle pen lift and mode resets
            if self.is_pen_down:
                self.non_draw_frames += 1
                if gesture in self.release_gestures or self.non_draw_frames >= self.release_after_frames:
                    pyautogui.mouseUp()
                    self.is_pen_down = False
                    self.non_draw_frames = 0
                else:
                    if abs(screen_x - self.prev_x) > self.jitter_threshold or abs(screen_y - self.prev_y) > self.jitter_threshold:
                        pyautogui.moveTo(screen_x, screen_y)
                        self.prev_x, self.prev_y = screen_x, screen_y

            if (not self.is_pen_down) and self.last_activated_mode in ["POINTER", "DRAW"] and gesture in ["THUMB_UP", "OPEN_PALM", "UNKNOWN"]:
                print("⚡ Action: Restoring Standard Mouse Cursor (Ctrl + A)")
                pyautogui.hotkey('ctrl', 'a')
                self.last_activated_mode = "NORMAL"

            if gesture == "FIST":
                print("⚡ Action: Clearing All Slide Markings (E)")
                pyautogui.press('e')
                self.last_activated_mode = "ERASED"

            if not self.is_pen_down:
                self.prev_x, self.prev_y = None, None

    def draw_landmarks(self, frame, landmarks, color=(0,255,0), radius=4, thickness=2, is_drawing=False):
        """Draw hand landmarks and connections on `frame` using the normalized
        landmark coordinates in `landmarks` (expects objects with .x and .y).
        When `is_drawing` is True, the index fingertip is highlighted with a
        larger red dot so the presenter can see the active drawing point.
        """
        if not landmarks:
            return

        h, w = frame.shape[:2]

        # Define common hand connections (MediaPipe-style)
        connections = [
            (0,1),(1,2),(2,3),(3,4),
            (0,5),(5,6),(6,7),(7,8),
            (5,9),(9,10),(10,11),(11,12),
            (9,13),(13,14),(14,15),(15,16),
            (13,17),(17,18),(18,19),(19,20),
            (0,17)
        ]

        # Convert landmarks to pixel coords
        pts = []
        for lm in landmarks:
            px = int(lm.x * w)
            py = int(lm.y * h)
            pts.append((px, py))

        # Draw connections
        for a, b in connections:
            if a < len(pts) and b < len(pts):
                cv2.line(frame, pts[a], pts[b], color, thickness)

        # Draw keypoints; index fingertip (id 8) gets special handling
        for idx, (x, y) in enumerate(pts):
            if idx == 8:
                # larger indicator for index fingertip
                if is_drawing:
                    inner_r = max(radius, 14)
                    outer_r = max(int(radius * 2), 28)
                    cv2.circle(frame, (x, y), inner_r, (0, 0, 255), -1)
                    cv2.circle(frame, (x, y), outer_r, (0, 0, 180), 3)
                else:
                    small_r = max(radius, 8)
                    cv2.circle(frame, (x, y), small_r, (0, 200, 0), -1)
            else:
                cv2.circle(frame, (x, y), radius, (0, 200, 0), -1)

