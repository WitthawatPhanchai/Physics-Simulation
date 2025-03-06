import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

# Initialize figure and axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]})
plt.subplots_adjust(left=0.15, bottom=0.25)
fig.suptitle('Simple Harmonic Motion Simulation', fontsize=16)

# Parameters
mass = 1.0  # kg
k = 10.0    # N/m
amplitude = 1.0  # m
damping = 0.1    # damping coefficient
g = 9.8    # m/s^2

# Time parameters
t = np.linspace(0, 10, 1000)
dt = t[1] - t[0]
interval = 20  # Animation interval in ms

# Calculate important values
omega = np.sqrt(k/mass)  # angular frequency
period = 2*np.pi/omega   # period
frequency = 1/period     # frequency

# Calculate position as a function of time (with optional damping)
def x_position(t, A, m, k, c):
    omega = np.sqrt(k/m)
    if c == 0:
        return A * np.cos(omega * t)
    else:
        gamma = c/(2*m)
        omega_d = np.sqrt(omega**2 - gamma**2) if omega**2 > gamma**2 else 0
        if omega_d > 0:
            return A * np.exp(-gamma * t) * np.cos(omega_d * t)
        else:
            return A * np.exp(-gamma * t)  # overdamped case

# Set up the plots
positions = x_position(t, amplitude, mass, k, damping)
time_line, = ax2.plot(t, positions, 'b-')
spring_line, = ax1.plot([], [], 'k-', linewidth=3)
mass_point, = ax1.plot([], [], 'ro', markersize=20)
wall, = ax1.plot([-2, -2], [-2, 2], 'k-', linewidth=6)

# Set up the coordinate system
ax1.set_xlim(-3, 3)
ax1.set_ylim(-2, 2)
ax1.set_aspect('equal')
ax1.grid(True)
ax1.set_title('Spring-Mass System')
ax1.set_xlabel('Position (m)')
ax1.set_yticks([])

ax2.set_xlim(0, 10)
ax2.set_ylim(-1.5, 1.5)
ax2.grid(True)
ax2.set_title('Position vs Time')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Position (m)')

# Add a vertical line on the time plot to show current time
time_marker, = ax2.plot([], [], 'r-')

# Spring properties
def spring_points(x, coils=10, width=0.5):
    pts_per_coil = 20
    x_points = np.linspace(-2, x, coils * pts_per_coil)
    y_points = np.zeros_like(x_points)
    
    # First and last 10% of points are straight
    coil_start = int(0.1 * len(x_points))
    coil_end = int(0.9 * len(x_points))
    
    # Middle points form the coil
    coil_indices = np.arange(coil_start, coil_end)
    coil_x = np.linspace(x_points[coil_start], x_points[coil_end], len(coil_indices))
    y_points[coil_indices] = width * np.sin(2 * np.pi * np.arange(len(coil_indices)) / pts_per_coil)
    x_points[coil_indices] = coil_x
    
    return x_points, y_points

# Animation function
def animate(i):
    current_t = (i * interval/1000) % 10
    idx = int(current_t / dt)
    if idx >= len(positions):
        idx = 0
    
    current_x = positions[idx]
    
    # Update spring
    x_spring, y_spring = spring_points(current_x)
    spring_line.set_data(x_spring, y_spring)
    
    # Update mass
    mass_point.set_data([current_x], [0])
    
    # Update time marker
    time_marker.set_data([current_t, current_t], [-1.5, 1.5])
    
    return spring_line, mass_point, time_marker

# Create sliders
ax_mass = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_k = plt.axes([0.25, 0.1, 0.65, 0.03])
ax_amplitude = plt.axes([0.25, 0.05, 0.65, 0.03])
ax_damping = plt.axes([0.25, 0.0, 0.65, 0.03])

s_mass = Slider(ax_mass, 'Mass (kg)', 0.1, 5.0, valinit=mass)
s_k = Slider(ax_k, 'Spring Constant (N/m)', 1.0, 30.0, valinit=k)
s_amplitude = Slider(ax_amplitude, 'Amplitude (m)', 0.1, 2.0, valinit=amplitude)
s_damping = Slider(ax_damping, 'Damping', 0.0, 1.0, valinit=damping)

# Update function for parameter changes
def update(val):
    new_mass = s_mass.val
    new_k = s_k.val
    new_amplitude = s_amplitude.val
    new_damping = s_damping.val
    
    # Recalculate position data
    global positions
    positions = x_position(t, new_amplitude, new_mass, new_k, new_damping)
    
    # Update the time plot
    time_line.set_ydata(positions)
    
    # Update frequency text
    new_omega = np.sqrt(new_k/new_mass)
    new_period = 2*np.pi/new_omega
    new_frequency = 1/new_period
    
    # Update the y-axis limits based on amplitude
    ax2.set_ylim(-new_amplitude*1.5, new_amplitude*1.5)
    
    fig.canvas.draw_idle()

# Connect the sliders to the update function
s_mass.on_changed(update)
s_k.on_changed(update)
s_amplitude.on_changed(update)
s_damping.on_changed(update)

# Add Reset button
reset_ax = plt.axes([0.8, 0.20, 0.1, 0.04])
reset_button = Button(reset_ax, 'Reset', color='lightgoldenrodyellow', hovercolor='0.975')

def reset(event):
    s_mass.reset()
    s_k.reset()
    s_amplitude.reset()
    s_damping.reset()
    
reset_button.on_clicked(reset)

# Add text information
params_ax = plt.axes([0.15, 0.2, 0.3, 0.04])
params_ax.axis('off')
omega = np.sqrt(k/mass)
period = 2*np.pi/omega
frequency = 1/period
params_text = params_ax.text(0, 0, f"ω = {omega:.2f} rad/s\nPeriod = {period:.2f} s\nFrequency = {frequency:.2f} Hz", fontsize=10)

def update_text(val=None):
    new_mass = s_mass.val
    new_k = s_k.val
    new_omega = np.sqrt(new_k/new_mass)
    new_period = 2*np.pi/new_omega
    new_frequency = 1/new_period
    params_text.set_text(f"ω = {new_omega:.2f} rad/s\nPeriod = {new_period:.2f} s\nFrequency = {new_frequency:.2f} Hz")

s_mass.on_changed(update_text)
s_k.on_changed(update_text)
update_text()  # Initial update

# Create animation
ani = FuncAnimation(fig, animate, frames=500, interval=interval, blit=True)

plt.show()
