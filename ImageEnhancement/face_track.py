from picamera2 import Picamera2
import cv2
import time
from ultralytics import YOLO  # Import the YOLO library

# Initialize the YOLO model
model = YOLO("yolo11n.pt")  # Replace 'yolov8n.pt' with the path to your model if custom

# Initialize the Picamera2
picam2 = Picamera2()

# Configure the camera for preview
camera_config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(camera_config)

# Start the camera
picam2.start()
time.sleep(2)  # Allow the camera to warm up

try:
    while True:
        # Capture a frame as a NumPy array
        frame = picam2.capture_array()

        # Perform inference on the frame
        results_15 = model(frame, classes=[15])  # Inference for class 15
        results_0 = model(frame, classes=[0])   # Inference for class 0

        # Combine results or process them as needed
        results = results_15 + results_0  # Assuming results can be concatenated

        # Draw bounding boxes and labels on the frame
        for result in results:
            # Assuming YOLO results contain bounding boxes and labels
            for box in result.boxes:
                confidence = box.conf[0]
                if confidence > 0.4:
                    x1, y1, x2, y2 = map(int,box.xyxy[0].tolist())
                    class_id = int(box.cls[0])
                    label = model.names[class_id]
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    cv2.putText(frame, f"{label} {confidence:.2f}",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Picamera2 Frame with YOLO Inference", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Clean up resources
    picam2.stop()
    cv2.destroyAllWindows()
