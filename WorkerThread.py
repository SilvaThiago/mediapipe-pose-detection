from PyQt6.QtCore import Qt, QThread, pyqtSignal

class WorkerThread(QThread):
    # Sinal para solicitar a criação de uma janela
    create_window_signal = pyqtSignal(str)

    def __init__(self, window_name):
        super().__init__()
        self.window_name = window_name

    def run(self):
        # Emite o sinal para criar a janela
        self.create_window_signal.emit(self.window_name)