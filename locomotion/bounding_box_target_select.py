import time
import random
import locomotion.bounding_box_motor_control

safe_distance = 1.5  # Distance to maintain from objects (meters)
target_size = 110  # Desired bounding box height in pixels
size_tolerance = 50  # Acceptable deviation from the target size in pixels

divide_speed = 1.5

speed = 50
# Combined score weights
SIZE_WEIGHT = 0.7
CONFIDENCE_WEIGHT = 0.3

def random_exploration(last_time=None, move_time=None):
    """
    Randomly move the robot to explore the area:
    - 30% chance to turn.
    - If turning, 50% chance to turn left or right.
    - 40% chance to move forward or backwards.
    - 30 % chance to pause for 3 seconds to scan the area.
    """
    current_time = time.time()
    if last_time is None:
        return current_time
    
    random_number = random.random()

    # Only perform an action if 3 seconds have passed since the last action
    if current_time - last_time > 1:
        # Decide if the robot should turn (30% chance)
        if random_number > 0.7:
            # Decide turning direction (50% chance for left or right)
            if random.random() > 0.5:
                print("Explore - Turning left - explore")
                locomotion.bounding_box_motor_control.move_robot(-speed, speed)  # Turn left
            else:
                print("Explore - Turning right - explore")
                locomotion.bounding_box_motor_control.move_robot(speed, -speed)  # Turn right
            
            # Update the time for the turn
            last_time = time.time()
            if time.time() - last_time > 0.3:  # Turn for 0.3 s
                locomotion.bounding_box_motor_control.stop_robot()  
                return time.time()
        
        elif random_number > 0.2:
            # Move for 1.5 seconds
            if random.random() > 0.2:
                print("Explore - Moving forward")
                locomotion.bounding_box_motor_control.move_robot(-speed, -speed)  # Move forward
            else:
                print("Explore - Moving backward")
                locomotion.bounding_box_motor_control.move_robot(speed, speed) # Move backward

            # Update the time for movement
            last_time = time.time()
            if time.time() - last_time > 1.5:  # Move for 1.5 seconds
                locomotion.bounding_box_motor_control.stop_robot()  # Stop after 1.5 seconds
                return time.time()
            
        else:
            print("Pausing to scan the area")
            locomotion.bounding_box_motor_control.stop_robot() # Pause for 2 seconds
            last_time = time.time()
            if time.time() - last_time > 2:  # Pause for 2 seconds
                return time.time()
            
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
    return (x1, y1, x2 - x1, y2 - y1, x1 + x2)

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
    if not detections:
        return last_time
    
    current_time = time.time()

    if last_time == None:
        last_time = current_time
    frame_center = width / 2
    

    if current_time - last_time > 0.1:
        # Process the detections
        target = select_target_box(detections, width, height)
        bbox = get_coordinates(target, width, height)
        #center_x = (bbox[0] + bbox[2])
        center_x = bbox[4] / 2
        error_x = center_x - frame_center
        box_height = bbox[3] - bbox[1]
        # print("Frame center = {frame_center}")
        # print("Center bbox = {center_x}")
        print(f"Frame center: {frame_center}, Box center: {center_x}, Error: {error_x}")

        if abs(error_x) > 100:
            turn_speed = min(max(abs(error_x) * 0.05, 15), 12)
            if error_x > 0:
                print(f"Approach - Turning right, speed = {turn_speed}")
                locomotion.bounding_box_motor_control.move_robot(-turn_speed, turn_speed)
            else:
                print(f"Approach - Turning left, speed={turn_speed}")
                locomotion.bounding_box_motor_control.move_robot(turn_speed, -turn_speed)
        
        elif abs(box_height - target_size) > size_tolerance:
            if box_height < target_size:
                print("Approach - Adjusting distance closer")
                locomotion.bounding_box_motor_control.move_robot(-speed, -speed)
            else:
                print("Approach - Adjusting distance further")
                locomotion.bounding_box_motor_control.move_robot(speed, speed)

        elif abs(error_x) <= 50 and abs(box_height - target_size) <= size_tolerance:
            print("Approach - Object centered and at desired size. Stopping.")
            locomotion.bounding_box_motor_control.stop_robot()

        last_time = current_time
    return last_time    