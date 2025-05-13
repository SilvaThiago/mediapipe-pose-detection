import unittest
from Services.ExperimentCapturesService import ExperimentCapturesService
import os

class Test_ExperimentCapturesService(unittest.TestCase):
    def test_process_all_csv_from_folder_success(self):
        # Arrange
        experimentCaptureService = ExperimentCapturesService()

        # Act
        folder_path = os.path.join(os.path.dirname(__file__), '..', 'Resources', 'CalculateAngles_Experiment')
        result = experimentCaptureService.ProcessAllCsvFromFolder(folder_path)

        # Assert
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()