from VideoThread import VideoThread
from ExperimentWindow import ExperimentWindow

import Constants
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QComboBox, QCheckBox, QStatusBar, QFileDialog, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot as Slot
from PyQt6.QtGui import QImage, QPixmap
import csv
import os
from datetime import datetime

class MotionCaptureWindow(QMainWindow):
    """Main application window for motion capture."""

    def __init__(self, experiment):
        super().__init__()

        self.experiment = experiment
        self.setWindowTitle(self.experiment.chosenCamera or "Motion Capture")
        self.first_timestamp = None

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.setSpacing(1)

        if self.experiment.showPreview:
            # Video feed group
            video_group = QGroupBox("Video Feed")
            video_layout = QVBoxLayout()
            video_layout.setContentsMargins(1, 1, 1, 1)
            video_layout.setSpacing(0)
            self.video_label = QLabel()
            self.video_label.setFixedSize(self.experiment.textureWidth, self.experiment.textureHeight)
            self.video_label.setStyleSheet("QLabel { background-color: black; }")
            video_layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
            video_group.setLayout(video_layout)
            main_layout.addWidget(video_group)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(2)

        # Add groups to control panel
        main_layout.addWidget(control_panel)

        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.setFixedHeight(20)
        self.setStatusBar(self.statusBar)
        self.fps_label = QLabel("FPS: 0.0")
        self.statusBar.addPermanentWidget(self.fps_label)

        # Initialize variables
        self.filename = self.experiment.resultFilePath
        self.csv_file = None
        self.csv_writer = None
        self.video_writer = None

        # Create video thread
        self.thread = VideoThread()
        self.thread.frame_ready.connect(self.update_frame)
        self.thread.fps_updated.connect(self.update_fps)
        self.thread.landmarks_ready.connect(self.save_landmarks)

        self.thread.camera_index = self.experiment.cameraIndex

        # Connect signals
        

        # Set window size and show
        self.resize(self.experiment.textureWidth + 20, self.experiment.textureHeight + 70)
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
            if True:    #self.save_video_cb.isChecked():
                video_path = self.filename.replace('.csv', Constants.VIDEO_FORMAT)
                fourcc = cv2.VideoWriter_fourcc(*Constants.VIDEO_CODEC)
                self.video_writer = cv2.VideoWriter(
                    video_path,
                    fourcc,
                    25,    #float(self.fps_spinbox.value()),
                    (self.experiment.textureWidth, self.experiment.textureHeight)
                )
            
            # Reset the first timestamp
            self.first_timestamp = None

            # Start capture
            self.thread.recording = True
            self.thread.start()

            # Update UI
            self.statusBar.showMessage("Recording...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start capture: {str(e)}")

    def stop_capture(self):
        """Stop motion capture."""
        self.thread.recording = False
        self.thread.stop()

        # Desconectar o sinal para evitar gravações após o arquivo ser fechado
        try:
            self.thread.landmarks_ready.disconnect(self.save_landmarks)
        except TypeError:
            # O sinal já pode estar desconectado
            pass

        # Close files
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        # Update UI
        self.statusBar.showMessage("Capture finished", 3000)

    @Slot(np.ndarray)
    def update_frame(self, frame):
        """Update the video display."""
        if self.video_writer:
            self.video_writer.write(frame)

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        if self.experiment.showPreview:
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

