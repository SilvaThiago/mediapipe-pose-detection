"""Controller for Multi-Camera Experiment - Handles logic between Model and View."""

import threading
from typing import List, Optional
from Models.MultiCameraExperimentModel import MultiCameraExperimentModel
from Views.MultiCameraExperimentView import MultiCameraExperimentView
from Controls.CameraThread import CameraThread


class MultiCameraExperimentController:
    """Controller for multi-camera experiment application."""
    
    def __init__(self, view: MultiCameraExperimentView, model: MultiCameraExperimentModel):
        self.view = view
        self.model = model
        
        # Camera threads (one per camera)
        self.camera_threads: List[Optional[CameraThread]] = [None, None, None]
        self.preview_started = False
        
        # Thread lock for safe access to shared variables
        self.lock = threading.Lock()
        
        # Setup view callbacks
        self.view.on_directory_select = self.handle_directory_select
        self.view.on_camera_connect = self.handle_camera_connect
        self.view.on_init_videos = self.handle_init_videos
        self.view.on_start_recording = self.handle_start_recording
        self.view.on_stop_recording = self.handle_stop_recording
        
        # Initialize
        self.initialize()
    
    def initialize(self):
        """Initialize controller."""
        # Detect and populate available cameras
        available_cameras = self.model.detect_available_cameras()
        self.view.set_available_cameras(available_cameras)
        
        # Set initial output directory
        self.view.output_dir_var.set(self.model.output_dir)
        
        self.view.update_status("Waiting for configuration", "orange")
    
    def handle_directory_select(self):
        """Handle directory selection."""
        directory = self.view.select_directory()
        if directory:
            self.model.output_dir = directory
    
    def handle_camera_connect(self, panel_index: int, camera_index: int):
        """Handle camera connection."""
        try:
            success = self.model.connect_camera(panel_index, camera_index)
            
            if success:
                # Update visual status
                self.view.set_camera_connected(panel_index, True)
                
                self.view.show_info(
                    "Success",
                    f"Camera {camera_index} connected to Panel {panel_index + 1}"
                )
                
                # Enable Init Videos button if at least one camera is connected
                if self.model.has_any_camera_connected():
                    self.view.enable_init_videos_button()
                    self.view.update_status("Click 'INIT VIDEOS' to start preview", "blue")
            else:
                # Update visual status
                self.view.set_camera_connected(panel_index, False)
                self.view.show_error("Error", "Could not connect to camera")
        
        except Exception as e:
            self.view.show_error("Error", f"Error connecting camera: {str(e)}")
    
    def handle_init_videos(self):
        """Handle Init Videos button click."""
        # Check if at least one camera is connected
        if not self.model.has_any_camera_connected():
            self.view.show_warning("Warning", "Connect at least one camera first!")
            return
        
        # Start preview
        if not self.preview_started:
            self.start_preview()
            self.view.disable_init_videos_button()
            
            connected_count = sum(1 for cam in self.model.cameras if cam.is_connected)
            self.view.update_status(f"Preview started ({connected_count} camera(s))", "green")
            self.view.show_info(
                "Success", 
                f"Preview started with {connected_count} camera(s) connected!"
            )
    
    def start_preview(self):
        """Start camera preview with separate threads for each camera."""
        print("Starting camera preview with dedicated threads...")
        
        for i, camera in enumerate(self.model.cameras):
            if camera.is_connected:
                # Create and start thread for this camera
                thread = CameraThread(camera, i, self)
                self.camera_threads[i] = thread
                thread.start()
                print(f"Started thread for camera {i}")
        
        self.preview_started = True
    
    def stop_preview(self):
        """Stop all camera threads."""
        print("Stopping camera threads...")
        
        for i, thread in enumerate(self.camera_threads):
            if thread is not None:
                thread.stop()
                thread.join(timeout=2.0)
                self.camera_threads[i] = None
                print(f"Stopped thread for camera {i}")
        
        self.preview_started = False
    
    def update_camera_display(self, camera_index: int, frame, fps: float):
        """Update camera display (called from camera threads)."""
        # Schedule UI update in main thread
        self.view.root.after(1, lambda: self._update_display_main_thread(camera_index, frame, fps))
    
    def _update_display_main_thread(self, camera_index: int, frame, fps: float):
        """Update display in main thread (thread-safe)."""
        try:
            self.view.display_frame(camera_index, frame)
            self.view.update_fps(camera_index, fps)
        except Exception as e:
            print(f"Error updating display for camera {camera_index}: {e}")
    
    # Thread-safe getters for camera threads
    def get_show_landmarks(self) -> bool:
        """Get show landmarks setting (thread-safe)."""
        with self.lock:
            return self.view.show_landmarks_var.get()
    
    def get_is_recording(self) -> bool:
        """Get recording state (thread-safe)."""
        with self.lock:
            return self.model.is_recording
    
    def get_save_video(self) -> bool:
        """Get save video setting (thread-safe)."""
        with self.lock:
            return self.model.save_video
    
    def handle_start_recording(self):
        """Handle start recording button."""
        # Check if preview was started
        if not self.preview_started:
            self.view.show_warning("Warning", "Start camera preview first!")
            return
        
        # Validate experiment name
        experiment_name = self.view.experiment_name_var.get().strip()
        if not experiment_name:
            self.view.show_warning("Warning", "Enter experiment ID!")
            return
        
        # Check if at least one camera is connected
        if not self.model.has_any_camera_connected():
            self.view.show_warning("Warning", "Connect at least one camera before recording!")
            return
        
        try:
            # Update model settings
            with self.lock:
                self.model.experiment_name = experiment_name
                self.model.save_video = self.view.save_video_var.get()
                self.model.show_landmarks = self.view.show_landmarks_var.get()
            
            # Start experiment
            success = self.model.start_experiment()
            
            if success:
                # Count connected cameras
                connected_count = sum(1 for cam in self.model.cameras if cam.is_connected)
                
                # Update view
                self.view.set_recording_state(True)
                self.view.update_status(f"⏺ RECORDING ({connected_count} camera(s))", "red")
                
                exp_dir = self.model.output_dir + "/" + self.model.experiment_name
                
                # Build camera list message
                camera_list = []
                for i, cam in enumerate(self.model.cameras):
                    if cam.is_connected:
                        camera_list.append(f"  • Camera {i + 1}")
                
                cameras_str = "\n".join(camera_list)
                
                self.view.show_info(
                    "Success",
                    f"Recording started with {connected_count} camera(s)!\n\n"
                    f"Recording cameras:\n{cameras_str}\n\n"
                    f"Files saved to:\n{exp_dir}"
                )
            else:
                self.view.show_error("Error", "Failed to start recording")
        
        except Exception as e:
            self.view.show_error("Error", f"Error starting recording: {str(e)}")
    
    def handle_stop_recording(self):
        """Handle stop recording button."""
        try:
            with self.lock:
                self.model.stop_experiment()
            
            # Update view
            self.view.set_recording_state(False)
            
            connected_count = sum(1 for cam in self.model.cameras if cam.is_connected)
            self.view.update_status(f"Preview active ({connected_count} camera(s)) - Ready for new recording", "green")
            
            self.view.show_info("Success", "Recording finished successfully!")
        
        except Exception as e:
            self.view.show_error("Error", f"Error stopping recording: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources."""
        print("Cleaning up controller...")
        
        # Stop all camera threads
        self.stop_preview()
        
        # Cleanup model
        self.model.cleanup()
        
        print("Controller cleanup complete")