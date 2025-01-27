import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
PAN_PIN = 17  # GPIO pin for pan servo
TILT_PIN = 18  # GPIO pin for tilt servo

GPIO.setup(PAN_PIN, GPIO.OUT)
GPIO.setup(TILT_PIN, GPIO.OUT)

pan_servo = GPIO.PWM(PAN_PIN, 50)  # 50Hz PWM
tilt_servo = GPIO.PWM(TILT_PIN, 50)

pan_servo.start(7.5)  # Neutral position
tilt_servo.start(7.5)

def set_angle(servo, angle):
    duty = 2 + (angle / 18)  # Convert angle to duty cycle
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Allow time to move
    servo.ChangeDutyCycle(0)  # Stop signal to prevent jitter

# Example usage
set_angle(pan_servo, 90)  # Pan to 90°
set_angle(tilt_servo, 45)  # Tilt to 45°

pan_servo.stop()
tilt_servo.stop()
GPIO.cleanup()
