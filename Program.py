from MotionCaptureWindow import MotionCaptureWindow

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import tensorflow as tf


# Optimize TensorFlow for M1
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'  # Enable oneDNN optimizations
os.environ['TF_METAL_ENABLED'] = '1'      # Enable Metal GPU acceleration

# Verify TensorFlow and GPU support
print(f"TensorFlow version: {tf.__version__}")
print("GPU available:", tf.config.list_physical_devices('GPU'))


class WorkerThread(QThread):
    # Sinal para solicitar a criação de uma janela
    create_window_signal = pyqtSignal(str)

    def __init__(self, window_name):
        super().__init__()
        self.window_name = window_name

    def run(self):
        # Emite o sinal para criar a janela
        self.create_window_signal.emit(self.window_name)


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

    
    # Função para criar uma janela
    def create_window(title):
        window = MotionCaptureWindow(title)
        window.show()
        windows.append(window)  # Armazena a referência para evitar garbage collection

    windows = []  # Lista para manter as janelas abertas

    # Criação de threads para abrir janelas
    threads = []
    for i in range(2):
        thread = WorkerThread(f"Window {i + 1}")
        thread.create_window_signal.connect(create_window)
        threads.append(thread)
        thread.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()