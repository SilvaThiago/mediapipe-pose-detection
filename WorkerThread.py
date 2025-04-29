from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ExperimentWindow import ExperimentWindow

class WorkerThread(QThread):
    # Sinal para solicitar a criação de uma janela
    create_window_signal = pyqtSignal(ExperimentWindow)

    def __init__(self, experiment):
        super().__init__()
        self.experiment = experiment

    def run(self):
        # Emite o sinal para criar a janela
        self.create_window_signal.emit(self.experiment)