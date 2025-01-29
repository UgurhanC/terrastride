import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
servo_pin = 3  # GPIO pin 2

GPIO.setup(servo_pin, GPIO.OUT)

# Set up PWM on the servo pin
pwm = GPIO.PWM(servo_pin, 50)  # 50Hz is standard for most servos

# Start PWM with 0% duty cycle (initially stopped)
pwm.start(0)

# Function to set servo position
def set_angle(angle):
    # Convert angle to duty cycle (approximation for most servos)
    duty = angle / 18 + 2
    pwm.ChangeDutyCycle(duty)

# Test the servo by moving it to different angles
try:
    print("Moving servo to 0°")
    set_angle(0)  # Move to 0 degrees
    time.sleep(2)
    
    print("Moving servo to 90°")
    set_angle(90)  # Move to 90 degrees
    time.sleep(2)
    
    print("Moving servo to 180°")
    set_angle(180)  # Move to 180 degrees
    time.sleep(2)
    
    # You can keep testing other angles as needed.
    
except KeyboardInterrupt:
    print("Program interrupted by user.")

# Cleanup
pwm.stop()
GPIO.cleanup()
