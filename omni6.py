import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import tkinter as tk
from tkinter import ttk

# Tire dimensions (Formula 1 tire example, in meters)
tire_outer_radius = 0.33  # Outer radius
tire_inner_radius = 0.18  # Inner radius (increased to show thickness)
tire_width = 0.305        # Width

# Wear parameters
wear_rate = 0.0002
max_wear = tire_outer_radius - tire_inner_radius  # Maximum wear is until inner radius

# Function to create a cylinder
def create_cylinder(radius, width, num_points=100):
    theta = np.linspace(0, 2 * np.pi, num_points)
    z = np.array([-width / 2, width / 2])
    theta_grid, z_grid = np.meshgrid(theta, z)
    x = radius * np.cos(theta_grid)
    y = radius * np.sin(theta_grid)
    z = z_grid
    return x, y, z

# Function to smoothly interpolate between radii
def smooth_radius(z, left_radius, left_middle_radius, right_middle_radius, right_radius, width):
    left_indices = z < -width / 4
    left_middle_indices = (z >= -width / 4) & (z < 0)
    right_middle_indices = (z >= 0) & (z < width / 4)
    right_indices = z >= width / 4

    radius = np.zeros_like(z)
    radius[left_indices] = left_radius
    radius[left_middle_indices] = np.interp(z[left_middle_indices], [-width / 4, 0], [left_radius, left_middle_radius])
    radius[right_middle_indices] = np.interp(z[right_middle_indices], [0, width / 4], [right_middle_radius, right_radius])
    radius[right_indices] = right_radius

    return radius

# Function to draw the tire with gradient wear
def draw_tire(ax, wear, rotation_angle, wear_position, tire_rotation_angle):
    ax.clear()
    
    # Define the four outer radii
    outer_radius_left = tire_outer_radius - wear if wear_position == 'left' else tire_outer_radius
    outer_radius_left_middle = tire_outer_radius - wear if wear_position == 'middle' or wear_position == 'left' else tire_outer_radius
    outer_radius_right_middle = tire_outer_radius - wear if wear_position == 'middle' or wear_position == 'right' else tire_outer_radius
    outer_radius_right = tire_outer_radius - wear if wear_position == 'right' else tire_outer_radius
    
    # Create inner cylinder
    x_inner, y_inner, z_inner = create_cylinder(tire_inner_radius, tire_width)
    
    # Create outer cylinder with dynamic radii
    z = np.linspace(-tire_width / 2, tire_width / 2, x_inner.shape[1])
    radius = smooth_radius(z, outer_radius_left, outer_radius_left_middle, outer_radius_right_middle, outer_radius_right, tire_width)
    
    x_outer = np.zeros_like(x_inner)
    y_outer = np.zeros_like(y_inner)
    
    for i in range(x_outer.shape[1]):
        x_outer[:, i] = radius[i] * np.cos(2 * np.pi * i / x_outer.shape[1])
        y_outer[:, i] = radius[i] * np.sin(2 * np.pi * i / x_outer.shape[1])
    
    # Apply rotation
    x_outer_rot = x_outer * np.cos(tire_rotation_angle) - y_outer * np.sin(tire_rotation_angle)
    y_outer_rot = x_outer * np.sin(tire_rotation_angle) + y_outer * np.cos(tire_rotation_angle)
    x_inner_rot = x_inner * np.cos(tire_rotation_angle) - y_inner * np.sin(tire_rotation_angle)
    y_inner_rot = x_inner * np.sin(tire_rotation_angle) + y_inner * np.cos(tire_rotation_angle)

    # Create the sidewalls
    vertices = []
    for i in range(x_outer.shape[1] - 1):
        # Outer surface
        vertices.append([
            [x_outer_rot[0, i], y_outer_rot[0, i], z_inner[0, 0]],
            [x_outer_rot[1, i], y_outer_rot[1, i], z_inner[1, 0]],
            [x_outer_rot[1, i + 1], y_outer_rot[1, i + 1], z_inner[1, 1]],
            [x_outer_rot[0, i + 1], y_outer_rot[0, i + 1], z_inner[0, 1]]
        ])
        # Inner surface
        vertices.append([
            [x_inner_rot[0, i], y_inner_rot[0, i], z_inner[0, 0]],
            [x_inner_rot[1, i], y_inner_rot[1, i], z_inner[1, 0]],
            [x_inner_rot[1, i + 1], y_inner_rot[1, i + 1], z_inner[1, 1]],
            [x_inner_rot[0, i + 1], y_inner_rot[0, i + 1], z_inner[0, 1]]
        ])
        # Sidewall between outer and inner surfaces
        vertices.append([
            [x_outer_rot[0, i], y_outer_rot[0, i], z_inner[0, 0]],
            [x_inner_rot[0, i], y_inner_rot[0, i], z_inner[0, 0]],
            [x_inner_rot[1, i], y_inner_rot[1, i], z_inner[1, 0]],
            [x_outer_rot[1, i], y_outer_rot[1, i], z_inner[1, 0]]
        ])
        vertices.append([
            [x_outer_rot[0, i + 1], y_outer_rot[0, i + 1], z_inner[0, 1]],
            [x_inner_rot[0, i + 1], y_inner_rot[0, i + 1], z_inner[0, 1]],
            [x_inner_rot[1, i + 1], y_inner_rot[1, i + 1], z_inner[1, 1]],
            [x_outer_rot[1, i + 1], y_outer_rot[1, i + 1], z_inner[1, 1]]
        ])
    
    # Add the outer and inner surfaces
    ax.add_collection3d(Poly3DCollection(vertices, facecolors='grey', linewidths=0.5, edgecolors='black', alpha=0.5))
    
    # Draw the red strip for rotation visibility
    red_strip_z = np.array([-tire_width / 2, tire_width / 2])
    red_strip_x = np.array([outer_radius_left, outer_radius_right])
    red_strip_y = np.array([0, 0])
    red_strip_x_rot = red_strip_x * np.cos(rotation_angle) - red_strip_y * np.sin(rotation_angle)
    red_strip_y_rot = red_strip_x * np.sin(rotation_angle) + red_strip_y * np.cos(rotation_angle)
    ax.plot(red_strip_x_rot, red_strip_y_rot, red_strip_z, color='red', linewidth=5)
    
    ax.set_xlim(-tire_outer_radius - 0.1, tire_outer_radius + 0.1)
    ax.set_ylim(-tire_outer_radius - 0.1, tire_outer_radius + 0.1)
    ax.set_zlim(-tire_width, tire_width)
    ax.view_init(elev=ax.elev, azim=ax.azim)  # Maintain current azimuth and elevation angle for rotation
    ax.set_box_aspect([1, 1, 1])  # Aspect ratio is 1:1:1
    ax.axis('off')

# Animation function
def update(frame, ax, fig, wear, rotation_angle, wear_position, tire_rotation_angle):
    draw_tire(ax, wear[0], rotation_angle[0], wear_position, tire_rotation_angle[0])
    wear[0] += wear_rate
    rotation_angle[0] += 0.1  # Increment the rotation angle
    if wear[0] > max_wear:
        wear[0] = max_wear
    fig.canvas.draw()

# Event handler for mouse rotation
def on_mouse_press(event):
    on_mouse_press.prev_x, on_mouse_press.prev_y = event.x, event.y

def on_mouse_motion(event, fig, ax):
    dx = event.x - on_mouse_press.prev_x
    dy = event.y - on_mouse_press.prev_y
    if event.button == 1:  # Left mouse button
        ax.view_init(elev=ax.elev - dy * 0.1, azim=ax.azim - dx * 0.1)
        fig.canvas.draw()
    on_mouse_press.prev_x, on_mouse_press.prev_y = event.x, event.y

# Initialize
on_mouse_press.prev_x = 0
on_mouse_press.prev_y = 0

# Function to update azimuth from slider
def update_azimuth(val):
    ax.view_init(azim=float(val), elev=ax.elev)
    fig.canvas.draw()

# Function to update elevation from slider
def update_elevation(val):
    ax.view_init(elev=float(val), azim=ax.azim)
    fig.canvas.draw()

# Function to update tire rotation from slider
def update_tire_rotation(val):
    tire_rotation_angle[0] = float(val)
    fig.canvas.draw()

# Main Tkinter window
root = tk.Tk()
root.title("F1 Tire Simulation")

# Create matplotlib figure and axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Bind mouse press and motion events to the figure
fig.canvas.mpl_connect('button_press_event', on_mouse_press)
fig.canvas.mpl_connect('motion_notify_event', lambda event: on_mouse_motion(event, fig, ax))

# Create a horizontal slider to control the azimuth angle
azimuth_slider = ttk.Scale(root, from_=0, to=360, orient='horizontal', command=update_azimuth)
azimuth_slider.set(120)  # Set the initial azimuth angle to match the initial view
azimuth_slider.pack(side=tk.BOTTOM, fill=tk.X)

# Create a vertical slider to control the elevation angle
elevation_slider = ttk.Scale(root, from_=-90, to=90, orient='horizontal', command=update_elevation)
elevation_slider.set(30)  # Set the initial elevation angle to match the initial view
elevation_slider.pack(side=tk.BOTTOM, fill=tk.X)

# Create a slider to control the tire rotation angle
tire_rotation_slider = ttk.Scale(root, from_=0, to=360, orient='horizontal', command=update_tire_rotation)
tire_rotation_slider.set(0)  # Set the initial tire rotation angle
tire_rotation_slider.pack(side=tk.BOTTOM, fill=tk.X)

# Animation control
wear = [0]
rotation_angle = [0]
wear_position = 'left'  # Set wear position to 'left', 'middle', or 'right'
tire_rotation_angle = [0]

ani = FuncAnimation(fig, update, fargs=(ax, fig, wear, rotation_angle, wear_position, tire_rotation_angle), interval=50, repeat=True, cache_frame_data=False)

# Play/Pause functionality
def play():
    ani.event_source.start()

def pause():
    ani.event_source.stop()

button_frame = ttk.Frame(root)
button_frame.pack(side=tk.BOTTOM)

play_button = ttk.Button(button_frame, text="Play", command=play)
play_button.pack(side=tk.LEFT)

pause_button = ttk.Button(button_frame, text="Pause", command=pause)
pause_button.pack(side=tk.LEFT)

# Start Tkinter main loop
tk.mainloop()