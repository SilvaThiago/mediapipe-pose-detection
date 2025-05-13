from datetime import datetime
import os
from Services.CsvFileService import CsvFileService

import matplotlib.pyplot as plt

class AngleGraphicService:
    def __init__(self, csv_folder_path, experiment_string, angle_to_compare):
        self.cameras = []
        self.experiment_string = experiment_string
        self.csv_folder_path = csv_folder_path
        self.angle_to_compare = angle_to_compare
        self.csv_service = []
        print(f"Starting processing for: {self.experiment_string} - {self.angle_to_compare}")

    def load_data(self):
        """
        Carrega os dados dos arquivos CSV no caminho especificado, filtrando pelas colunas de ângulo especificadas.
        """
        
        print(f"Loading data from: {self.csv_folder_path}")
        if not os.path.exists(self.csv_folder_path):
            raise FileNotFoundError(f"O caminho {self.csv_folder_path} não existe.")

        self.cameras = []
        for file_name in os.listdir(self.csv_folder_path):
            if self.experiment_string in file_name and file_name.endswith(".csv"):
                file_path = os.path.join(self.csv_folder_path, file_name)
                aux_csv_service=CsvFileService(file_path)
                try:
                    data = aux_csv_service.read_csv()
                    keys = []
                    if data:
                        keys = list(data[0])
                    if any(self.angle_to_compare == column for column in keys):
                        self.cameras.append(([(row['timestamp'], row[self.angle_to_compare]) for row in data], file_name))
                    else:
                        raise ValueError(f"A coluna '{self.angle_to_compare}' não foi encontrada em {file_name}.")
                except Exception as e:
                    print(f"Erro ao processar o arquivo {file_name}: {e}")

    def generate_comparative_graph(self):
        """
        Generates a comparative graph of angle values from different files.

        :param output_file: Name of the output file to save the graph.
        """
        print(f"Generating graph")
        if not self.cameras:
            raise ValueError("No camera data has been loaded.")

        plt.figure(figsize=(10, 6))

        for camera in self.cameras:
            file_name = camera[1] 
            camera_name = file_name.split('_')[-4]
            camera_data = camera[0]
            timestamps = [(datetime.strptime(entry[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(camera_data[0][0], '%Y-%m-%d %H:%M:%S.%f')).total_seconds() for entry in camera_data]
            angles = [float(entry[1].replace(',', '.')) for entry in camera_data]
            plt.plot(timestamps, angles, label=f"{camera_name}")

        plt.title("Angle Comparison for angle " + self.angle_to_compare + " in experiment " + self.experiment_string)
        plt.xlabel("Time (seconds)")
        plt.ylabel("Angle (degrees)")
        plt.legend()
        plt.grid(True)

        output_file = self.experiment_string + "_" + self.angle_to_compare + ".png"
        output_path = os.path.join(os.path.dirname(__file__), '..', 'Resources', 'GenerateGraphics_Experiment', "Results", output_file)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        plt.savefig(output_path)
        plt.close()