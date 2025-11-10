"""View for Multi-Camera Experiment - Handles UI."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os
import Constants


class MultiCameraExperimentView:
    """Main view for multi-camera experiment application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Camera Motion Capture System")
        self.root.geometry(f"{Constants.WINDOW_WIDTH}x{Constants.WINDOW_HEIGHT}")
        
        # Callback references (to be set by controller)
        self.on_directory_select = None
        self.on_camera_connect = None
        self.on_init_videos = None
        self.on_start_recording = None
        self.on_stop_recording = None
        
        # UI Variables
        self.experiment_name_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        self.save_video_var = tk.BooleanVar(value=True)
        self.show_landmarks_var = tk.BooleanVar(value=True)
        
        # UI Components
        self.camera_combos = []
        self.canvas_labels = []
        self.fps_labels = []
        self.connection_status_labels = []
        self.experiment_entry = None
        self.init_videos_button = None
        self.start_button = None
        self.stop_button = None
        self.status_label = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Create the user interface."""
        
        # Configuration Frame
        self.create_config_frame()
        
        # Cameras Frame
        self.create_cameras_frame()
        
        # Control Frame
        self.create_control_frame()
    
    def create_config_frame(self):
        """Create configuration frame."""
        config_frame = ttk.LabelFrame(self.root, text="Experiment Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Experiment name
        ttk.Label(config_frame, text="Experiment ID:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.experiment_entry = ttk.Entry(config_frame, textvariable=self.experiment_name_var, width=30)
        self.experiment_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        # Output directory
        ttk.Label(config_frame, text="Output Directory:").grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Entry(config_frame, textvariable=self.output_dir_var, state='readonly', width=30).grid(
            row=0, column=3, sticky=tk.EW, padx=5
        )
        ttk.Button(config_frame, text="Browse", command=self._handle_directory_select).grid(
            row=0, column=4, padx=5
        )
        
        # Options
        ttk.Checkbutton(config_frame, text="Save Video", variable=self.save_video_var).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5
        )
        
        ttk.Checkbutton(config_frame, text="Show Landmarks", variable=self.show_landmarks_var).grid(
            row=1, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5
        )
        
        config_frame.columnconfigure(3, weight=1)
    
    def create_cameras_frame(self):
        """Create cameras frame."""
        cameras_frame = ttk.LabelFrame(self.root, text="Cameras", padding=10)
        cameras_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create camera panels
        for i in range(Constants.MAX_CAMERAS):
            self.create_camera_panel(cameras_frame, i)
        
        for i in range(Constants.MAX_CAMERAS):
            cameras_frame.columnconfigure(i, weight=1)
    
    def create_camera_panel(self, parent, camera_index):
        """Create a single camera panel."""
        frame = ttk.LabelFrame(parent, text=f"Camera {camera_index + 1}", padding=5)
        frame.grid(row=0, column=camera_index, sticky="nsew", padx=5, pady=5)
        
        # Connection status label
        status_label = ttk.Label(frame, text="● Disconnected", foreground="red")
        status_label.pack()
        self.connection_status_labels.append(status_label)
        
        # Video canvas
        canvas = tk.Canvas(frame, width=Constants.DISPLAY_WIDTH, height=Constants.DISPLAY_HEIGHT, bg="black")
        canvas.pack(padx=5, pady=5)
        self.canvas_labels.append(canvas)
        
        # FPS label
        fps_label = ttk.Label(frame, text="FPS: 0.0", foreground="blue")
        fps_label.pack()
        self.fps_labels.append(fps_label)
        
        # Camera selection
        ttk.Label(frame, text="Select camera:").pack()
        combo = ttk.Combobox(frame, state="readonly", width=20)
        combo.pack(padx=5, pady=5)
        self.camera_combos.append(combo)
        
        # Connect button
        ttk.Button(
            frame, text="✓ Connect",
            command=lambda idx=camera_index: self._handle_camera_connect(idx)
        ).pack(padx=5, pady=5)
    
    def create_control_frame(self):
        """Create control frame."""
        control_frame = ttk.LabelFrame(self.root, text="Control", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Init Videos button
        self.init_videos_button = ttk.Button(
            control_frame, text="🎥 INIT VIDEOS",
            command=self._handle_init_videos,
            width=20
        )
        self.init_videos_button.pack(side=tk.LEFT, padx=5)
        self.init_videos_button.config(state=tk.DISABLED)
        
        # Separator
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Recording buttons
        self.start_button = ttk.Button(
            control_frame, text="▶ START RECORDING",
            command=self._handle_start_recording,
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            control_frame, text="⏹ STOP RECORDING",
            command=self._handle_stop_recording,
            state=tk.DISABLED, width=20
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(
            control_frame, text="Status: Waiting for configuration",
            foreground="orange"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
    
    def set_available_cameras(self, camera_indices):
        """Set available cameras in combo boxes."""
        camera_names = [f"Camera {i}" for i in camera_indices]
        for combo in self.camera_combos:
            combo['values'] = camera_names
            if camera_names:
                combo.current(0)
    
    def set_camera_connected(self, camera_index: int, connected: bool):
        """Update camera connection status."""
        if 0 <= camera_index < len(self.connection_status_labels):
            if connected:
                self.connection_status_labels[camera_index].config(
                    text="● Connected",
                    foreground="green"
                )
            else:
                self.connection_status_labels[camera_index].config(
                    text="● Disconnected",
                    foreground="red"
                )
    
    def enable_init_videos_button(self):
        """Enable Init Videos button."""
        self.init_videos_button.config(state=tk.NORMAL)
    
    def disable_init_videos_button(self):
        """Disable Init Videos button."""
        self.init_videos_button.config(state=tk.DISABLED)
    
    def display_frame(self, camera_index, frame):
        """Display frame on canvas."""
        try:
            # Resize for display
            display_frame = cv2.resize(frame, (Constants.DISPLAY_WIDTH, Constants.DISPLAY_HEIGHT))
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # Display on canvas
            canvas = self.canvas_labels[camera_index]
            canvas.create_image(Constants.DISPLAY_WIDTH // 2, Constants.DISPLAY_HEIGHT // 2, image=photo)
            canvas.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Error displaying frame: {e}")
    
    def update_fps(self, camera_index, fps):
        """Update FPS label."""
        if 0 <= camera_index < len(self.fps_labels):
            self.fps_labels[camera_index].config(text=f"FPS: {fps:.1f}")
    
    def update_status(self, message, color="black"):
        """Update status message."""
        self.status_label.config(text=f"Status: {message}", foreground=color)
    
    def set_recording_state(self, is_recording):
        """Set UI state for recording."""
        if is_recording:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.experiment_entry.config(state=tk.DISABLED)
            self.init_videos_button.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.experiment_entry.config(state=tk.NORMAL)
    
    def show_error(self, title, message):
        """Show error message."""
        messagebox.showerror(title, message)
    
    def show_info(self, title, message):
        """Show info message."""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title, message):
        """Show warning message."""
        messagebox.showwarning(title, message)
    
    def select_directory(self):
        """Open directory selection dialog."""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir_var.set(directory)
            return directory
        return None
    
    # Event handlers (called by view, delegated to controller)
    def _handle_directory_select(self):
        if self.on_directory_select:
            self.on_directory_select()
    
    def _handle_camera_connect(self, camera_index):
        if self.on_camera_connect:
            combo = self.camera_combos[camera_index]
            camera_num = int(combo.get().split()[-1])
            self.on_camera_connect(camera_index, camera_num)
    
    def _handle_init_videos(self):
        """Handle Init Videos button click."""
        if self.on_init_videos:
            self.on_init_videos()
    
    def _handle_start_recording(self):
        if self.on_start_recording:
            self.on_start_recording()
    
    def _handle_stop_recording(self):
        if self.on_stop_recording:
            self.on_stop_recording()