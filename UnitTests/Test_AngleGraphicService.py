import os
import unittest
from Services.AngleGraphicService import AngleGraphicService

class TestAngleGraphicService(unittest.TestCase):
    def setUp(self):
        self.csv_folder_path = os.path.join(os.path.dirname(__file__), '..', 'Resources', 'GenerateGraphics_Experiment')
        self.experiment_strings = [
            "Bia_Puxada",
            "Bia_Empurrada",
            "Bia_Puxada_Elastico",
            "Bia_Empurrada_Elastico",
            "Bia_Agachamento",
            "Nilson_Puxada",
            "Nilson_Empurrada",
            "Nilson_Puxada_Elastico",
            "Nilson_Empurrada_Elastico",
            "Nilson_Agachamento",
            "Paulo_Puxada",
            "Paulo_Empurrada",
            "Paulo_Puxada_Elastico",
            "Paulo_Empurrada_Elastico",
            "Paulo_Agachamento",
            "Stefanie_Puxada",
            "Stefanie_Empurrada",
            "Stefanie_Puxada_Elastico",
            "Stefanie_Empurrada_Elastico",
            "Stefanie_Agachamento",
            "Thauanne_Puxada",
            "Thauanne_Empurrada",
            "Thauanne_Puxada_Elastico",
            "Thauanne_Empurrada_Elastico",
            "Thauanne_Agachamento",
            "Thiago_Puxada",
            "Thiago_Empurrada",
            "Thiago_Puxada_Elastico",
            "Thiago_Empurrada_Elastico",
            "Thiago_Agachamento"
        ]
        self.angles_to_compare = [
            'left_ankle', 
            'right_ankle',
            'left_knee', 
            'right_knee', 
            'left_hip', 
            'right_hip', 
            'left_vertical_shoulder', 
            'right_vertical_shoulder', 
            'left_horizontal_shoulder', 
            'right_horizontal_shoulde', 
            'left_elbow', 
            'right_elbow'
        ]

    def test_load_data(self):
        # Arrange        
        
        # Act
        for experiment_string in self.experiment_strings:
            for angle_to_compare in self.angles_to_compare:
                service = AngleGraphicService(self.csv_folder_path, experiment_string, angle_to_compare)
                service.load_data()
                service.generate_comparative_graph()
        
        # Assert
        self.assertTrue(self.service.cameras)

if __name__ == '__main__':
    unittest.main()