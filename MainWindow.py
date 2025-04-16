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

        checkbox_layout = QHBoxLayout()
        checkbox_layout.setContentsMargins(2, 2, 2, 2) 
        checkbox_layout.setSpacing(1)

        self.showPreview_cb = QCheckBox("Show Preview:")
        self.showPreview_cb.setChecked(True)    
        checkbox_layout.addWidget(self.showPreview_cb)
        self.saveVideo_cb = QCheckBox("Save Video:")
        self.saveVideo_cb.setChecked(True)
        checkbox_layout.addWidget(self.saveVideo_cb)  
        addWindow_layout.addLayout(checkbox_layout) 
        
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

        experimentButtons_layout = QHBoxLayout()
        experimentButtons_layout.setContentsMargins(2, 2, 2, 2)
        self.open_experiment_btn = QPushButton("Open Experiment")
        self.open_experiment_btn.setFixedHeight(20)
        self.open_experiment_btn.setEnabled(False)
        self.start_btn = QPushButton("Start Experiment")
        self.start_btn.setFixedHeight(20)
        self.start_btn.setEnabled(False)
        self.stop_btn = QPushButton("Stop Experiment")
        self.stop_btn.setFixedHeight(20)
        self.stop_btn.setEnabled(False)
        self.close_btn = QPushButton("Close and Clear Experiment")
        self.close_btn.setFixedHeight(20)
        self.close_btn.setEnabled(False)
        experimentButtons_layout.addWidget(self.open_experiment_btn)
        experimentButtons_layout.addWidget(self.start_btn)
        experimentButtons_layout.addWidget(self.stop_btn)
        experimentButtons_layout.addWidget(self.close_btn)

        experimentResources_layout.addLayout(experimentButtons_layout)
        experimentResources_group.setLayout(experimentResources_layout)

        # # Add groups to control panel
        control_layout.addWidget(addWindow_group)
        control_layout.addWidget(experimentResources_group)
        main_layout.addWidget(control_panel)

        # Initialize variables
        self.filename = None
        self.csv_file = None
        self.csv_writer = None
        self.video_writer = None
        self.currentExperimentList = None
        
        # Criação de threads para abrir janelas
        self.threads = []
        self.windows = []  # List to keep track of opened windows

        # # Connect signals
        self.select_file_btn.clicked.connect(self.select_file)
        self.add_window_btn.clicked.connect(self.add_window)
        self.open_experiment_btn.clicked.connect(self.open_experiment)
        self.start_btn.clicked.connect(self.start_experiment)
        self.stop_btn.clicked.connect(self.stop_experiment)
        self.close_btn.clicked.connect(self.close_experiment)
        self.refresh_cameras_btn.clicked.connect(self.refresh_cameras)
        self.camera_combo.currentIndexChanged.connect(self.generate_filename)  

        # Initial UI state
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
            self.open_experiment_btn.setEnabled(True)

    def add_window(self):
        """Fill a ExperimentWindow object with the selected camera and file and create it on CurrentExperiment group."""
        textureWidth = Constants.TEXTURE_WIDTH
        textureHeight = Constants.TEXTURE_HEIGHT
        if not self.showPreview_cb.isChecked():
            textureWidth = 500
            textureHeight = 250

        experimentWindow = ExperimentWindow(self.camera_combo.currentText(), 
                                            self.camera_combo.currentIndex(), 
                                            self.filename, 
                                            self.showPreview_cb.isChecked(),
                                            self.saveVideo_cb.isChecked(),
                                            textureWidth,
                                            textureHeight)

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
        print(f"Added: {experiment_info}")

        # Add the QLabel to the experimentResources_group layout
        self.open_experiment_btn.setEnabled(True)
        experimentResources_layout = self.open_experiment_btn.parentWidget().layout()
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

    def open_experiment(self):
        """Open the experiment by opening all ExperimentWindow objects."""
                              
        # Função para criar uma janela
        def create_window(experiment):
            window = MotionCaptureWindow(experiment)
            window.show()
            self.windows.append(window)  # Armazena a referência para evitar garbage collection

        
        if self.currentExperimentList is not None:
            for experiment in self.currentExperimentList: 
                thread = WorkerThread(experiment)
                thread.create_window_signal.connect(create_window)
                self.threads.append(thread)
                print(f"Create window starting thread {thread.experiment.chosenCamera}")
                thread.start() 
            self.open_experiment_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        else:
            QMessageBox.warning(self, "Warning", "No experiment windows to start.")
            self.open_experiment_btn.setEnabled(False)
            return

    def start_experiment(self):
        """Start the experiment by starting capturing."""
        
        for window in self.windows:
            window.start_capture()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.close_btn.setEnabled(False)

    def stop_experiment(self):
        """Stop the experiment by stopping capturing."""
        
        for window in self.windows:
            window.stop_capture()
        self.stop_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.close_btn.setEnabled(True)

    def close_experiment(self):
        """close the experiment by closing windows and clearing current experiment."""
            
        # Close all open windows
        for window in self.windows:
            window.close()
        self.windows.clear()

        # Clear the current experiment list
        self.currentExperimentList = None

        # Remove all widgets (experiment labels) from experimentResources_layout
        experimentResources_layout = self.open_experiment_btn.parentWidget().layout()
        while experimentResources_layout.count():
            item = experimentResources_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # Properly delete the widget

        self.currentExperimentList = None
        self.stop_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.open_experiment_btn.setEnabled(False)

    def refresh_cameras(self):
        """Refresh the list of available cameras."""
        current_camera = self.camera_combo.currentIndex()
        self.camera_combo.clear()
        self.camera_combo.addItems(get_available_cameras())
        if current_camera < self.camera_combo.count():
            self.camera_combo.setCurrentIndex(current_camera)

    def generate_filename(self):
        """Generate automatic filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        self.filename = os.path.join(documents_path, f"motion_capture_{self.camera_combo.currentText()}_{timestamp}.csv")
        self.filename_label.setText(f"File: {self.filename}")
        # self.open_experiment_btn.setEnabled(True)
    