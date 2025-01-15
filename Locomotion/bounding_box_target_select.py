import time
import random
import Locomotion.bounding_box_motor_control
import multiprocessing

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
            print("turning right randomly")
            #right_speed = -right_speed  # Turn right randomly
        else:
            print("turning left randomly")
            #left_speed = -left_speed  # Turn left randomly

    #movement_mapping_test.move_robot(left_speed, right_speed)
    time.sleep(2)  # Move for 2 seconds
    #movement_mapping_test.stop_robot()

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


def cautious_approach(bbox_queue):
    """Align and adjust movement based on bounding boxes."""
    frame_center = 500

    while True:
        detections = []
        while not bbox_queue.empty():
            detections.append(bbox_queue.get())

        if not detections:
            random_exploration()
            continue

        target = select_target_box(detections, frame_center)
        box = target['box']
        center_x = (box[0] + box[2]) / 2
        error_x = center_x - frame_center
        box_height = box[3] - box[1]

        if abs(error_x) > 10:
            turn_speed = min(max(abs(error_x) * 0.1, 10), 50)
            print("Turning", "right" if error_x > 0 else "left", f"speed={turn_speed}")
        elif abs(box_height - target_size) > size_tolerance:
            print("Adjusting distance", "closer" if box_height < target_size else "further")
        else:
            print("Object centered and at desired size. Stopping.")
        time.sleep(0.1)

if __name__ == "__main__":
    bbox_queue = multiprocessing.Queue()
    cautious_approach(bbox_queue)
