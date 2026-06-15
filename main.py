import cv2
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from slide_controller import SlideController
from annotation import AnnotationManager

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker(model_path='hand_landmarker.task')
    controller = SlideController(cooldown_frames=25)
    annotator = AnnotationManager()
    
    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            print("Error: Can't receive frame.")
            continue
        
        frame = cv2.flip(frame, 1)
        
        tracker.process_frame(frame)
        
        landmarks, handedness = tracker.get_landmarks()
        
        gesture = "NO_HAND"
        
        if landmarks:
            wrist = landmarks[0]
            print(f"Detected {handedness} Hand | Wrist -> X: {wrist.x:.2f}, Y: {wrist.y:.2f}")
        
            raw_pattern = GestureDetector.get_raised_fingers(landmarks, handedness)
            print(f"DEBUG -> Raw Finger Pattern: {raw_pattern}")
            
            gesture = GestureDetector.identify_gesture(landmarks, handedness)
            print(f"Detected Action State -> {gesture}")
                
            action_executed = controller.trigger_action(gesture)
            if action_executed:
                print(f"⌨️ Keyboard Action Simulated: {action_executed}")
               
            cv2.putText(frame, f"Gesture: {gesture}", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        annotator.update_canvas(frame, landmarks, gesture)
                    
        cv2.imshow('Main Application View', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    tracker.close()
    
if __name__ == "__main__":
    main()