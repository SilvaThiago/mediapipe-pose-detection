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
                    isRowValid = True
                    pose_points = []
                    # Convert the row to a PoseMoment object
                    for i in range(33):
                        if (self.IsValuesInsideInterval(row[f'pose_{i}_x'], row[f'pose_{i}_y'], row[f'pose_{i}_z'])):
                            pose_points.append(PosePoint(float(row[f'pose_{i}_x']), float(row[f'pose_{i}_y']), float(row[f'pose_{i}_z'])))
                        else:
                            isRowValid = False
                    if (isRowValid):
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
            # if not pose.CalculateAngles(anglesToCalculate):
            #     print(f"Error calculating angles for pose at {pose.timestamp}.")
            #     self.poses.remove(pose)

    
    @staticmethod
    def IsValuesInsideInterval(*numbers):
        """Validate if the given number are within the range [-1, 1]."""
        for number in numbers:
            try:
                floatValue = float(number)
                if not -1 <= floatValue <= 1:
                    print(f"Invalid number: {floatValue}. Number must be in the range [-1, 1].")
                    return False
            except ValueError: 
                return False
        return True     
    