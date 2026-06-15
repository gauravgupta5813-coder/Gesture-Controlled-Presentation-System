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
        self.smooth_alpha = 0.25        
        self.jitter_threshold = 4
        self.non_draw_frames = 0
        self.release_after_frames = 3
        self.release_gestures = {"THUMB_UP", "OPEN_PALM", "FIST"}
         
    def update_canvas(self, frame, landmarks, gesture):
        
        if not landmarks or len(landmarks) < 21:
            # Safe Release: Lift the virtual pen up if the hand leaves the camera frame
            if self.is_pen_down:
                pyautogui.mouseUp()
                self.is_pen_down = False
            self.prev_x, self.prev_y = None, None
            return

        index_tip = landmarks[8]
        target_x = int(index_tip.x * self.screen_w)
        target_y = int(index_tip.y * self.screen_h)

        # --- Exponential Moving Average (EMA) स्मूथिंग फ़िल्टर ---
        if self.prev_x is None or self.prev_y is None:
            screen_x, screen_y = target_x, target_y
        else:
            # पिछले पिक्सेल और नए पिक्सेल को आपस में मिलाकर झटके सोखें
            screen_x = int(self.prev_x + self.smooth_alpha * (target_x - self.prev_x))
            screen_y = int(self.prev_y + self.smooth_alpha * (target_y - self.prev_y))
            
        screen_x = max(0, min(screen_x, self.screen_w - 1))
        screen_y = max(0, min(screen_y, self.screen_h - 1))
        
        # --- STATE MACHINE & HOTKEY INJECTION LAYER ---

        if gesture == "INDEX_UP":
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

            # only move when vibration in hand is more
            if self.prev_x is None or abs(screen_x - self.prev_x) > self.jitter_threshold or abs(screen_y - self.prev_y) > self.jitter_threshold:
                pyautogui.moveTo(screen_x, screen_y)
                self.prev_x, self.prev_y = screen_x, screen_y

        elif gesture == "INDEX_MIDDLE":
            self.non_draw_frames = 0
            if self.last_activated_mode != "DRAW":
                print("⚡ Action: Activating PowerPoint Drawing Pen (Ctrl + P)")
                pyautogui.hotkey('ctrl', 'p')
                self.last_activated_mode = "DRAW"

            if not self.is_pen_down:
                pyautogui.moveTo(screen_x, screen_y)
                pyautogui.mouseDown(button='left')
                self.is_pen_down = True
                self.prev_x, self.prev_y = screen_x, screen_y
            else:
                if abs(screen_x - self.prev_x) > self.jitter_threshold or abs(screen_y - self.prev_y) > self.jitter_threshold:
                    pyautogui.moveTo(screen_x, screen_y)
                    self.prev_x, self.prev_y = screen_x, screen_y

        else:
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

