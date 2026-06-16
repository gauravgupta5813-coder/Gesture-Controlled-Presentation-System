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
    gesture_history = []
    gesture_buffer_length = 5
    show_webcam_preview = True

    cv2.namedWindow('Main Application View', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Webcam Preview', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Webcam Preview', 220, 200)
    cv2.setWindowProperty('Webcam Preview', cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow('Webcam Preview', 20, 20)

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

            raw_gesture = GestureDetector.identify_gesture(landmarks, handedness)
            gesture_history.append(raw_gesture)
            if len(gesture_history) > gesture_buffer_length:
                gesture_history.pop(0)
            gesture = max(set(gesture_history), key=gesture_history.count)

            print(f"DEBUG -> Buffered Gesture History: {gesture_history}")
            print(f"Detected Action State -> {gesture}")
                
            action_executed = controller.trigger_action(gesture)
            if action_executed:
                print(f"⌨️ Keyboard Action Simulated: {action_executed}")
               
            cv2.putText(frame, f"Gesture: {gesture}", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if not landmarks:
            gesture_history.clear()
        annotator.update_canvas(frame, landmarks, gesture)

        if show_webcam_preview:
            preview_size = 180
            h, w = frame.shape[:2]
            min_dim = min(h, w)
            start_x = (w - min_dim) // 2
            start_y = (h - min_dim) // 2
            square_frame = frame[start_y:start_y + min_dim, start_x:start_x + min_dim]

            # Draw landmarks overlay on the preview copy so the main frame is untouched
            preview_overlay = square_frame.copy()
            if landmarks:
                annotator.draw_landmarks(preview_overlay, landmarks, is_drawing=annotator.is_pen_down)

            preview = cv2.resize(preview_overlay, (preview_size, preview_size))
            cv2.imshow('Webcam Preview', preview)

        # Draw landmarks overlay on the main application view so the pen indicator
        # is visible on the presentation preview. Use a larger radius while drawing.
        if landmarks:
            annotator.draw_landmarks(frame, landmarks, is_drawing=annotator.is_pen_down, radius=10, thickness=3)

        cv2.imshow('Main Application View', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('w'):
            show_webcam_preview = not show_webcam_preview
            if not show_webcam_preview:
                cv2.destroyWindow('Webcam Preview')
            else:
                cv2.namedWindow('Webcam Preview', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Webcam Preview', 180, 180)
                cv2.setWindowProperty('Webcam Preview', cv2.WND_PROP_TOPMOST, 1)
                cv2.moveWindow('Webcam Preview', 20, 20)

    cap.release()
    cv2.destroyAllWindows()
    tracker.close()
    
if __name__ == "__main__":
    main()