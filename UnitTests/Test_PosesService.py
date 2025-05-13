import unittest
from Models.PoseMoment import PoseMoment
from Services.PosesService import PosesService

class Test_Test_PosesService(unittest.TestCase):
    def test_load_valid_csv(self):
        # Arrange
        valid_csv_path = "C:/Users/thiag/OneDrive/Área de Trabalho/Temporário/2025-05-04 Poses test/motion_capture_Camera 0_20250417_113738.csv"
        service = PosesService(valid_csv_path)
        expected_poses_count = 817  

        # Act
        service.load_poses_from_csv()

        # Assert
        self.assertEqual(len(service.poses), expected_poses_count)
        for pose in service.poses:
            self.assertIsInstance(pose, PoseMoment)  # Assuming PosePoint is the expected object type

if __name__ == '__main__':
    unittest.main()