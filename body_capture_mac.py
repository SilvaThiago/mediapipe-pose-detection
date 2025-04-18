import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QComboBox, QCheckBox, QStatusBar, QFileDialog, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot, QThread
from PyQt6.QtGui import QImage, QPixmap
import mediapipe as mp
import csv
import time
import os
import queue
import tensorflow as tf
from datetime import datetime

# Optimize TensorFlow for M1
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'  # Enable oneDNN optimizations
os.environ['TF_METAL_ENABLED'] = '1'      # Enable Metal GPU acceleration

# Verify TensorFlow and GPU support
print(f"TensorFlow version: {tf.__version__}")
print("GPU available:", tf.config.list_physical_devices('GPU'))

# Constants
CAPTURE_FPS = 60  # Camera capture rate
DEFAULT_VIDEO_FPS = 25  # Default video recording FPS
TEXTURE_WIDTH = 1280
TEXTURE_HEIGHT = 720
VIDEO_CODEC = 'mp4v'
VIDEO_FORMAT = '.mp4'
BUFFER_SIZE = 30  # Frame buffer size
CSV_BUFFER_SIZE = 100  # CSV data buffer size


def get_available_cameras():
    """Get list of available camera devices."""
    camera_list = []
    for i in range(3):  # Check up to 3 cameras
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_list.append(f"Camera {i}")
            cap.release()
    return camera_list


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
        self.frame_queue = queue.Queue(maxsize=BUFFER_SIZE)
        self.csv_queue = queue.Queue(maxsize=CSV_BUFFER_SIZE)
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
            self.frame_ready.emit(np.zeros((TEXTURE_HEIGHT, TEXTURE_WIDTH, 3), dtype=np.uint8))
            self.fps_updated.emit(0.0)
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, TEXTURE_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TEXTURE_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAPTURE_FPS)

        start_time = time.time()
        frames_processed = 0

        with self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=self.model_complexity,  # Use the selected model complexity
            enable_segmentation=False,
            enable_tracking=False
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

class MotionCaptureWindow(QMainWindow):
    """Main application window for motion capture."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motion Capture System")
        self.first_timestamp = None

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.setSpacing(1)

        # Video feed group
        video_group = QGroupBox("Video Feed")
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(1, 1, 1, 1)
        video_layout.setSpacing(0)
        self.video_label = QLabel()
        self.video_label.setFixedSize(TEXTURE_WIDTH, TEXTURE_HEIGHT)
        self.video_label.setStyleSheet("QLabel { background-color: black; }")
        video_layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
        video_group.setLayout(video_layout)
        main_layout.addWidget(video_group)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(2)

        # File group
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(2, 2, 2, 2)
        file_layout.setSpacing(1)
        self.filename_label = QLabel("No file selected")
        self.select_file_btn = QPushButton("Change File")
        self.select_file_btn.setFixedHeight(20)
        file_layout.addWidget(self.filename_label)
        file_layout.addWidget(self.select_file_btn)
        file_group.setLayout(file_layout)

        # Camera group
        camera_group = QGroupBox("Camera")
        camera_layout = QVBoxLayout()
        camera_layout.setContentsMargins(2, 2, 2, 2)
        camera_layout.setSpacing(1)
        self.camera_combo = QComboBox()
        self.camera_combo.setFixedHeight(20)
        self.camera_combo.addItems(get_available_cameras())
        self.refresh_cameras_btn = QPushButton("Refresh Cameras")
        self.refresh_cameras_btn.setFixedHeight(20)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.addWidget(self.refresh_cameras_btn)
        camera_group.setLayout(camera_layout)

        # Capture group
        capture_group = QGroupBox("Capture Controls")
        capture_layout = QVBoxLayout()
        capture_layout.setContentsMargins(2, 2, 2, 2)
        capture_layout.setSpacing(1)

        # Model Complexity control
        model_complexity_layout = QHBoxLayout()
        model_complexity_layout.setSpacing(2)
        model_complexity_label = QLabel("Model Complexity:")
        model_complexity_label.setFixedHeight(20)
        self.model_complexity_combo = QComboBox()
        self.model_complexity_combo.setFixedHeight(20)
        self.model_complexity_combo.addItems(["Low (0)", "Medium (1)", "High (2)"])
        self.model_complexity_combo.setCurrentIndex(0)  # Default to Low
        model_complexity_layout.addWidget(model_complexity_label)
        model_complexity_layout.addWidget(self.model_complexity_combo)
        capture_layout.addLayout(model_complexity_layout)

        # FPS control
        fps_layout = QHBoxLayout()
        fps_layout.setSpacing(2)
        fps_label = QLabel("Video FPS:")
        fps_label.setFixedHeight(20)
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setFixedHeight(20)
        self.fps_spinbox.setRange(1, 60)
        self.fps_spinbox.setValue(DEFAULT_VIDEO_FPS)
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(self.fps_spinbox)
        capture_layout.addLayout(fps_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(2)
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.save_video_cb = QCheckBox("Save Video")
        self.show_landmarks_cb = QCheckBox("Show Landmarks")
        self.show_landmarks_cb.setChecked(True)

        for btn in [self.start_btn, self.stop_btn]:
            btn.setFixedHeight(20)

        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.save_video_cb)
        buttons_layout.addWidget(self.show_landmarks_cb)
        capture_layout.addLayout(buttons_layout)

        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedHeight(20)
        capture_layout.addWidget(self.close_btn)
        capture_group.setLayout(capture_layout)

        # Add groups to control panel
        control_layout.addWidget(file_group)
        control_layout.addWidget(camera_group)
        control_layout.addWidget(capture_group)
        main_layout.addWidget(control_panel)

        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.setFixedHeight(20)
        self.setStatusBar(self.statusBar)
        self.fps_label = QLabel("FPS: 0.0")
        self.statusBar.addPermanentWidget(self.fps_label)

        # Initialize variables
        self.filename = None
        self.csv_file = None
        self.csv_writer = None
        self.video_writer = None

        # Create video thread
        self.thread = VideoThread()
        self.thread.frame_ready.connect(self.update_frame)
        self.thread.fps_updated.connect(self.update_fps)
        self.thread.landmarks_ready.connect(self.save_landmarks)

        # Connect signals
        self.select_file_btn.clicked.connect(self.select_file)
        self.start_btn.clicked.connect(self.start_capture)
        self.stop_btn.clicked.connect(self.stop_capture)
        self.close_btn.clicked.connect(self.close)
        self.refresh_cameras_btn.clicked.connect(self.refresh_cameras)
        self.camera_combo.currentIndexChanged.connect(self.camera_changed)
        self.show_landmarks_cb.stateChanged.connect(self.toggle_landmarks)
        self.model_complexity_combo.currentIndexChanged.connect(self.update_model_complexity)

        # Initial UI state
        self.stop_btn.setEnabled(False)
        self.generate_filename()

        # Set window size and show
        self.resize(TEXTURE_WIDTH + 20, TEXTURE_HEIGHT + 70)
        self.show()

    def update_model_complexity(self, index):
        """Update the model complexity based on the selected value."""
        self.thread.set_model_complexity(index)

    def refresh_cameras(self):
        """Refresh the list of available cameras."""
        current_camera = self.camera_combo.currentIndex()
        self.camera_combo.clear()
        self.camera_combo.addItems(get_available_cameras())
        if current_camera < self.camera_combo.count():
            self.camera_combo.setCurrentIndex(current_camera)

    def camera_changed(self, index):
        """Handle camera selection change."""
        if self.thread.recording:
            self.stop_capture()
        self.thread.camera_index = index
        self.statusBar.showMessage(f"Selected camera {index}", 3000)

    def generate_filename(self):
        """Generate automatic filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        self.filename = os.path.join(documents_path, f"motion_capture_{timestamp}.csv")
        self.filename_label.setText(f"File: {self.filename}")
        self.start_btn.setEnabled(True)

    def select_file(self):
        """Select output file for data recording."""
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            os.path.join(documents_path, os.path.basename(self.filename)),  # Default to Documents
            "CSV Files (*.csv)"
        )
        if filename:
            self.filename = filename
            self.filename_label.setText(f"File: {os.path.basename(filename)}")
            self.start_btn.setEnabled(True)

    def start_capture(self):
        """Start motion capture."""
        if not self.filename:
            QMessageBox.warning(self, "Error", "Please select a file to save data.")
            return

        try:
            # Initialize CSV file
            self.csv_file = open(self.filename, mode='w', newline='')
            self.csv_writer = csv.writer(self.csv_file)

            # Write CSV headers
            headers = ['timestamp']
            for i in range(33):
                headers.extend([f'pose_{i}_x', f'pose_{i}_y', f'pose_{i}_z', f'pose_{i}_v'])
            for i in range(21):
                headers.extend([f'lhand_{i}_x', f'lhand_{i}_y', f'lhand_{i}_z'])
                headers.extend([f'rhand_{i}_x', f'rhand_{i}_y', f'rhand_{i}_z'])
            self.csv_writer.writerow(headers)

            # Initialize video writer if needed
            if self.save_video_cb.isChecked():
                video_path = self.filename.replace('.csv', VIDEO_FORMAT)
                fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
                self.video_writer = cv2.VideoWriter(
                    video_path,
                    fourcc,
                    float(self.fps_spinbox.value()),
                    (TEXTURE_WIDTH, TEXTURE_HEIGHT)
                )
            
            # Reset the first timestamp
            self.first_timestamp = None

            # Start capture
            self.thread.recording = True
            self.thread.start()

            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.select_file_btn.setEnabled(False)
            self.save_video_cb.setEnabled(False)
            self.camera_combo.setEnabled(False)
            self.refresh_cameras_btn.setEnabled(False)
            self.fps_spinbox.setEnabled(False)
            self.statusBar.showMessage("Recording...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start capture: {str(e)}")

    def stop_capture(self):
        """Stop motion capture."""
        self.thread.recording = False
        self.thread.stop()

        # Close files
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_file_btn.setEnabled(True)
        self.save_video_cb.setEnabled(True)
        self.camera_combo.setEnabled(True)
        self.refresh_cameras_btn.setEnabled(True)
        self.fps_spinbox.setEnabled(True)
        self.statusBar.showMessage("Capture finished", 3000)
        self.generate_filename()

    @Slot(np.ndarray)
    def update_frame(self, frame):
        """Update the video display."""
        if self.video_writer:
            self.video_writer.write(frame)

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    @Slot(float)
    def update_fps(self, fps):
        """Update the FPS display."""
        self.fps_label.setText(f"FPS: {fps:.1f}")

    @Slot(list)
    def save_landmarks(self, landmarks):
        """Save landmarks to CSV file."""
        if self.csv_writer:
            if self.first_timestamp is None:
                # Capture the first timestamp
                self.first_timestamp = landmarks[0]
                # Set the first timestamp to zero
                landmarks[0] = 0.0
            else:
                # Calculate the relative timestamp
                landmarks[0] = landmarks[0] - self.first_timestamp

            self.csv_writer.writerow(landmarks)

    def toggle_landmarks(self, state):
        """Toggle landmark visibility."""
        self.thread.show_landmarks = state == Qt.CheckState.Checked.value

    def closeEvent(self, event):
        """Handle window close event."""
        self.stop_capture()
        event.accept()


def main():
    """Main function to start the application."""
    # Configure high DPI settings
    if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    if hasattr(app, 'setDesktopFileName'):
        app.setDesktopFileName("motion_capture")

    # Set fusion style for better look
    app.setStyle('Fusion')

    window = MotionCaptureWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()