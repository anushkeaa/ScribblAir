import cv2
import numpy as np
import os
import time

def main():
    """
    BLUE OBJECT DRAWING APP
    Detects blue objects and allows you to draw with them
    """
    print("\n*** BLUE OBJECT DRAWING APP ***")
    print("-----------------------------------------")
    print("SETUP:")
    print("1. Use a blue object (pen cap, marker, tape, etc.)")
    print("2. Hold it in front of the camera")
    print("3. Adjust the sliders to detect your blue object")
    print("4. Press SPACE to start drawing")
    print("-----------------------------------------")
    print("CONTROLS:")
    print("  Space: Toggle drawing on/off")
    print("  c: Clear the canvas")
    print("  s: Save the drawing")
    print("  r/g/b/k: Change color to red/green/blue/black")
    print("  q: Quit")
    print("-----------------------------------------")
    
    # Initialize the webcam
    camera = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not camera.isOpened():
        print("Error: Could not open camera")
        return
    
    # Get the first frame and create a canvas of the same size
    ret, frame = camera.read()
    if not ret:
        print("Error: Could not read from camera")
        camera.release()
        return
    
    height, width = frame.shape[:2]
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # White canvas
    
    # Variables for drawing
    drawing = False
    prev_pos = None
    draw_color = (0, 0, 0)  # Black
    thickness = 5
    
    # Create control windows
    cv2.namedWindow("Blue Detection Controls")
    # Default values optimized for blue detection
    cv2.createTrackbar("Blue Hue Min", "Blue Detection Controls", 90, 179, lambda x: None)  # Lower range of blue
    cv2.createTrackbar("Blue Hue Max", "Blue Detection Controls", 130, 179, lambda x: None)  # Upper range of blue
    cv2.createTrackbar("Saturation Min", "Blue Detection Controls", 50, 255, lambda x: None)
    cv2.createTrackbar("Value Min", "Blue Detection Controls", 50, 255, lambda x: None)
    cv2.createTrackbar("Brush Size", "Blue Detection Controls", thickness, 20, lambda x: None)
    
    # Main loop
    while True:
        # Read the current frame from the webcam
        ret, frame = camera.read()
        if not ret:
            break
        
        # Flip the frame horizontally for more intuitive drawing
        frame = cv2.flip(frame, 1)
        display = frame.copy()
        
        # Get settings from trackbars
        hue_min = cv2.getTrackbarPos("Blue Hue Min", "Blue Detection Controls")
        hue_max = cv2.getTrackbarPos("Blue Hue Max", "Blue Detection Controls")
        sat_min = cv2.getTrackbarPos("Saturation Min", "Blue Detection Controls")
        val_min = cv2.getTrackbarPos("Value Min", "Blue Detection Controls")
        thickness = cv2.getTrackbarPos("Brush Size", "Blue Detection Controls")
        if thickness < 1:
            thickness = 1
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define blue color range
        lower_blue = np.array([hue_min, sat_min, val_min])
        upper_blue = np.array([hue_max, 255, 255])
        
        # Create a mask for blue detection
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.medianBlur(mask, 5)
        
        # Find contours
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the blue object position
        curr_pos = None
        
        if contours:
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # Only use contours with minimum area to avoid noise
            if area > 100:
                # Calculate the center of the contour
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    curr_pos = (cx, cy)
                    
                    # Draw the contour and center point
                    cv2.drawContours(display, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.circle(display, curr_pos, 10, (0, 0, 255), -1)
        
        # Draw on the canvas if enabled
        if drawing and curr_pos:
            if prev_pos:
                cv2.line(canvas, prev_pos, curr_pos, draw_color, thickness)
            prev_pos = curr_pos
        elif not drawing:
            prev_pos = None
        
        # Show the drawing on the display with transparency
        mask_draw = (canvas != 255).any(axis=2)
        combined = display.copy()
        combined[mask_draw] = cv2.addWeighted(display[mask_draw], 0.3, canvas[mask_draw], 0.7, 0)[mask_draw]
        
        # Add status information
        cv2.putText(combined, f"Drawing: {'ON' if drawing else 'OFF'}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show position info if detected
        if curr_pos:
            cv2.putText(combined, f"Position: {curr_pos}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show windows
        cv2.imshow("Blue Object Drawing", combined)
        cv2.imshow("Blue Detection", mask)
        cv2.imshow("Canvas", canvas)
        
        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):  # Quit
            break
        elif key == ord('c'):  # Clear canvas
            canvas = np.ones((height, width, 3), dtype=np.uint8) * 255
            print("Canvas cleared")
        elif key == ord('s'):  # Save drawing
            filename = f"drawing_{int(time.time())}.jpg"
            cv2.imwrite(filename, canvas)
            print(f"Drawing saved as {filename}")
        elif key == ord(' '):  # Toggle drawing
            drawing = not drawing
            prev_pos = None  # Reset the previous position
            print(f"Drawing {'enabled' if drawing else 'disabled'}")
        elif key == ord('r'):  # Change to red
            draw_color = (0, 0, 255)  # BGR for red
            print("Color changed to red")
        elif key == ord('g'):  # Change to green
            draw_color = (0, 255, 0)  # BGR for green
            print("Color changed to green")
        elif key == ord('b'):  # Change to blue
            draw_color = (255, 0, 0)  # BGR for blue
            print("Color changed to blue")
        elif key == ord('k'):  # Change to black
            draw_color = (0, 0, 0)  # BGR for black
            print("Color changed to black")
    
    # Release resources
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
