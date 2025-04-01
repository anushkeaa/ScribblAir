import numpy as np
import cv2
from collections import deque
import os

#default called trackbar function 
def setValues(x):
   print("")

# Creating the trackbars needed for adjusting the marker colour
cv2.namedWindow("Color detectors")

# Set default values for BLUE COLOR detection
cv2.createTrackbar("Upper Hue", "Color detectors", 130, 180, setValues)  # Upper blue
cv2.createTrackbar("Upper Saturation", "Color detectors", 255, 255, setValues)
cv2.createTrackbar("Upper Value", "Color detectors", 255, 255, setValues)
cv2.createTrackbar("Lower Hue", "Color detectors", 90, 180, setValues)  # Lower blue
cv2.createTrackbar("Lower Saturation", "Color detectors", 50, 255, setValues)
cv2.createTrackbar("Lower Value", "Color detectors", 50, 255, setValues)
cv2.createTrackbar("Brush Size", "Color detectors", 2, 10, setValues)

# Giving different arrays to handle colour points of different colour
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

# These indexes will be used to mark the points in particular arrays of specific colour
blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0

#The kernel to be used for dilation purpose 
kernel = np.ones((5,5),np.uint8)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

# Here is code for Canvas setup
paintWindow = np.zeros((471,636,3)) + 255
paintWindow = cv2.rectangle(paintWindow, (40,1), (140,65), (0,0,0), 2)
paintWindow = cv2.rectangle(paintWindow, (160,1), (255,65), colors[0], -1)
paintWindow = cv2.rectangle(paintWindow, (275,1), (370,65), colors[1], -1)
paintWindow = cv2.rectangle(paintWindow, (390,1), (485,65), colors[2], -1)
paintWindow = cv2.rectangle(paintWindow, (505,1), (600,65), colors[3], -1)

cv2.putText(paintWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 2, cv2.LINE_AA)
cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

# Add save button
paintWindow = cv2.rectangle(paintWindow, (40, 70), (140, 120), (0, 255, 255), -1)
cv2.putText(paintWindow, "SAVE", (65, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)

# Function to save the canvas
def save_canvas(window):
    # Create a copy of the window to add watermark before saving
    save_copy = window.copy()
    add_watermark(save_copy)
    
    filename = f"air_canvas_{len([f for f in os.listdir('.') if f.startswith('air_canvas_')])}.jpg"
    cv2.imwrite(filename, save_copy)
    print(f"Canvas saved as {filename}")

# Function to add watermark
def add_watermark(image):
    h, w = image.shape[:2]
    watermark_text = "Made by Anushka 2025 - All Rights Reserved"
    # Set watermark properties - position at bottom right with semi-transparency
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    color = (100, 100, 100)  # Gray color
    
    # Get text size to position it properly
    text_size = cv2.getTextSize(watermark_text, font, font_scale, thickness)[0]
    
    # Position at bottom right with some padding
    position = (w - text_size[0] - 10, h - 20)
    
    # Add the text to the image
    cv2.putText(image, watermark_text, position, font, font_scale, color, thickness, cv2.LINE_AA)
    return image

# Loading the default webcam of PC.
cap = cv2.VideoCapture(0)

# Keep looping
while True:
    # Reading the frame from the camera
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break
        
    # Flipping the frame to see same side of yours
    frame = cv2.flip(frame, 1)
    
    # Get brush size
    brush_size = cv2.getTrackbarPos("Brush Size", "Color detectors")
    if brush_size < 1:
        brush_size = 1

    # Add save button to frame
    frame = cv2.rectangle(frame, (40, 70), (140, 120), (0, 255, 255), -1)
    cv2.putText(frame, "SAVE", (65, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Get HSV values
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    u_hue = cv2.getTrackbarPos("Upper Hue", "Color detectors")
    u_saturation = cv2.getTrackbarPos("Upper Saturation", "Color detectors")
    u_value = cv2.getTrackbarPos("Upper Value", "Color detectors")
    l_hue = cv2.getTrackbarPos("Lower Hue", "Color detectors")
    l_saturation = cv2.getTrackbarPos("Lower Saturation", "Color detectors")
    l_value = cv2.getTrackbarPos("Lower Value", "Color detectors")
    Upper_hsv = np.array([u_hue, u_saturation, u_value])
    Lower_hsv = np.array([l_hue, l_saturation, l_value])
    
    # Identifying the pointer by making its mask
    Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
    
    # Adding the color buttons to the live frame
    frame = cv2.rectangle(frame, (40,1), (140,65), (122,122,122), -1)
    frame = cv2.rectangle(frame, (160,1), (255,65), colors[0], -1)
    frame = cv2.rectangle(frame, (275,1), (370,65), colors[1], -1)
    frame = cv2.rectangle(frame, (390,1), (485,65), colors[2], -1)
    frame = cv2.rectangle(frame, (505,1), (600,65), colors[3], -1)
    
    cv2.putText(frame, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 2, cv2.LINE_AA)
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((5,5), np.uint8)
    Mask = cv2.erode(Mask, kernel, iterations=1)
    Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
    Mask = cv2.dilate(Mask, kernel, iterations=2)  # Increased dilation to detect better
    
    # Find contours for the pointer
    cnts, _ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    # If contours are formed
    if len(cnts) > 0:
        # Find the largest contour
        cnt = max(cnts, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        
        # Only use contours with significant area
        if area > 100:  # Lowered threshold to detect smaller blue objects
            # Calculate the centroid of the contour
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            else:
                # If moments calculation fails, use the center of the bounding rect
                x, y, w, h = cv2.boundingRect(cnt)
                center = (int(x + w/2), int(y + h/2))
            
            # Draw a circle at the center point
            cv2.circle(frame, center, 10, (0, 0, 255), -1)
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)

            # Now checking if the user wants to click on any button above the screen 
            if center[1] <= 65:
                if 40 <= center[0] <= 140: # Clear Button
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]

                    blue_index = 0
                    green_index = 0
                    red_index = 0
                    yellow_index = 0

                    paintWindow[67:,:,:] = 255
                elif 160 <= center[0] <= 255:
                        colorIndex = 0 # Blue
                elif 275 <= center[0] <= 370:
                        colorIndex = 1 # Green
                elif 390 <= center[0] <= 485:
                        colorIndex = 2 # Red
                elif 505 <= center[0] <= 600:
                        colorIndex = 3 # Yellow
            # Check for save button click
            elif 40 <= center[0] <= 140 and 70 <= center[1] <= 120:
                save_canvas(paintWindow)
            else:
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(center)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(center)
    # Append new deques when nothing is detected
    else:
        bpoints.append(deque(maxlen=512))
        blue_index += 1
        gpoints.append(deque(maxlen=512))
        green_index += 1
        rpoints.append(deque(maxlen=512))
        red_index += 1
        ypoints.append(deque(maxlen=512))
        yellow_index += 1

    # Draw lines of all the colors on the canvas and frame 
    points = [bpoints, gpoints, rpoints, ypoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], brush_size)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], brush_size)
    
    # Draw the current position if detected
    if center:
        cv2.putText(frame, f"Position: {center}", (10, 440), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    # Add watermark to the displayed frame and paintWindow
    frame_copy = frame.copy()
    paint_copy = paintWindow.copy()
    add_watermark(frame_copy)
    add_watermark(paint_copy)

    # Show all the windows
    cv2.imshow("Tracking", frame_copy)
    cv2.imshow("Paint", paint_copy)
    cv2.imshow("Mask", Mask)

    # Key handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):  # Save with 's' key
        save_canvas(paintWindow)

# Release the camera and all resources
cap.release()
cv2.destroyAllWindows()
