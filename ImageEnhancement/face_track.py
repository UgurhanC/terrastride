from picamera2 import Picamera2
import cv2
import time
from ultralytics import YOLO  # Import the YOLO library

# Initialize the YOLO model
model = YOLO("yolov8n.pt")  # Replace 'yolov8n.pt' with the path to your model if custom

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
                bbox = box.xyxy[0].cpu().numpy()  # Get bounding box coordinates
                label = int(box.cls.cpu().numpy())  # Get class label
                confidence = float(box.conf.cpu().numpy())  # Confidence score

                # Draw the bounding box on the frame
                cv2.rectangle(
                    frame,
                    (int(bbox[0]), int(bbox[1])),  # Top-left corner
                    (int(bbox[2]), int(bbox[3])),  # Bottom-right corner
                    (0, 255, 0),  # Green color
                    2  # Thickness
                )

                # Put the label and confidence on the frame
                cv2.putText(
                    frame,
                    f"{label} {confidence:.2f}",
                    (int(bbox[0]), int(bbox[1] - 10)),  # Slightly above the box
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,  # Font size
                    (0, 255, 0),  # Green color
                    2  # Thickness
                )

        # Display the frame
        cv2.imshow("Picamera2 Frame with YOLO Inference", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Clean up resources
    picam2.stop()
    cv2.destroyAllWindows()