from MotionCaptureWindow import MotionCaptureWindow

import sys
from PyQt6.QtWidgets import (QApplication)
from PyQt6.QtCore import Qt
import os
import tensorflow as tf

# Optimize TensorFlow for M1
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'  # Enable oneDNN optimizations
os.environ['TF_METAL_ENABLED'] = '1'      # Enable Metal GPU acceleration

# Verify TensorFlow and GPU support
print(f"TensorFlow version: {tf.__version__}")
print("GPU available:", tf.config.list_physical_devices('GPU'))

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