import unittest
from Extensions.AngleExtensions import AngleExtensions
from Models.PosePoint import PosePoint
class Test_AngleExtensions(unittest.TestCase):

    def test_calculate_by_points_valid_3d(self):
        # Test with valid 3D points forming an angle
        point1 = PosePoint(1, 0, 0)
        point2 = PosePoint(0, 0, 0)
        point3 = PosePoint(1, 1, 0)
        result = AngleExtensions.CalculateByPoints(point1, point2, point3)
        self.assertAlmostEqual(result, 45.0, places=1)

    def test_calculate_by_points_collinear_3d(self):
        # Test with collinear 3D points
        point1 = PosePoint(0, 0, 0)
        point3 = PosePoint(2, 2, 2)
        point2 = PosePoint(1, 1, 1)
        result = AngleExtensions.CalculateByPoints(point1, point2, point3)
        self.assertIn(result, [0.0, 180.0, 360.0])  # Collinear points should return 0, 180 or 360 degrees

    def test_calculate_by_points_invalid_3d(self):
        # Test with invalid 3D points (e.g., identical points)
        point1 = PosePoint(1, 1, 1)
        point2 = PosePoint(1, 1, 1)
        point3 = PosePoint(1, 1, 1)
        with self.assertRaises(ValueError):
            AngleExtensions.CalculateByPoints(point1, point2, point3)

    def test_calculate_by_points_right_angle_3d(self):
        # Test with 3D points forming a right angle (90 degrees)
        point1 = PosePoint(0, 0, 0)
        point2 = PosePoint(1, 0, 0)
        point3 = PosePoint(1, 1, 0)
        result = AngleExtensions.CalculateByPoints(point1, point2, point3)
        self.assertAlmostEqual(result, 90.0, places=1)

    def test_calculate_by_points_acute_angle_3d(self):
        # Test with 3D points forming an acute angle (< 90 degrees)
        point1 = PosePoint(0, 0, 0)
        point2 = PosePoint(1, 1, 1)
        point3 = PosePoint(2, 0, 0)
        result = AngleExtensions.CalculateByPoints(point1, point2, point3)
        self.assertLess(result, 90.0)
        self.assertGreater(result, 0.0)

    def test_calculate_by_points_obtuse_angle_3d(self):
        # Test with 3D points forming an obtuse angle (> 90 degrees)
        point1 = PosePoint(2, 0, 0)
        point2 = PosePoint(0, 0, 0)
        point3 = PosePoint(-1, 1, 0)
        result = AngleExtensions.CalculateByPoints(point1, point2, point3)
        self.assertLess(result, 180.0)
        self.assertGreater(result, 90.0)

    def test_calculate_by_points_zero_angle_3d(self):
        # Test with 3D points forming a zero angle (0 degrees)
        point1 = PosePoint(0, 0, 0)
        point2 = PosePoint(2, 2, 2)
        point3 = PosePoint(1, 1, 1)
        result = AngleExtensions.CalculateByPoints(point1, point2, point3)
        self.assertEqual(result, 0.0)

    def test_calculate_by_points_straight_angle_3d(self):
        # Test with 3D points forming a straight angle (180 degrees)
        point1 = PosePoint(0, 0, 0)
        point2 = PosePoint(1, 1, 1)
        point3 = PosePoint(2, 2, 2)
        result = AngleExtensions.CalculateByPoints(point1, point2, point3)
        self.assertAlmostEqual(result, 180.0, places=1)

    def test_calculate_by_points_coincident_points_3d(self):
        # Test with coincident 3D points
        point1 = PosePoint(1, 1, 1)
        point2 = PosePoint(1, 1, 1)
        point3 = PosePoint(2, 2, 2)
        with self.assertRaises(ValueError):
            AngleExtensions.CalculateByPoints(point1, point2, point3)

    def test_calculate_by_lines_right_angle_3d(self):
        # Test with 3D lines forming a right angle (90 degrees)
        line1 = (PosePoint(0, 0, 0), PosePoint(1, 0, 0))
        line2 = (PosePoint(0, 0, 0), PosePoint(0, 1, 0))
        result = AngleExtensions.CalculateByLines(line1, line2)
        self.assertAlmostEqual(result, 90.0, places=1)

    def test_calculate_by_lines_acute_angle_3d(self):
        # Test with 3D lines forming an acute angle (< 90 degrees)
        line1 = (PosePoint(0, 0, 0), PosePoint(1, 1, 1))
        line2 = (PosePoint(0, 0, 0), PosePoint(2, 0, 0))
        result = AngleExtensions.CalculateByLines(line1, line2)
        self.assertLess(result, 90.0)
        self.assertGreater(result, 0.0)

    def test_calculate_by_lines_obtuse_angle_3d(self):
        # Test with 3D lines forming an obtuse angle (> 90 degrees)
        line1 = (PosePoint(0, 0, 0), PosePoint(1, 0, 0))
        line2 = (PosePoint(0, 0, 0), PosePoint(-1, 1, 1))
        result = AngleExtensions.CalculateByLines(line1, line2)
        self.assertLess(result, 180.0)
        self.assertGreater(result, 90.0)

    def test_calculate_by_lines_zero_angle_3d(self):
        # Test with 3D lines forming a zero angle (0 degrees)
        line1 = (PosePoint(0, 0, 0), PosePoint(1, 1, 1))
        line2 = (PosePoint(0, 0, 0), PosePoint(1, 1, 1))
        result = AngleExtensions.CalculateByLines(line1, line2)
        self.assertEqual(result, 0.0)

    def test_calculate_by_lines_straight_angle_3d(self):
        # Test with 3D lines forming a straight angle (180 degrees)
        line1 = (PosePoint(0, 0, 0), PosePoint(1, 0, 0))
        line2 = (PosePoint(0, 0, 0), PosePoint(-1, 0, 0))
        result = AngleExtensions.CalculateByLines(line1, line2)
        self.assertAlmostEqual(result, 180.0, places=1)

    def test_calculate_by_lines_degenerate_lines_3d(self):
        # Test with degenerate 3D lines (points coinciding)
        line1 = (PosePoint(1, 1, 1), PosePoint(1, 1, 1))
        line2 = (PosePoint(0, 0, 0), PosePoint(1, 1, 1))
        with self.assertRaises(ValueError):
            AngleExtensions.CalculateByLines(line1, line2)

    def test_calculate_by_lines_perpendicular_non_intersecting(self):
        # Test with 3D lines that are perpendicular but do not intersect
        line1 = (PosePoint(1, 0, 0), PosePoint(2, 0, 0))  # Line along the x-axis
        line2 = (PosePoint(0, 1, 0), PosePoint(0, 2, 0))  # Line along the y-axis
        result = AngleExtensions.CalculateByLines(line1, line2)
        self.assertAlmostEqual(result, 90.0, places=1)

if __name__ == '__main__':
    unittest.main()