import cv2
from ultralytics import YOLO

# Load the YOLO model
model = YOLO("yolo11n.pt") 

# Open the camera
cap = cv2.VideoCapture(0)  # 0 for default camera

# Open a CSV file to save results
# Loop to process frames from the camera
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    # Perform inference on the frame
    results = model(frame, classes=[15])

    # Draw bounding boxes and labels on the frame
    for result in results:
        for box in result.boxes:
            confidence = box.conf[0]
            if confidence > 0.4:  # Confidence threshold
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_id = int(box.cls[0])  # Class ID
                label = model.names[class_id]

                # Draw the bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Display label and confidence
                cv2.putText(frame, f"{label} {confidence:.2f}", 
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    # Display the frame with bounding boxes
    cv2.imshow("YOLO Camera Feed", frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()