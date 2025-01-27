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

def random_exploration(last_time=None):
    """
    Randomly move the robot to explore the area:
    - 50% chance to turn.
    - If turning, 50% chance to turn left or right.
    - After turning, move forward for 1.5 seconds.
    - Pause for 3 seconds to scan the area.
    """
    current_time = time.time()
    if last_time is None:
        last_time = current_time

    # Only perform an action if 3 seconds have passed since the last action
    if current_time - last_time > 3:
        # Decide if the robot should turn (50% chance)
        if random.random() > 0.5:
            # Decide turning direction (50% chance for left or right)
            if random.random() > 0.5:
                print("Turning left")
                locomotion.bounding_box_motor_control.move_robot(-20, 20)  # Turn left
            else:
                print("Turning right")
                locomotion.bounding_box_motor_control.move_robot(20, -20)  # Turn right
            
            # Turn for a short duration
            time.sleep(1)  # Turn for 1 second
            locomotion.bounding_box_motor_control.stop_robot()
        
        # Move forward for 1.5 seconds
        print("Moving forward after turn")
        locomotion.bounding_box_motor_control.move_robot(20, 20)  # Move forward
        time.sleep(1.5)
        locomotion.bounding_box_motor_control.stop_robot()

        # Pause for 3 seconds to "scan" the area
        print("Pausing to scan the area")
        time.sleep(3)

        # Update the last action time
        last_time = time.time()
        
        # locomotion.bounding_box_motor_control.move_robot(left_speed/divide_speed, right_speed/divide_speed)
        # time.sleep(5)
        # locomotion.bounding_box_motor_control.stop_robot()

    return last_time

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
            turn_speed = min(max(abs(error_x) * 0.1, 20), 35)
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
                locomotion.bounding_box_motor_control.move_robot(-20, -20)
            else:
                print("Adjusting distance", "closer" if box_height < target_size else "further")
                locomotion.bounding_box_motor_control.move_robot(20, 20)
        else:
            print("Object centered and at desired size. Stopping.")
            locomotion.bounding_box_motor_control.stop_robot()
        last_time = current_time
