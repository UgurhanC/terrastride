import math
import matplotlib.pyplot as plt
import time

# Robot parameters
WHEEL_RADIUS = 0.035  # 3.5 cm 69.8
WHEELBASE_WIDTH = 0.15  # 15 cm distance between left and right wheels
MAX_SPEED = 0.5  # Maximum speed in meters per second at 100% duty cycle

# Initialize robot position and orientation
x, y, theta = 0.0, 0.0, 0.0  # Position (meters) and orientation (radians)

# Trajectory storage for plotting
trajectory = [(x, y)]

# Initialize matplotlib figure
fig, ax = plt.subplots()
line, = ax.plot([], [], marker='o', linestyle='-', label="Robot Path")
ax.set_title("Robot Trajectory")
ax.set_xlabel("X Position (m)")
ax.set_ylabel("Y Position (m)")
ax.axis("equal")
ax.grid()
ax.legend()


def update_plot():
    """Update the plot with the latest trajectory."""
    xs, ys = zip(*trajectory)
    line.set_data(xs, ys)
    ax.relim()
    ax.autoscale_view()
    plt.pause(0.001)  # Add a small delay for smoother real-time updates


def move_robot(left_speed, right_speed, duration):
    """
    - left_speed, right_speed: Speeds of left and right motors (in % of MAX_SPEED)
    - duration: Time in seconds for which the motors run
    """
    global x, y, theta

    # Convert speeds to meters per second
    left_velocity = (left_speed / 100.0) * MAX_SPEED
    right_velocity = (right_speed / 100.0) * MAX_SPEED

    # Calculate linear and angular velocity
    linear_velocity = (left_velocity + right_velocity) / 2.0
    angular_velocity = (right_velocity - left_velocity) / WHEELBASE_WIDTH

    # Update position based on velocities
    distance = linear_velocity * duration
    x += distance * math.cos(theta)
    y += distance * math.sin(theta)
    theta += angular_velocity * duration

    # Save the new position for trajectory plotting
    trajectory.append((x, y))
    update_plot()  # Update the plot after every movement

if __name__ == "__main__":
    plt.ion()  # Enable interactive mode
    print("Mapping robot trajectory in real time...")

    try:
        while True:
            time.sleep(0.1)  # Keep the script running to update the map
    except KeyboardInterrupt:
        print("Stopping mapping...")
    finally:
        plt.ioff()  # Disable interactive mode
        plt.show()  # Keep the plot open after stopping
