import pyautogui

class SlideController:
    def __init__(self, cooldown_frames = 25):
        self.cooldown_frames = cooldown_frames
        self.current_cooldown = 0
        
    def trigger_action(self, gesture):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            return None

        if gesture == "THUMB_UP":
            pyautogui.press('right')
            self.current_cooldown = self.cooldown_frames
            return "NEXT SLIDE"
            
        elif gesture == "OPEN_PALM":
            pyautogui.press('left')
            self.current_cooldown = self.cooldown_frames
            return "PREV SLIDE"
            
        return None
        