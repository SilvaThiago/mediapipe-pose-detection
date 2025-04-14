from MotionCaptureWindow import MotionCaptureWindow
from ExperimentWindow import ExperimentWindow
from WorkerThread import WorkerThread

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

def get_available_cameras():
    """Get list of available camera devices."""
    camera_list = []
    for i in range(3):  # Check up to 3 cameras
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_list.append(f"Camera {i}")
            cap.release()
    return camera_list

class MainWindow(QMainWindow):
    """Main application window managing multiple motion capture windows."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motion Capture Manager")
        self.first_timestamp = None

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.setSpacing(1)

        # # Video feed group
        # video_group = QGroupBox("Video Feed")
        # video_layout = QVBoxLayout()
        # video_layout.setContentsMargins(1, 1, 1, 1)
        # video_layout.setSpacing(0)
        # self.video_label = QLabel()
        # self.video_label.setFixedSize(Constants.TEXTURE_WIDTH, Constants.TEXTURE_HEIGHT)
        # self.video_label.setStyleSheet("QLabel { background-color: black; }")
        # video_layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # video_group.setLayout(video_layout)
        # main_layout.addWidget(video_group)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.setSpacing(1)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(2)

        # Add new motion capture window button
        addWindow_group = QGroupBox("Add new capture window")
        addWindow_layout = QVBoxLayout()
        addWindow_layout.setContentsMargins(2, 2, 2, 2)
        addWindow_layout.setSpacing(1)

        self.camera_label = QLabel("Select Camera:")
        self.camera_label.setFixedHeight(20)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        addWindow_layout.addWidget(self.camera_label)

        camera_layout = QHBoxLayout()
        camera_layout.setSpacing(2)
        self.camera_combo = QComboBox()
        self.camera_combo.setFixedHeight(20)
        self.camera_combo.addItems(get_available_cameras())
        self.refresh_cameras_btn = QPushButton("Refresh Cameras")
        self.refresh_cameras_btn.setFixedHeight(20)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.addWidget(self.refresh_cameras_btn)
        addWindow_layout.addLayout(camera_layout)
        
        self.file_label = QLabel("Select File Path:")
        self.file_label.setFixedHeight(20)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        addWindow_layout.addWidget(self.file_label)

        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(2, 2, 2, 2)
        file_layout.setSpacing(1)
        self.filename_label = QLabel("No file selected")
        self.select_file_btn = QPushButton("Change File")
        self.select_file_btn.setFixedHeight(20)
        file_layout.addWidget(self.filename_label)
        file_layout.addWidget(self.select_file_btn)
        addWindow_layout.addLayout(file_layout)
        
        self.add_window_btn = QPushButton("Add Window")
        self.add_window_btn.setFixedHeight(20)
        self.add_window_btn.setEnabled(True)
        addWindow_layout.addWidget(self.add_window_btn)

        addWindow_group.setLayout(addWindow_layout)


        # Current experiment resources group
        experimentResources_group = QGroupBox("Current Experiment Resources")
        experimentResources_layout = QVBoxLayout()
        experimentResources_layout.setContentsMargins(2, 2, 2, 2)
        experimentResources_layout.setSpacing(1)
        self.start_btn = QPushButton("Start Experiment")
        self.start_btn.setFixedHeight(20)
        self.start_btn.setEnabled(False)
        experimentResources_layout.addWidget(self.start_btn)
        experimentResources_group.setLayout(experimentResources_layout)

        # self.close_btn = QPushButton("Close")
        # self.close_btn.setFixedHeight(20)
        # capture_layout.addWidget(self.close_btn)
        # capture_group.setLayout(capture_layout)

        # # Add groups to control panel
        control_layout.addWidget(addWindow_group)
        control_layout.addWidget(experimentResources_group)
        main_layout.addWidget(control_panel)

        # # Status bar
        # self.statusBar = QStatusBar()
        # self.statusBar.setFixedHeight(20)
        # self.setStatusBar(self.statusBar)
        # self.fps_label = QLabel("FPS: 0.0")
        # self.statusBar.addPermanentWidget(self.fps_label)

        # Initialize variables
        self.filename = None
        self.csv_file = None
        self.csv_writer = None
        self.video_writer = None
        self.currentExperimentList = None
        
        # Criação de threads para abrir janelas
        self.threads = []

        # # Create video thread
        # self.thread = VideoThread()
        # self.thread.frame_ready.connect(self.update_frame)
        # self.thread.fps_updated.connect(self.update_fps)
        # self.thread.landmarks_ready.connect(self.save_landmarks)

        # # Connect signals
        self.select_file_btn.clicked.connect(self.select_file)
        self.add_window_btn.clicked.connect(self.add_window)
        self.start_btn.clicked.connect(self.start_experiment)
        # self.start_btn.clicked.connect(self.start_capture)
        # self.stop_btn.clicked.connect(self.stop_capture)
        # self.close_btn.clicked.connect(self.close)
        # self.refresh_cameras_btn.clicked.connect(self.refresh_cameras)
        # self.camera_combo.currentIndexChanged.connect(self.camera_changed)
        # self.show_landmarks_cb.stateChanged.connect(self.toggle_landmarks)
        # self.model_complexity_combo.currentIndexChanged.connect(self.update_model_complexity)

        # Initial UI state
        # self.stop_btn.setEnabled(False)
        self.generate_filename()

        # Set window size and show
        self.resize(Constants.TEXTURE_WIDTH + 20, 250)
        self.show()

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

    def add_window(self):
        """Fill a ExperimentWindow object with the selected camera and file and create it on CurrentExperiment group."""
        experimentWindow = ExperimentWindow(self.camera_combo.currentText(), self.filename, showPreview=True)

        isExperimentValid = self.CheckExperimentWindow(experimentWindow)
        if not isExperimentValid:
            return
        
        # Add the ExperimentWindow to the current experiment list
        if self.currentExperimentList is None:
            self.currentExperimentList = []
        self.currentExperimentList.append(experimentWindow)
            
        # Create a QLabel to display the experiment information
        experiment_info = f"[{len(self.currentExperimentList)}] {experimentWindow.chosenCamera}, File: {experimentWindow.resultFilePath}, Preview: {experimentWindow.showPreview}"
        experiment_label = QLabel(experiment_info)
        experiment_label.setFixedHeight(20)

        # Add the QLabel to the experimentResources_group layout
        self.start_btn.setEnabled(True)
        experimentResources_layout = self.start_btn.parentWidget().layout()
        experimentResources_layout.addWidget(experiment_label)      

    def CheckExperimentWindow(self, experimentWindow):
        if experimentWindow.chosenCamera is None:
            QMessageBox.warning(self, "Warning", "Please select a file path first.")
            return False
        if experimentWindow.resultFilePath == "":
            QMessageBox.warning(self, "Warning", "Please select a camera.")
            return False
        # Check if the camera is already in the currentExperimentList
        if self.currentExperimentList is not None:
            for existing_experiment in self.currentExperimentList:
                if existing_experiment.chosenCamera == experimentWindow.chosenCamera:
                    QMessageBox.warning(self, "Warning", f"Camera '{experimentWindow.chosenCamera}' is already in use.")
                    return False
        return True

    def start_experiment(self):
        """Start the experiment by opening all ExperimentWindow objects."""

        windows = []  # List to keep track of opened windows
                              
        # Função para criar uma janela
        def create_window(title):
            window = MotionCaptureWindow(title)
            window.show()
            windows.append(window)  # Armazena a referência para evitar garbage collection

        
        if self.currentExperimentList is not None:
            for experiment in self.currentExperimentList: 
                thread = WorkerThread(f"Window {len(windows) + 1}")
                thread.create_window_signal.connect(create_window)
                self.threads.append(thread)
                thread.start() 
        else:
            QMessageBox.warning(self, "Warning", "No experiment windows to start.")
            self.start_btn.setEnabled(False)
            return
        


        


    def generate_filename(self):
        """Generate automatic filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        self.filename = os.path.join(documents_path, f"motion_capture_{timestamp}.csv")
        self.filename_label.setText(f"File: {self.filename}")
        # self.start_btn.setEnabled(True)
    