import numpy as np
import cv2

class region_class:
    def __init__(self, image: np.ndarray):
        self.image = image
        self.display_img = image.copy()
        self.image_width = image.shape[1]
        self.image_height = image.shape[0]
        self.mask = np.zeros((self.image_height, self.image_width), dtype=np.uint8)
        self.points = []
        self.drawing_complete = False

    def click_event(self, event, x, y, flags, param):
        """Handle mouse events for region drawing"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Add point to the list
            self.points.append((x, y))
            
            # Draw the point on the display image
            cv2.circle(self.display_img, (x, y), 5, (0, 0, 255), -1)
            
            # Draw line connecting points
            if len(self.points) > 1:
                cv2.line(self.display_img, self.points[-2], self.points[-1], (0, 255, 0), 2)
            
            # Update the display
            cv2.imshow('Draw Region', self.display_img)
    
    def draw_region(self):
        """
        Display image and allow user to draw a polygon region by clicking points.
        Press 'q' to complete the region and exit.
        Returns the list of points defining the region.
        """
        # Create a copy of the image for display
        self.display_img = self.image.copy()
        
        # Create window and set mouse callback
        cv2.namedWindow('Draw Region')
        cv2.setMouseCallback('Draw Region', self.click_event)
        
        # Display the image
        cv2.imshow('Draw Region', self.display_img)
        
        # Wait for user to press 'q' to exit
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            # If 'q' is pressed, complete the region
            if key == ord('q'):
                # If we have at least 3 points, close the polygon
                if len(self.points) >= 3:
                    # Draw the closing line
                    cv2.line(self.display_img, self.points[-1], self.points[0], (0, 255, 0), 2)
                    cv2.imshow('Draw Region', self.display_img)
                    cv2.waitKey(100)  # Brief delay to show the completed polygon
                    
                    # Create mask from the polygon
                    points_array = np.array(self.points, np.int32)
                    points_array = points_array.reshape((-1, 1, 2))
                    # Fill the polygon region with 1s (or 255 for full intensity in a binary mask)
                    cv2.fillPoly(self.mask, [points_array], 1)  # Using 1 instead of 255 for binary mask
                    
                    self.drawing_complete = True
                break
        
        # Clean up
        cv2.destroyAllWindows()
        
        return self.points