import Constants
import queue
import time
import mediapipe as mp
import cv2
import numpy as np
from PyQt6.QtCore import pyqtSignal as Signal, QThread


class VideoThread(QThread):
    """Thread for video capture and landmark processing."""
    frame_ready = Signal(np.ndarray)
    fps_updated = Signal(float)
    landmarks_ready = Signal(list)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.recording = False
        self.show_landmarks = True  # Toggle landmark visibility
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.frame_queue = queue.Queue(maxsize=Constants.BUFFER_SIZE)
        self.csv_queue = queue.Queue(maxsize=Constants.CSV_BUFFER_SIZE)
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=2, circle_radius=1)
        self.model_complexity = 0  # Default model complexity

    def set_model_complexity(self, complexity):
        """Set the model complexity level."""
        self.model_complexity = complexity

    def run(self):
        """Main capture and processing loop."""
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.running = False
            self.frame_ready.emit(np.zeros((Constants.TEXTURE_HEIGHT, Constants.TEXTURE_WIDTH, 3), dtype=np.uint8))
            self.fps_updated.emit(0.0)
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, Constants.TEXTURE_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Constants.TEXTURE_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, Constants.CAPTURE_FPS)

        start_time = time.time()
        frames_processed = 0

        with self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=self.model_complexity,  # Use the selected model complexity
            enable_segmentation=False
        ) as holistic:
            self.running = True
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break

                # Process frame with MediaPipe
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)

                # Draw landmarks if enabled
                display_frame = frame.copy()
                if self.show_landmarks:
                    self.draw_landmarks(display_frame, results)

                # Process landmarks if recording
                if self.recording and (results.pose_landmarks or results.left_hand_landmarks or results.right_hand_landmarks):
                    landmarks = self.process_landmarks(results, time.time())
                    self.landmarks_ready.emit(landmarks)

                # Calculate FPS
                frames_processed += 1
                elapsed_time = time.time() - start_time
                fps = frames_processed / elapsed_time

                # Emit signals
                self.frame_ready.emit(display_frame)
                self.fps_updated.emit(fps)

                # Save frame if needed
                try:
                    self.frame_queue.put(display_frame, block=False)
                except queue.Full:
                    continue

        cap.release()

    def draw_landmarks(self, image, results):
        """Draw detected landmarks on the image."""
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                self.mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=self.drawing_spec
            )
        if results.left_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                results.left_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=self.drawing_spec
            )
        if results.right_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                results.right_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=self.drawing_spec
            )

    def process_landmarks(self, results, timestamp):
        """Process and format landmark data."""
        landmarks = [timestamp]  # Include only timestamp

        # Process pose landmarks
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
        else:
            landmarks.extend([0] * (33 * 4))

        # Process hand landmarks
        for hand_landmarks in [results.left_hand_landmarks, results.right_hand_landmarks]:
            if hand_landmarks:
                for landmark in hand_landmarks.landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])
            else:
                landmarks.extend([0] * (21 * 3))

        return landmarks

    def stop(self):
        """Stop the video thread."""
        self.running = False
        self.wait()
