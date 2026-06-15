import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker :
    def __init__(self, model_path='hand_landmarker.task'):
        self.model_path = model_path
        self.latest_result = None
        self.detector = None
        self._initialize_detector()

    def _callback(self, result, output_image: mp.Image, timestamp_ms: int):
        self.latest_result = result
        
    def _initialize_detector(self):
        
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM, 
            result_callback=self._callback,              
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
    def process_frame(self, frame_bgr):
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        timestamp_ms = int(time.time() * 1000)
        
        self.detector.detect_async(mp_image, timestamp_ms)

    def get_landmarks(self):
        
        if not self.latest_result or not self.latest_result.hand_landmarks:
            return None, None
            
        if not self.latest_result.handedness:
            return None, None

        try:
            landmarks = self.latest_result.hand_landmarks[0]
            
            handedness_category = self.latest_result.handedness[0][0]
            handedness_label = handedness_category.category_name
            
            return landmarks, handedness_label
            
        except (IndexError, AttributeError):
            return None, None

    def get_results(self):
        return self.latest_result

    def close(self):
        if self.detector:
            self.detector.close()