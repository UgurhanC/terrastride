import RPi.GPIO as GPIO
import time

# GPIO Pins (same as your current setup)
# Occupied pins by cam: 2, 4, 6, 14, 3, 5
# GPIO Pins (same as your current setup)
LEFT_MOTOR1_IN1 = 22  # Left Motor 1 Forward
LEFT_MOTOR1_IN2 = 23  # Left Motor 1 Backward
LEFT_MOTOR2_IN1 = 9  # Left Motor 2 Forward
LEFT_MOTOR2_IN2 = 25  # Left Motor 2 Backward
LEFT_PWM = 24         # PWM speed control for left motors

RIGHT_MOTOR1_IN3 = 17  # Right Motor 1 Forward
RIGHT_MOTOR1_IN4 = 27 # Right Motor 1 Backward
RIGHT_MOTOR2_IN3 = 7 # Right Motor 2 Forward
RIGHT_MOTOR2_IN4 = 11  # Right Motor 2 Backward
RIGHT_PWM = 10        # PWM speed control for right motors



# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_MOTOR1_IN1, GPIO.OUT)
GPIO.setup(LEFT_MOTOR1_IN2, GPIO.OUT)
GPIO.setup(LEFT_MOTOR2_IN1, GPIO.OUT)
GPIO.setup(LEFT_MOTOR2_IN2, GPIO.OUT)
GPIO.setup(LEFT_PWM, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR1_IN3, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR1_IN4, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR2_IN3, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR2_IN4, GPIO.OUT)
GPIO.setup(RIGHT_PWM, GPIO.OUT)

# Initialize PWM
left_pwm = GPIO.PWM(LEFT_PWM, 100)  # Frequency at 100 Hz
right_pwm = GPIO.PWM(RIGHT_PWM, 100)
left_pwm.start(0)
right_pwm.start(0)

# Function to stop all motors
def stop_all_motors():
    """Stop all motors by setting direction pins to LOW and PWM to 0."""
    print("Stopping all motors...")
    # Stop left motors
    GPIO.output(LEFT_MOTOR1_IN1, GPIO.LOW)
    GPIO.output(LEFT_MOTOR1_IN2, GPIO.LOW)
    GPIO.output(LEFT_MOTOR2_IN1, GPIO.LOW)
    GPIO.output(LEFT_MOTOR2_IN2, GPIO.LOW)
    left_pwm.ChangeDutyCycle(0)
    
    # Stop right motors
    GPIO.output(RIGHT_MOTOR1_IN3, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR1_IN4, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR2_IN3, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR2_IN4, GPIO.LOW)
    right_pwm.ChangeDutyCycle(0)

# Function to test a motor (forward or backward)
def test_motor(pin1, pin2, motor_name, pwm_pin, pwm_name, direction):
    print(f"Testing {motor_name} motor {direction}...")
    
    # Stop all motors before starting the new movement
    stop_all_motors()
    
    if direction == 'f':
        # Move forward
        GPIO.output(pin1, GPIO.HIGH)
        GPIO.output(pin2, GPIO.LOW)
    elif direction == 'b':
        # Move backward
        GPIO.output(pin1, GPIO.LOW)
        GPIO.output(pin2, GPIO.HIGH)
    
    pwm_pin.ChangeDutyCycle(50)  # Adjust speed to 50% for visibility
    time.sleep(2)  # Motor should run for 2 seconds
    
    # Stop motor
    stop_all_motors()
    print(f"Stopped {motor_name} motor.")

# Main loop for testing motors via user input
def motor_test():
    while True:
        # Get input command
        user_input = input("Enter motor command (e.g. r1f for Right Motor 1 Forward, l2b for Left Motor 2 Backward, or 'exit' to quit): ").lower()
        
        if user_input == 'exit':
            print("Exiting motor test...")
            break
        
        # Validate and map the user input to the correct motor and direction
        if len(user_input) == 3:
            motor = user_input[0]  # 'r' or 'l' for Right or Left
            motor_num = int(user_input[1])  # 1 or 2 for motor 1 or 2
            direction = user_input[2]  # 'f' for Forward, 'b' for Backward

            if motor == 'r' and motor_num == 1:
                # Right Motor 1
                test_motor(RIGHT_MOTOR1_IN3, RIGHT_MOTOR1_IN4, "Right Motor 1", right_pwm, "Right PWM", direction)
            elif motor == 'r' and motor_num == 2:
                # Right Motor 2
                test_motor(RIGHT_MOTOR2_IN3, RIGHT_MOTOR2_IN4, "Right Motor 2", right_pwm, "Right PWM", direction)
            elif motor == 'l' and motor_num == 1:
                # Left Motor 1
                test_motor(LEFT_MOTOR1_IN1, LEFT_MOTOR1_IN2, "Left Motor 1", left_pwm, "Left PWM", direction)
            elif motor == 'l' and motor_num == 2:
                # Left Motor 2
                test_motor(LEFT_MOTOR2_IN1, LEFT_MOTOR2_IN2, "Left Motor 2", left_pwm, "Left PWM", direction)
            else:
                print("Invalid command! Please enter a valid motor and direction (e.g., r1f, l2b).")
        else:
            print("Invalid command format! Please use the format: r1f, l2b, etc.")

# Start the motor test
motor_test()

# Clean-up GPIO after tests
GPIO.cleanup()
