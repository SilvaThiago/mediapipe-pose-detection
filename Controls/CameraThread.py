"""Camera Thread - Handles individual camera capture in separate thread."""

import threading
import time
from Models.CameraModel import CameraModel


class CameraThread(threading.Thread):
    """Thread for handling individual camera capture and processing."""
    
    def __init__(self, camera: CameraModel, camera_index: int, controller):
        super().__init__(daemon=True)
        self.camera = camera
        self.camera_index = camera_index
        self.controller = controller
        self.stop_flag = False
        self.paused = False
        
    def run(self):
        """Main thread loop for camera capture."""
        while not self.stop_flag:
            try:
                # Skip if paused or camera not connected
                if self.paused or not self.camera.is_connected:
                    time.sleep(0.01)
                    continue
                
                # Read frame
                frame = self.camera.read_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # Get settings from controller
                show_landmarks = self.controller.get_show_landmarks()
                is_recording = self.controller.get_is_recording()
                save_video = self.controller.get_save_video()
                
                # Process frame with MediaPipe
                processed_frame, results = self.camera.process_frame(frame, show_landmarks)
                
                # Save data if recording
                if is_recording:
                    if results and results.pose_landmarks:
                        self.camera.save_landmarks(results.pose_landmarks)
                    
                    if save_video:
                        self.camera.save_frame(frame)
                
                # Update display (needs to be done in main thread via controller)
                self.controller.update_camera_display(self.camera_index, processed_frame, self.camera.fps)
                
                # Small delay to prevent CPU overload
                time.sleep(0.001)
            
            except Exception as e:
                print(f"Error in camera {self.camera_index} thread: {e}")
                time.sleep(0.1)
    
    def stop(self):
        """Stop the thread."""
        self.stop_flag = True
    
    def pause(self):
        """Pause capture."""
        self.paused = True
    
    def resume(self):
        """Resume capture."""
        self.paused = False