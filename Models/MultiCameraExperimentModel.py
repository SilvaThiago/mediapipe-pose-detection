"""Model for Multi-Camera Experiment - Handles data and business logic."""

import os
import cv2
from datetime import datetime
from typing import List
import Constants
from Models.CameraModel import CameraModel


class MultiCameraExperimentModel:
    """Main model for multi-camera experiment."""
    
    def __init__(self):
        self.cameras: List[CameraModel] = []
        self.is_recording = False
        self.experiment_name = ""
        self.output_dir = os.getcwd()
        self.save_video = True
        self.show_landmarks = True
        
        # Initialize camera models
        for i in range(Constants.MAX_CAMERAS):
            self.cameras.append(CameraModel(i))
    
    def detect_available_cameras(self) -> List[int]:
        """Detect available camera indices."""
        available = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available if available else [0, 1, 2]
    
    def connect_camera(self, panel_index: int, camera_index: int) -> bool:
        """Connect a specific camera to a panel."""
        if 0 <= panel_index < len(self.cameras):
            # Disconnect previous camera
            self.cameras[panel_index].disconnect()
            
            # Create new camera model with selected index
            self.cameras[panel_index] = CameraModel(camera_index)
            return self.cameras[panel_index].connect()
        return False
    
    def has_any_camera_connected(self) -> bool:
        """Check if at least one camera is connected."""
        return any(cam.is_connected for cam in self.cameras)
    
    def are_all_cameras_connected(self) -> bool:
        """Check if all cameras are connected."""
        return all(cam.is_connected for cam in self.cameras)
    
    def get_connected_cameras_count(self) -> int:
        """Get count of connected cameras."""
        return sum(1 for cam in self.cameras if cam.is_connected)
    
    def start_experiment(self) -> bool:
        """Start recording experiment.
        
        Only starts recording for cameras that are connected.
        Returns True if at least one camera successfully started recording.
        """
        if not self.experiment_name:
            print("Error: No experiment name provided")
            return False
        
        if not self.has_any_camera_connected():
            print("Error: No cameras connected")
            return False
        
        try:
            # Create experiment directory
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            exp_dir = os.path.join(self.output_dir, f"{self.experiment_name}_{timestamp_str}")
            os.makedirs(exp_dir, exist_ok=True)
            
            print(f"Starting experiment in: {exp_dir}")
            
            # Start recording for each CONNECTED camera
            success_count = 0
            for i, camera in enumerate(self.cameras):
                if camera.is_connected:
                    if camera.start_recording(exp_dir, self.experiment_name, self.save_video):
                        print(f"Camera {i} recording started")
                        success_count += 1
                    else:
                        print(f"Warning: Failed to start recording for camera {i}")
                else:
                    print(f"Camera {i} not connected, skipping")
            
            # Consider success if at least one camera started recording
            if success_count > 0:
                self.is_recording = True
                print(f"Experiment started with {success_count} camera(s)")
                return True
            else:
                print("Error: No cameras successfully started recording")
                return False
            
        except Exception as e:
            print(f"Error starting experiment: {e}")
            return False
    
    def stop_experiment(self):
        """Stop recording experiment for all cameras."""
        print("Stopping experiment...")
        
        for i, camera in enumerate(self.cameras):
            if camera.is_connected:
                camera.stop_recording()
                print(f"Camera {i} recording stopped")
        
        self.is_recording = False
        print("Experiment stopped")
    
    def cleanup(self):
        """Cleanup all resources."""
        print("Cleaning up model...")
        
        self.stop_experiment()
        
        for i, camera in enumerate(self.cameras):
            camera.disconnect()
            print(f"Camera {i} disconnected")
        
        print("Model cleanup complete")