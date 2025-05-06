from Services.PosesService import PosesService
import os
import csv

class ExperimentCapturesService:
    def __init__(self):
        self.poses_service = None
        self.anglesToCalculate = [
            ('lines', 'left_ankle', (26, 28), (30,32)), # left ankle
            ('lines', 'right_ankle', (25, 27), (29,31)), # right ankle
            ('points', 'left_knee', 24, 26, 28), # left knee
            ('points', 'right_knee', 23, 25, 27), # right knee
            ('points', 'left_hip', 12, 24, 26), # left side hip  
            ('points', 'right_hip', 11, 23, 25), # righ side hip   
            ('points', 'left_vertical_shoulder', 14, 12, 24), # left vertical shoulder  
            ('points', 'right_vertical_shoulder', 13, 11, 23), # right vertical shoulder
            ('points', 'left_horizontal_shoulder', 11, 12, 14), # left horizontal shoulder  
            ('points', 'right_horizontal_shoulde', 12, 11, 13), # right horizontal shoulder
            ('points', 'left_elbow', 12, 14, 16), # left elbow  
            ('points', 'right_elbow', 11, 13, 15), # right elbow
        ]

    def ProcessAllCsvFromFolder(self, folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(folder_path, file_name)
                self.poses_service = PosesService(file_path)
                self.poses_service.load_poses_from_csv()
                self.poses_service.CalculatePoseAngles(self.anglesToCalculate)
                
                output_file_name = f"{os.path.splitext(file_name)[0]}_angles.csv"
                output_file_path = os.path.join(folder_path, output_file_name)
                
                with open(output_file_path, mode='w', newline='') as output_file:
                    csv_writer = csv.writer(output_file, delimiter=';')
                    header = ['timestamp'] + [angle[1] for angle in self.anglesToCalculate]
                    csv_writer.writerow(header)
                    
                    for pose in self.poses_service.poses:
                        row = [pose.timestamp] + [
                            f"{float(pose.pose_degrees[angle[1]]):.2f}".replace('.', ',') for angle in self.anglesToCalculate
                        ]
                        csv_writer.writerow(row)