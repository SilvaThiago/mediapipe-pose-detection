from datetime import datetime
import os

import cv2
from Services.CsvFileService import CsvFileService

import matplotlib.pyplot as plt

class AngleGraphicService:
    def __init__(self, csv_folder_path, experiment_string, angle_to_compare):
        self.cameras = []
        self.experiment_string = experiment_string
        self.csv_folder_path = csv_folder_path
        self.angle_to_compare = angle_to_compare
        self.csv_service = []
        self.camera_name = {
            "Camera 0": "90º Camera",
            "Camera 1": "0º Camera",
            "Camera 2": "45º Camera",
        }
        self.experiment_name = {
            "Bia_Agachamento": "Female Volunteer 1 Squat",
            "Bia_Empurrada": "Female Volunteer 1 Push",
            "Bia_Empurrada_Elastico": "Female Volunteer 1 Push with Elastic Band",
            "Bia_Puxada": "Female Volunteer 1 Pull",
            "Bia_Puxada_Elastico": "Female Volunteer 1 Pull with Elastic Band",
            "Stefanie_Agachamento": "Female Volunteer 2 Squat",
            "Stefanie_Empurrada": "Female Volunteer 2 Push",
            "Stefanie_Empurrada_Elastico": "Female Volunteer 2 Push with Elastic Band",
            "Stefanie_Puxada": "Female Volunteer 2 Pull",
            "Stefanie_Puxada_Elastico": "Female Volunteer 2 Pull with Elastic Band",
            "Thauanne_Agachamento": "Female Volunteer 3 Squat",
            "Thauanne_Empurrada": "Female Volunteer 3 Push",
            "Thauanne_Empurrada_Elastico": "Female Volunteer 3 Push with Elastic Band",
            "Thauanne_Puxada": "Female Volunteer 3 Pull",
            "Thauanne_Puxada_Elastico": "Female Volunteer 3 Pull with Elastic Band",
            "Nilson_Agachamento": "Male Volunteer 1 Squat",
            "Nilson_Empurrada": "Male Volunteer 1 Push",
            "Nilson_Empurrada_Elastico": "Male Volunteer 1 Push with Elastic Band",
            "Nilson_Puxada": "Male Volunteer 1 Pull",
            "Nilson_Puxada_Elastico": "Male Volunteer 1 Pull with Elastic Band",
            "Paulo_Agachamento": "Male Volunteer 2 Squat",
            "Paulo_Empurrada": "Male Volunteer 2 Push",
            "Paulo_Empurrada_Elastico": "Male Volunteer 2 Push with Elastic Band",
            "Paulo_Puxada": "Male Volunteer 2 Pull",
            "Paulo_Puxada_Elastico": "Male Volunteer 2 Pull with Elastic Band",
            "Thiago_Agachamento": "Male Volunteer 3 Squat",
            "Thiago_Empurrada": "Male Volunteer 3 Push",
            "Thiago_Empurrada_Elastico": "Male Volunteer 3 Push with Elastic Band",
            "Thiago_Puxada": "Male Volunteer 3 Pull",
            "Thiago_Puxada_Elastico": "Male Volunteer 3 Pull with Elastic Band",
        }
        print(f"Starting processing for: {self.experiment_string} - {self.angle_to_compare}")

    def load_data(self):
        """
        Load data from CSV file on specified, filtering by column of specified angle.
        """
        
        print(f"Loading data from: {self.csv_folder_path}")
        if not os.path.exists(self.csv_folder_path):
            raise FileNotFoundError(f"The path {self.csv_folder_path} does not exist.")

        self.cameras = []
        for file_name in os.listdir(self.csv_folder_path):
            if self.experiment_string == file_name.split('_Camera')[0] and file_name.endswith(".csv"):
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
            camera_name = self.camera_name[file_name.split('_')[-4]]
            camera_data = camera[0]
            timestamps = [(datetime.strptime(entry[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(camera_data[0][0], '%Y-%m-%d %H:%M:%S.%f')).total_seconds() for entry in camera_data]
            angles = [float(entry[1].replace(',', '.')) for entry in camera_data]
            plt.plot(timestamps, angles, label=f"{camera_name}")

        plt.title("Angle Comparison for '" + self.angle_to_compare + "' in experiment '" + self.experiment_name[self.experiment_string] + "'")
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
        
    @staticmethod
    def save_screenshot_from_video(video_path, seconds, output_path):

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        # Se seconds for uma tupla (segundos, milissegundos), converte para float
        if isinstance(seconds, tuple):
            sec = float(str(seconds[0]) + '.' + str(seconds[1]))
        else:
            sec = float(seconds)
        frame_number = int(fps * sec)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            raise ValueError(f"Could not read frame at {sec} seconds in {video_path}")

        cv2.imwrite(output_path, frame)
        cap.release()
        pass