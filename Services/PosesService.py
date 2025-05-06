import csv
from Models.PoseMoment import PoseMoment
from Models.PosePoint import PosePoint

class PosesService:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.poses = []

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
    
    def CalculatePoseAngles(self, anglesToCalculate):
        """Calculate angles for each pose."""
        for pose in self.poses:
            pose.CalculateAngles(anglesToCalculate)
            
    