import cv2
import numpy as np

# Initialize the webcam
cap = cv2.VideoCapture(2)

# Set the width and height of the capture frame
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def process_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply binary threshold to get black line on white background
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # Define the height of the region for "sensors"
    height, width = thresh.shape
    sensor_height = height - 50  # Focus on bottom part for line detection
    
    # Divide the width into 5 regions for sensor zones
    sensor_zones = np.array_split(thresh[sensor_height:, :], 5, axis=1)
    detection = []

    # Detect line presence in each "sensor" zone
    for i, zone in enumerate(sensor_zones):
        # Count black pixels in each zone
        black_pixels = cv2.countNonZero(zone)
        detection.append(black_pixels > 100)  # Threshold for line presence

        # Draw rectangle on the original frame for visualization
        color = (0, 255, 0) if detection[i] else (0, 0, 255)
        cv2.rectangle(frame, 
                      (i * width // 5, sensor_height), 
                      ((i + 1) * width // 5, height), 
                      color, 2)

    # Decide action based on which sensors detect the black line
    if detection[0] or detection[1]:   # Line is on the left
        direction = "Turn Left"
    elif detection[3] or detection[4]: # Line is on the right
        direction = "Turn Right"
    elif detection[2]:                 # Line is centered
        direction = "Go Straight"
    else:
        direction = "Searching Line"

    # Display direction
    cv2.putText(frame, direction, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return frame
                              
# Main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Process the frame to detect line and direction
    processed_frame = process_frame(frame)

    # Display the result
    cv2.imshow("Line Follower", processed_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
