import time
import random
import multiprocessing

safe_distance = 1.5  # Distance to maintain from objects (meters)
target_size = 600  # Desired bounding box height in pixels
size_tolerance = 10  # Acceptable deviation from the target size in pixels

# Combined score weights
SIZE_WEIGHT = 0.7
CONFIDENCE_WEIGHT = 0.3

def random_exploration(last_time):
    """Randomly move the robot to explore the area."""
    current_time = time.time()

    left_speed = random.randint(20, 40)  # Random speed between 20% and 40%
    right_speed = random.randint(20, 40)  # Random speed between 20% and 40%

    if current_time - last_time > 2:
        if random.random() > 0.5:  # Turn robot randomly
            if random.random() > 0.5:
                print(f"turning right randomly at {right_speed}%")
            # right_speed = -right_speed  # Turn right randomly
            else:
                print(f"turning left randomly at {left_speed}%")
             # left_speed = -left_speed  # Turn left randomly
        last_time = current_time
    return last_time
    
    # movement_mapping_test.move_robot(left_speed, right_speed)
    # movement_mapping_test.stop_robot()

def calculate_combined_score(det):
    """
    Calculate a score for selecting the best bounding box based on size and confidence.
    """
    bbox = det.get_bbox()
    confidence = det.get_confidence()
    size_score = bbox.ymax() - bbox.ymin()  # Bounding box height (proxy for proximity)
    combined_score = SIZE_WEIGHT * size_score + CONFIDENCE_WEIGHT * confidence  # Weighted combination
    return combined_score

def select_target_box(detections):
    """
    Select the best bounding box to track based on combined score.
    """
    return max(detections, key=lambda det: calculate_combined_score(det))

def cautious_approach(detections):
    """Align and adjust movement based on bounding boxes."""
    print("Cautious approach started")
    frame_center = 500

    while True:
        # Process the detections
        target = select_target_box(detections)
        bbox = target.get_bbox()
        center_x = (bbox.xmin() + bbox.xmax()) / 2
        error_x = center_x - frame_center
        box_height = bbox.ymax() - bbox.ymin()

        if abs(error_x) > 10:
            turn_speed = min(max(abs(error_x) * 0.1, 10), 50)
            print("Turning", "right" if error_x > 0 else "left", f"speed={turn_speed}")
        elif abs(box_height - target_size) > size_tolerance:
            print("Adjusting distance", "closer" if box_height < target_size else "further")
        else:
            print("Object centered and at desired size. Stopping.")
        time.sleep(0.1)