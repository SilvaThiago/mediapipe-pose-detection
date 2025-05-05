from datetime import datetime

from Extensions.AngleExtensions import AngleExtensions

class PoseMoment:    
    
    def __init__(self, timestamp, pose_points) :
        self.timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        self.pose_points = pose_points
        self.pose_degrees = {}
        # self.pose_degrees = [float(row[f'degree_{i}']) for i in range(1, 35)]
    
    def CalculateAngles(self, anglesToCalculate):
        """Calculate angles for each pose."""
        # Placeholder for angle calculation logic
        # This should be replaced with actual calculations based on pose_points
        if anglesToCalculate is not None:
            for angle in anglesToCalculate:
                if angle[0] == 'lines':
                    line1_point1 = self.pose_points[angle[2][0]]
                    line1_point2 = self.pose_points[angle[2][1]]
                    line2_point1 = self.pose_points[angle[3][0]]
                    line2_point2 = self.pose_points[angle[3][1]]
                    currentAngle = AngleExtensions.CalculateByLines((line1_point1, line1_point2), (line2_point1, line2_point2))
                    self.pose_degrees[angle[1]] = currentAngle
                    pass
                elif angle[0] == 'points':
                    currentAngle = AngleExtensions.CalculateByPoints(self.pose_points[angle[2]], self.pose_points[angle[3]], self.pose_points[angle[4]])
                    self.pose_degrees[angle[1]] = currentAngle
                    pass
            pass
        else:
            raise ValueError("anglesToCalculate cannot be None")    