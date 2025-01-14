import time
import random
import bounding_box_motor_control

safe_distance = 1.5  # Distance to maintain from objects (meters)
target_size = 600  # Desired bounding box height in pixels
size_tolerance = 10  # Acceptable deviation from the target size in pixels

# Combined score weights
SIZE_WEIGHT = 0.7
CONFIDENCE_WEIGHT = 0.3

def random_exploration():
    """Randomly move the robot to explore the area."""
    left_speed = random.randint(20, 40)  # Random speed between 20% and 40%
    right_speed = random.randint(20, 40)  # Random speed between 20% and 40%

    if random.random() > 0.5:  # Turn robot randomly
        if random.random() > 0.5:
            right_speed = -right_speed  # Turn right randomly
        else:
            left_speed = -left_speed  # Turn left randomly

    movement_mapping_test.move_robot(left_speed, right_speed)
    time.sleep(2)  # Move for 2 seconds
    movement_mapping_test.stop_robot()

def calculate_combined_score(box, confidence, frame_center):
    """
    Calculate a score for selecting the best bounding box based on size and confidence.
    """
    size_score = box[3] - box[1]  # Bounding box height (proxy for proximity)
    center_score = -abs((box[0] + box[2]) / 2 - frame_center)  # Closer to center is better
    combined_score = SIZE_WEIGHT * size_score + CONFIDENCE_WEIGHT * confidence  # Weighted combination
    return combined_score

def select_target_box(detections, frame_center):
    """
    Select the best bounding box to track based on combined score.
    """
    return max(detections, key=lambda det: calculate_combined_score(det['box'], det['confidence'], frame_center))

def cautious_approach(detections, frame_center):
    """
    Align the bounding box to the frame center and adjust its size.
    """
    if not detections:
        random_exploration()
        return

    # Select the best bounding box
    target_detection = select_target_box(detections, frame_center)
    target_box = target_detection['box']
    box_center_x = (target_box[0] + target_box[2]) / 2  # Center of the target bounding box
    error_x = box_center_x - frame_center
    bounding_box_height = target_box[3] - target_box[1]

    if abs(error_x) > 10:  # Centering threshold
        turn_speed = min(max(abs(error_x) * 0.1, 10), 50)
        if error_x > 0:
            print("Turn right")
            movement_mapping_test.move_robot(-turn_speed, turn_speed)  # Turn right
        else:
            print("Turn left")
            movement_mapping_test.move_robot(turn_speed, -turn_speed)  # Turn left
    elif abs(bounding_box_height - target_size) > size_tolerance:
        # Adjust distance to match target size
        if bounding_box_height < target_size:
            print("Object too far, move forward")
            movement_mapping_test.move_robot(40, 40)  # Move forward
        else:
            print("Object too close, move backward")
            movement_mapping_test.move_robot(-30, -30)  # Move backward
    else:
        movement_mapping_test.stop_robot()  # Stop if within target size and centered

if __name__ == "__main__":
    bounding_boxes = []  # List of detected bounding boxes with confidence scores
    frame_center = 500  # Center of the frame (adjust dynamically if needed)

    while True:
        # Replace with actual detection logic
        # bounding_boxes = get_detections()
        # Each detection should be a dictionary with keys 'box' and 'confidence', e.g.,
        # {'box': [x1, y1, x2, y2], 'confidence': 0.95}
        if bounding_boxes:
            cautious_approach(bounding_boxes, frame_center)
        else:
            random_exploration()
