"""Camera Model - Handles individual camera operations."""

import cv2
import mediapipe as mp
import csv
import os
import time
from datetime import datetime
from typing import Optional
import Constants


class CameraModel:
    """Model for a single camera.
    
    Note: This class is designed to be used by a single thread at a time.
    The CameraThread class ensures thread-safe access.
    """
    
    def __init__(self, camera_index: int):
        self.camera_index = camera_index
        self.capture: Optional[cv2.VideoCapture] = None
        self.pose_detector: Optional[mp.solutions.pose.Pose] = None
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.csv_file = None
        self.csv_writer = None
        self.frame_count = 0
        self.fps = 0.0
        self.last_fps_time = time.time()
        self.is_connected = False
        
    def connect(self) -> bool:
        """Connect to camera and initialize pose detector."""
        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, Constants.DEFAULT_FRAME_WIDTH)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, Constants.DEFAULT_FRAME_HEIGHT)
            self.capture.set(cv2.CAP_PROP_FPS, Constants.DEFAULT_FPS)
            
            # Enable buffering for better performance
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not self.capture.isOpened():
                return False
            
            # Initialize MediaPipe Pose
            mp_pose = mp.solutions.pose
            self.pose_detector = mp_pose.Pose(
                min_detection_confidence=Constants.MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=Constants.MIN_TRACKING_CONFIDENCE,
                model_complexity=Constants.MODEL_COMPLEXITY
            )
            
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"Error connecting camera {self.camera_index}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect camera and release resources."""
        if self.capture:
            self.capture.release()
            self.capture = None
        
        if self.pose_detector:
            self.pose_detector.close()
            self.pose_detector = None
        
        self.is_connected = False
    
    def read_frame(self):
        """Read frame from camera."""
        if self.capture and self.is_connected:
            ret, frame = self.capture.read()
            if ret:
                self.update_fps()
                return frame
        return None
    
    def process_frame(self, frame, draw_landmarks: bool = True):
        """Process frame with MediaPipe and return results."""
        if not self.pose_detector:
            return frame, None
        
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose_detector.process(frame_rgb)
        
        # Draw landmarks if enabled
        if draw_landmarks and results.pose_landmarks:
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            mp_pose = mp.solutions.pose
            
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
        
        return frame, results
    
    def update_fps(self):
        """Update FPS calculation."""
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_fps_time
        
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def start_recording(self, output_dir: str, experiment_name: str, save_video: bool = True):
        """Start recording video and CSV."""
        try:
            # Create CSV file
            csv_filename = os.path.join(output_dir, f"{experiment_name}_camera{self.camera_index + 1}.csv")
            self.csv_file = open(csv_filename, mode='w', newline='')
            self.csv_writer = csv.writer(self.csv_file, delimiter=Constants.CSV_DELIMITER)
            
            # Write CSV headers
            headers = ['timestamp']
            for i in range(Constants.POSE_LANDMARKS_COUNT):
                headers.extend([f'pose_{i}_x', f'pose_{i}_y', f'pose_{i}_z', f'pose_{i}_v'])
            self.csv_writer.writerow(headers)
            
            # Create video writer if needed
            if save_video:
                video_filename = os.path.join(output_dir, f"{experiment_name}_camera{self.camera_index + 1}{Constants.VIDEO_FORMAT}")
                fourcc = cv2.VideoWriter_fourcc(*Constants.VIDEO_CODEC)
                self.video_writer = cv2.VideoWriter(
                    video_filename,
                    fourcc,
                    Constants.DEFAULT_FPS,
                    (Constants.DEFAULT_FRAME_WIDTH, Constants.DEFAULT_FRAME_HEIGHT)
                )
            
            return True
            
        except Exception as e:
            print(f"Error starting recording for camera {self.camera_index}: {e}")
            return False
    
    def stop_recording(self):
        """Stop recording and close files."""
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
    
    def save_frame(self, frame):
        """Save frame to video file."""
        if self.video_writer:
            self.video_writer.write(frame)
    
    def save_landmarks(self, pose_landmarks):
        """Save landmarks to CSV file."""
        if not self.csv_writer or not pose_landmarks:
            return
        
        try:
            timestamp = datetime.now()
            row = [timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")]
            
            # Extract landmark coordinates
            for landmark in pose_landmarks.landmark:
                row.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
            
            self.csv_writer.writerow(row)
            
        except Exception as e:
            print(f"Error saving landmarks: {e}")