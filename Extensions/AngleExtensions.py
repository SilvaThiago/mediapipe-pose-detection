import math

class AngleExtensions:
    @staticmethod
    def CalculateByPoints(point1, point2, point3):
        """
        Calculate the angle formed by three points in 3D space.
        
        Args:
            point1 (tuple): Coordinates of the first point (x, y, z).
            point2 (tuple): Coordinates of the second point (x, y, z) - vertex of the angle.
            point3 (tuple): Coordinates of the third point (x, y, z).
        
        Returns:
            float: Angle in degrees.
        """
        # Calculate the vectors
        vector_a = (
            point1[0] - point2[0],
            point1[1] - point2[1],
            point1[2] - point2[2]
        )
        vector_b = (
            point3[0] - point2[0],
            point3[1] - point2[1],
            point3[2] - point2[2]
        )
        
        return AngleExtensions._calculate_angle_between_vectors(vector_a, vector_b)

    @staticmethod
    def CalculateByLines(line1, line2):
        """
        Calculate the angle between two lines in 3D space.
        
        Args:
            line1 (tuple): A tuple of two points defining the first line ((x1, y1, z1), (x2, y2, z2)).
            line2 (tuple): A tuple of two points defining the second line ((x3, y3, z3), (x4, y4, z4)).
        
        Returns:
            float: Angle in degrees.
        """
        # Calculate the direction vectors of the lines
        vector_a = (
            line1[1][0] - line1[0][0],
            line1[1][1] - line1[0][1],
            line1[1][2] - line1[0][2]
        )
        vector_b = (
            line2[1][0] - line2[0][0],
            line2[1][1] - line2[0][1],
            line2[1][2] - line2[0][2]
        )
        
        return AngleExtensions._calculate_angle_between_vectors(vector_a, vector_b)

    @staticmethod
    def _calculate_angle_between_vectors(vector_a, vector_b):
        """
        Helper method to calculate the angle between two vectors in 3D space.
        
        Args:
            vector_a (tuple): The first vector (x, y, z).
            vector_b (tuple): The second vector (x, y, z).
        
        Returns:
            float: Angle in degrees.
        """
        # Calculate the dot product and magnitudes
        dot_product = (
            vector_a[0] * vector_b[0] +
            vector_a[1] * vector_b[1] +
            vector_a[2] * vector_b[2]
        )
        magnitude_a = math.sqrt(
            vector_a[0]**2 + vector_a[1]**2 + vector_a[2]**2
        )
        magnitude_b = math.sqrt(
            vector_b[0]**2 + vector_b[1]**2 + vector_b[2]**2
        )
        
        # Avoid division by zero
        if magnitude_a == 0 or magnitude_b == 0:
            raise ValueError("Invalid Numbers: Zero length vector")
        
        # Calculate the angle in radians and convert to degrees
        # Clamp the value to the range [-1, 1] to avoid math domain errors
        cos_theta = max(-1.0, min(1.0, dot_product / (magnitude_a * magnitude_b)))
        angle_radians = math.acos(cos_theta)
        angle_degrees = math.degrees(angle_radians)
        
        return angle_degrees