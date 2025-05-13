import unittest
from Models.PoseMoment import PoseMoment
from Services.PosesService import PosesService

class Test_PoseMoment(unittest.TestCase):

    def test_calculate_angles_success(self):
        # Arrange
        valid_csv_path = "C:/Users/thiag/OneDrive/Área de Trabalho/Temporário/2025-05-04 Poses test/motion_capture_Camera 2_20250417_113906.csv"
        service = PosesService(valid_csv_path)        
        service.load_poses_from_csv()

        anglesToCalculate = [
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
        expected_angles = {
            'left_ankle': 93.79805227158938,
            'left_elbow': 80.11651387332616,
            'left_hip': 160.9022598376762,
            'left_horizontal_shoulder': 87.14506015931514,
            'left_knee': 155.81361892399372,
            'left_vertical_shoulder': 41.96020532520427,
            'right_ankle': 113.97865785680341,
            'right_elbow': 143.65851291510467,
            'right_hip': 142.45013772882442,
            'right_horizontal_shoulde': 38.84203072626269,
            'right_knee': 165.75999160341775,
            'right_vertical_shoulder': 65.03988727437296
        }

        # Act
        for pose in service.poses:
            pose.CalculateAngles(anglesToCalculate)

        # Assert
            self.assertEqual(service.poses[0].pose_degrees, expected_angles)    

if __name__ == '__main__':
    unittest.main()