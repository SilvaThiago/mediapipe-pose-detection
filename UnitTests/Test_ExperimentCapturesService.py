import unittest
from Services.ExperimentCapturesService import ExperimentCapturesService

class Test_ExperimentCapturesService(unittest.TestCase):
    def test_process_all_csv_from_folder_success(self):
        # Arrange
        experimentCaptureService = ExperimentCapturesService()

        # Act
        result = experimentCaptureService.ProcessAllCsvFromFolder('C:\\Users\\thiag\\OneDrive\\Área de Trabalho\\Temporário\\2025-05-04 Poses test\\Experimento00')

        # Assert
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()