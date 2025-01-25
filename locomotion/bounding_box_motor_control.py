
import RPi.GPIO as GPIO
import time

# Robot parameters
WHEEL_RADIUS = 0.035  # 3.5 cm
WHEELBASE_WIDTH = 0.15  # 15 cm distance between left and right wheels

# GPIO Pins
# Left side motors
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

def move_robot(left_speed, right_speed):
    """
    Control the robot motors using GPIO pins based on left and right speed percentages.
    """
    print("robot moving")
    left_duty_cycle = max(min(left_speed, 100), -100) / 100.0
    right_duty_cycle = max(min(right_speed, 100), -100) / 100.0

    # Left motors direction control
    if left_duty_cycle > 0:
        # Forward direction for left motors
        GPIO.output(LEFT_MOTOR1_IN1, GPIO.HIGH)
        GPIO.output(LEFT_MOTOR1_IN2, GPIO.LOW)
        GPIO.output(LEFT_MOTOR2_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR2_IN2, GPIO.HIGH)
    else:
        # Backward direction for left motors
        GPIO.output(LEFT_MOTOR1_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR1_IN2, GPIO.HIGH)
        GPIO.output(LEFT_MOTOR2_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR2_IN2, GPIO.HIGH)

    # Right motors direction control
    if right_duty_cycle > 0:
        # Forward direction for right motors
        GPIO.output(RIGHT_MOTOR1_IN3, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR1_IN4, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR2_IN3, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR2_IN4, GPIO.LOW)
    else:
        # Backward direction for right motors
        GPIO.output(RIGHT_MOTOR1_IN3, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR1_IN4, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR2_IN3, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR2_IN4, GPIO.HIGH)

    # Adjust PWM for speed
    left_pwm.ChangeDutyCycle(abs(left_duty_cycle * 100))
    right_pwm.ChangeDutyCycle(abs(right_duty_cycle * 100))


def stop_robot():
    """
    Stop the robot by setting all GPIO outputs to low.
    """
    print("robot stopping")
    GPIO.output(LEFT_MOTOR1_IN1, GPIO.LOW)
    GPIO.output(LEFT_MOTOR1_IN2, GPIO.LOW)
    GPIO.output(LEFT_MOTOR2_IN1, GPIO.LOW)
    GPIO.output(LEFT_MOTOR2_IN2, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR1_IN3, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR1_IN4, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR2_IN3, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR2_IN4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(0)
    right_pwm.ChangeDutyCycle(0)

if __name__ == "__main__":
    try:
        print("Robot ready to receive movement commands.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping robot...")
        stop_robot()
    finally:
        GPIO.cleanup()
