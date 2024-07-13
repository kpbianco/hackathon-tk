# Function to draw the tire
# Function to draw the tire with gradient wear
# Function to draw the tire with gradient wear
def draw_tire(ax, wear, rotation_angle, wear_position, tire_rotation_angle):
    ax.clear()
    current_outer_radius = tire_outer_radius - wear
    if current_outer_radius < tire_inner_radius:
        current_outer_radius = tire_inner_radius
    
    # Create outer cylinder
    x_outer, y_outer, z_outer = create_cylinder(current_outer_radius, tire_width)
    
    # Create inner cylinder
    x_inner, y_inner, z_inner = create_cylinder(tire_inner_radius, tire_width)
    
    # Apply rotation
    x_outer_rot = x_outer * np.cos(tire_rotation_angle) - y_outer * np.sin(tire_rotation_angle)
    y_outer_rot = x_outer * np.sin(tire_rotation_angle) + y_outer * np.cos(tire_rotation_angle)
    x_inner_rot = x_inner * np.cos(tire_rotation_angle) - y_inner * np.sin(tire_rotation_angle)
    y_inner_rot = x_inner * np.sin(tire_rotation_angle) + y_inner * np.cos(tire_rotation_angle)

    # Adjust wear position
    z_outer_wear = z_outer.copy()
    num_points = z_outer.shape[1]
    if wear_position == 'left':
        gradient = np.linspace(0, wear, num_points // 2)
        z_outer_wear[:, :num_points // 2] -= gradient
    elif wear_position == 'right':
        gradient = np.linspace(0, wear, num_points // 2)
        z_outer_wear[:, num_points // 2:] -= gradient[::-1]
    elif wear_position == 'middle':
        middle_start = num_points // 4
        middle_end = 3 * num_points // 4
        gradient = np.linspace(0, wear, middle_end - middle_start)
        z_outer_wear[:, middle_start:middle_end] -= gradient

    # Create the sidewalls
    vertices = []
    for i in range(x_outer.shape[1] - 1):
        # Outer surface
        vertices.append([
            [x_outer_rot[0, i], y_outer_rot[0, i], z_outer_wear[0, 0]],
            [x_outer_rot[1, i], y_outer_rot[1, i], z_outer_wear[1, 0]],
            [x_outer_rot[1, i + 1], y_outer_rot[1, i + 1], z_outer_wear[1, 1]],
            [x_outer_rot[0, i + 1], y_outer_rot[0, i + 1], z_outer_wear[0, 1]]
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
            [x_outer_rot[0, i], y_outer_rot[0, i], z_outer_wear[0, 0]],
            [x_inner_rot[0, i], y_inner_rot[0, i], z_inner[0, 0]],
            [x_inner_rot[1, i], y_inner_rot[1, i], z_inner[1, 0]],
            [x_outer_rot[1, i], y_outer_rot[1, i], z_outer_wear[1, 0]]
        ])
        vertices.append([
            [x_outer_rot[0, i + 1], y_outer_rot[0, i + 1], z_outer_wear[0, 1]],
            [x_inner_rot[0, i + 1], y_inner_rot[0, i + 1], z_inner[0, 1]],
            [x_inner_rot[1, i + 1], y_inner_rot[1, i + 1], z_inner[1, 1]],
            [x_outer_rot[1, i + 1], y_outer_rot[1, i + 1], z_outer_wear[1, 1]]
        ])
    
    # Add the outer and inner surfaces
    ax.add_collection3d(Poly3DCollection(vertices, facecolors='grey', linewidths=0.5, edgecolors='black', alpha=0.5))
    
    # Draw the red strip for rotation visibility
    red_strip_z = np.array([-tire_width / 2, tire_width / 2])
    red_strip_x = np.array([current_outer_radius, tire_inner_radius])
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

# Initialize previous mouse position
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

