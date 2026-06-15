class GestureDetector:
    @staticmethod
    def get_raised_fingers(landmarks, handedness):
     
        if not landmarks or not handedness:
            return None

        fingers = []

        
        if handedness == 'Left':  # Physical RIGHT hand
            # If the thumb tip is to the RIGHT of its lower joint, it is extended/raised
            if landmarks[4].x > landmarks[3].x:
                fingers.append(1)
            else:
                fingers.append(0)
        else:  # Physical LEFT hand
            # If the thumb tip is to the LEFT of its lower joint, it is extended/raised
            if landmarks[4].x < landmarks[3].x:
                fingers.append(1)
            else:
                fingers.append(0)

        # --- 2. Four Fingers Check (Index, Middle, Ring, Pinky) ---
        # Tip IDs: 8 (Index), 12 (Middle), 16 (Ring), 20 (Pinky)
        # Pip Joint IDs: 6 (Index), 10 (Middle), 14 (Ring), 18 (Pinky)
        tip_ids = [8, 12, 16, 20]
        joint_ids = [6, 10, 14, 18]

        for tip, joint in zip(tip_ids, joint_ids):
            # In MediaPipe, the Y-axis increases downwards.
            if landmarks[tip].y < landmarks[joint].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    @classmethod
    def identify_gesture(cls, landmarks, handedness):
     
        finger_pattern = cls.get_raised_fingers(landmarks, handedness)
        if not finger_pattern:
            return "NO_HAND"
        
        if finger_pattern == [0, 0, 0, 0, 0]:
            return "FIST"             # Erase Drawing
            
        elif finger_pattern[1:] == [1, 0, 0, 0]:
            return "INDEX_UP"         # Pointer Mode
            
        elif finger_pattern[1:] == [1, 1, 0, 0]:
            return "INDEX_MIDDLE"     # Draw Mode
            
        elif finger_pattern == [1, 0, 0, 0, 0]:
            return "THUMB_UP"         # Next Slide
            
        elif finger_pattern == [1, 1, 1, 1, 1]:
            return "OPEN_PALM"        # Previous Slide

        return "UNKNOWN"
