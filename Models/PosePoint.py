class PosePoint:
    """
    Represents a point in 3D space with an associated value.
    Attributes:
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
        z (float): The z-coordinate of the point.
    Methods:
        __repr__(): Returns a string representation of the PosePoint object.
    """
    # This class is used to represent a point in 3D space
    # with an associated value, useful for pose detection or other calculations.
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"PosePoint(x={self.x}, y={self.y}, z={self.z})"
    

