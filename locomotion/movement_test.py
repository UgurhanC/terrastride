from bounding_box_motor_control import *
import time

#GPIO.cleanup()
move_robot(20, 20)
time.sleep(5)
move_robot(-20, -20)
time.sleep(5)