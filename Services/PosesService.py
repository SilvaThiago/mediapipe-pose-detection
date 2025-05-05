import csv
from Models.PoseMoment import PoseMoment
from Models.PosePoint import PosePoint

class PosesService:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.poses = []
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

    def load_poses_from_csv(self):
        """Load poses from the CSV file."""
        try:
            with open(self.csv_file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    # Convert the row to a PoseMoment object
                    pose_points = [
                        PosePoint(float(row[f'pose_{i}_x']), float(row[f'pose_{i}_y']), float(row[f'pose_{i}_z']))
                        for i in range(33)
                    ]
                    timestamp = row['timestamp']
                    pose_moment = PoseMoment(timestamp, pose_points)
                    self.poses.append(pose_moment)

        except FileNotFoundError:
            print(f"Error: File '{self.csv_file_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def CalculatePoseAngles(self):
        """Calculate angles for each pose."""
        for pose in self.poses:
            pose.CalculateAngles(self.anglesToCalculate)

    def get_pose_by_index(self, index):
        """Retrieve a pose by its index."""
        if 0 <= index < len(self.poses):
            return self.poses[index]
        else:
            print("Error: Index out of range.")
            return None

    def save_poses_to_csv(self, output_file_path):
        """Save the current poses to a new CSV file."""
        if not self.poses:
            print("No poses to save.")
            return

        try:
            with open(output_file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.poses[0].keys())
                writer.writeheader()
                writer.writerows(self.poses)
        except Exception as e:
            print(f"An error occurred while saving: {e}")