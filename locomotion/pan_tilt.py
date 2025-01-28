import smbus
import time

# Set the I2C address of your ArduCAM controller
I2C_ADDRESS = 0x0C  # Replace with the actual I2C address of your device

# Initialize the I2C bus (1 is for Raspberry Pi, change if using a different platform)
bus = smbus.SMBus(1)

# Define function to send a command to the controller
def send_command(register, value):
    bus.write_byte_data(I2C_ADDRESS, register, value)

# Define function to read a register from the controller
def read_register(register):
    return bus.read_byte_data(I2C_ADDRESS, register)

# Example: Command to set pan and tilt angles (these are hypothetical commands)
# Replace with actual registers and values for your controller

# Set pan angle (replace with actual register and value)
send_command(0x03, 180)  # Replace with correct register for pan angle

# Set tilt angle (replace with actual register and value)
send_command(0x04, 180)  # Replace with correct register for tilt angle

# Optional: Read back a value to check status (if your controller supports it)
status = read_register(0x07)  # Hypothetical register for status
print(f"Controller Status: {status}")

# Wait a bit before exiting
time.sleep(1)
