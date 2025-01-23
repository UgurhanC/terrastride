import time
import random
import multiprocessing
import locomotion.bounding_box_motor_control

safe_distance = 1.5  # Distance to maintain from objects (meters)
target_size = 100  # Desired bounding box height in pixels
size_tolerance = 100  # Acceptable deviation from the target size in pixels

divide_speed = 1.5

# Combined score weights
SIZE_WEIGHT = 0.7
CONFIDENCE_WEIGHT = 0.3

def random_exploration(last_time):
    """Randomly move the robot to explore the area."""
    last_time=10
    print(last_time)
    current_time = time.time()
    if last_time == None:
        last_time = current_time

    #left_speed = random.randint(20, 40)  # Random speed between 20% and 40%
    #right_speed = random.randint(20, 40)  # Random speed between 20% and 40%

    left_speed = 20
    right_speed = 20

    if current_time - last_time > 2:
        if random.random() > 0.5:  # Turn robot randomly
            if random.random() > 0.5:
                print(f"turning right randomly at {right_speed}%")
                right_speed = -right_speed  # Turn right randomly
            else:
                print(f"turning left randomly at {left_speed}%")
                left_speed = -left_speed  # Turn left randomly
        last_time = current_time
    return last_time
    
    locomotion.bounding_box_motor_control.move_robot(left_speed/divide_speed, right_speed/divide_speed)
    locomotion.bounding_box_motor_control.stop_robot()
def get_coordinates(det, width, height):
    """
    Convert normalized coordinates to pixel coordinates.
    """
    bbox = det.get_bbox()
    x1_norm = bbox.xmin()
    y1_norm = bbox.ymin()
    x2_norm = bbox.xmax()
    y2_norm = bbox.ymax()
    x1 = int(x1_norm * width)
    y1 = int(y1_norm * height)
    x2 = int(x2_norm * width)
    y2 = int(y2_norm * height)
    return (x1, y1, x2 - x1, y2 - y1)

def calculate_combined_score(det, width, height):
    """
    Calculate a score for selecting the best bounding box based on size and confidence.
    """
    bbox = get_coordinates(det, width, height)
    confidence = det.get_confidence()
    size_score = bbox[3] - bbox[1]  # Bounding box height (proxy for proximity)
    combined_score = SIZE_WEIGHT * size_score + CONFIDENCE_WEIGHT * confidence  # Weighted combination
    return combined_score

def select_target_box(detections, width, height):
    """
    Select the best bounding box to track based on combined score.
    """
    return max(detections, key=lambda det: calculate_combined_score(det, width, height))

def cautious_approach(detections, last_time, width, height):
    """Align and adjust movement based on bounding boxes."""
    last_time=10
    print(last_time)

    current_time = time.time()
    if last_time == None:
        last_time = current_time
    frame_center = width / 2
    

    if current_time - last_time > 2:
        # Process the detections
        target = select_target_box(detections, width, height)
        bbox = get_coordinates(target, width, height)
        center_x = (bbox[0] + bbox[2])
        error_x = center_x - frame_center
        box_height = bbox[3] - bbox[1]
        print(frame_center)
        print(center_x)

        if abs(error_x) > 300:
            turn_speed = min(max(abs(error_x) * 0.1, 10), 50)
            if abs(error_x) > 0:
                print("Turning", "right" if error_x > 0 else "left", f"speed={turn_speed}")
                #locomotion.bounding_box_motor_control.move_robot(-turn_speed/divide_speed, turn_speed/divide_speed)
                locomotion.bounding_box_motor_control.move_robot(-15, 15)
            else:
                print("Turning", "left" if error_x > 0 else "left", f"speed={turn_speed}")
                #locomotion.bounding_box_motor_control.move_robot(turn_speed/divide_speed, -turn_speed/divide_speed)
                locomotion.bounding_box_motor_control.move_robot(15, -15)
        
        elif abs(box_height - target_size) > size_tolerance:
            if box_height < target_size:
                print("Adjusting distance", "closer" if box_height < target_size else "further")
                locomotion.bounding_box_motor_control.move_robot(-10, -10)
            else:
                print("Adjusting distance", "closer" if box_height < target_size else "further")
                locomotion.bounding_box_motor_control.move_robot(10, 10)
        else:
            print("Object centered and at desired size. Stopping.")
            locomotion.bounding_box_motor_control.stop_robot()
        last_time = current_time
