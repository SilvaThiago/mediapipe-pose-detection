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

    def start_capture(self):
        """Start motion capture."""
        print("Start capture for {self.experiment.chosenCamera}")
        if not self.filename:
            QMessageBox.warning(self, "Error", "Please select a file to save data.")
            return

        try:
            # Initialize CSV file
            print(f"Open csv file for {self.experiment.chosenCamera}")
            self.csv_file = open(self.filename, mode='w', newline='')
            self.csv_writer = csv.writer(self.csv_file,delimiter=';')

            # Write CSV headers
            headers = ['timestamp']
            for i in range(33):
                headers.extend([f'pose_{i}_x', f'pose_{i}_y', f'pose_{i}_z', f'pose_{i}_v'])
            # for i in range(21):
            #     headers.extend([f'lhand_{i}_x', f'lhand_{i}_y', f'lhand_{i}_z'])
            #     headers.extend([f'rhand_{i}_x', f'rhand_{i}_y', f'rhand_{i}_z'])
            print(f"Write in csv file for {self.experiment.chosenCamera}")
            self.csv_writer.writerow(headers)

            # Initialize video writer if needed
            if self.experiment.saveVideo:
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
        print(f"Stop capture for {self.experiment.chosenCamera}")
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
            print(f"Close csv file for {self.experiment.chosenCamera}")
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None

        if self.video_writer:
            print(f"Releasing video writer for {self.experiment.chosenCamera}")
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
            landmarks[0] = datetime.now()

            print(f"Writing into csv for  {self.experiment.chosenCamera}")
            self.csv_writer.writerow(landmarks)

    def closeEvent(self, event):
        """Handle window close event."""
        
        print(f"Close event for {self.experiment.chosenCamera}")
        self.stop_capture()
        event.accept()

