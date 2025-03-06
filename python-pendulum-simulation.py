import pygame
import sys
import math
import numpy as np
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants and settings
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (66, 133, 244)
DARK_BLUE = (41, 101, 202)
RED = (255, 0, 0, 128)
GRAY = (200, 200, 200)

# Physics variables
length = 1.0  # meters
gravity = 9.8  # m/s²
dampening = 0.005
angle = math.radians(30)  # Initial angle in radians
angular_velocity = 0.0
angular_acceleration = 0.0
pixels_per_meter = 150  # Scale factor

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Harmonic Pendulum Simulation")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont('Arial', 16)
title_font = pygame.font.SysFont('Arial', 24, bold=True)

# Pivot point (center of screen horizontally, near top vertically)
pivot_x = WIDTH // 2
pivot_y = 100

# Bob properties
bob_radius = 20

# Trail points to track path
trail_points = []
max_trail_points = 100

# Button class for interactive controls
class Button:
    def __init__(self, x, y, width, height, text, color=(76, 175, 80), hover_color=(69, 160, 73)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Slider class for interactive controls
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, step, initial, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_rect = pygame.Rect(x, y - 5, 10, height + 10)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.value = initial
        self.label = label
        self.dragging = False
        self.set_knob_pos()
        
    def set_knob_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.knob_rect.centerx = self.rect.left + ratio * self.rect.width
        
    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=3)
        pygame.draw.rect(surface, BLACK, self.rect, 1, border_radius=3)
        
        # Draw knob
        pygame.draw.rect(surface, BLUE, self.knob_rect, border_radius=5)
        pygame.draw.rect(surface, DARK_BLUE, self.knob_rect, 1, border_radius=5)
        
        # Draw label and value
        label_surf = font.render(f"{self.label}: {self.value:.2f}", True, BLACK)
        label_rect = label_surf.get_rect(bottomleft=(self.rect.left, self.rect.top - 5))
        surface.blit(label_surf, label_rect)
        
    def update(self, pos, is_dragging):
        if is_dragging and self.dragging:
            # Calculate position ratio
            ratio = max(0, min(1, (pos[0] - self.rect.left) / self.rect.width))
            # Convert to value and apply stepping
            raw_value = self.min_val + ratio * (self.max_val - self.min_val)
            # Apply step rounding
            steps = round((raw_value - self.min_val) / self.step)
            self.value = self.min_val + steps * self.step
            # Clamp to range
            self.value = max(self.min_val, min(self.max_val, self.value))
            # Update knob position
            self.set_knob_pos()
            return True
        return False
        
    def check_click(self, pos, is_clicking):
        if is_clicking and self.knob_rect.collidepoint(pos):
            self.dragging = True
            return True
        if not pygame.mouse.get_pressed()[0]:
            self.dragging = False
        return False

# Create buttons
start_button = Button(WIDTH // 2 - 160, HEIGHT - 80, 100, 40, "Start")
pause_button = Button(WIDTH // 2 - 50, HEIGHT - 80, 100, 40, "Pause")
reset_button = Button(WIDTH // 2 + 60, HEIGHT - 80, 100, 40, "Reset")

# Create sliders
length_slider = Slider(WIDTH // 2 - 200, HEIGHT - 180, 400, 10, 0.1, 2.0, 0.1, length, "Length (m)")
gravity_slider = Slider(WIDTH // 2 - 200, HEIGHT - 140, 400, 10, 1.0, 20.0, 0.1, gravity, "Gravity (m/s²)")
dampening_slider = Slider(WIDTH // 2 - 200, HEIGHT - 100, 400, 10, 0.0, 0.1, 0.001, dampening, "Dampening")
angle_slider = Slider(WIDTH // 2 - 200, HEIGHT - 220, 400, 10, 0, 90, 1, math.degrees(angle), "Initial Angle (°)")

# Function to calculate bob position
def get_bob_position():
    bob_x = pivot_x + math.sin(angle) * length * pixels_per_meter
    bob_y = pivot_y + math.cos(angle) * length * pixels_per_meter
    return (bob_x, bob_y)

# Function to update physics
def update_physics(dt):
    global angle, angular_velocity, angular_acceleration
    
    # Calculate angular acceleration (F = ma)
    angular_acceleration = -(gravity / length) * math.sin(angle)
    
    # Apply dampening
    angular_acceleration -= dampening * angular_velocity
    
    # Update angular velocity
    angular_velocity += angular_acceleration * dt
    
    # Update angle
    angle += angular_velocity * dt

# Function to reset simulation
def reset_simulation():
    global angle, angular_velocity, angular_acceleration, trail_points
    angle = math.radians(angle_slider.value)
    angular_velocity = 0.0
    angular_acceleration = 0.0
    trail_points = []

# Function to draw everything
def draw():
    screen.fill(WHITE)
    
    # Draw title
    title = title_font.render("Simple Harmonic Pendulum Simulation", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
    
    # Draw pivot
    pygame.draw.circle(screen, BLACK, (pivot_x, pivot_y), 5)
    
    # Get bob position
    bob_pos = get_bob_position()
    
    # Draw trail
    if len(trail_points) > 1:
        pygame.draw.lines(screen, GRAY, False, trail_points, 2)
    
    # Draw string
    pygame.draw.line(screen, BLACK, (pivot_x, pivot_y), bob_pos, 2)
    
    # Draw reference line (vertical)
    pygame.draw.line(screen, RED, (pivot_x, pivot_y), (pivot_x, pivot_y + 40), 2)
    
    # Draw bob
    pygame.draw.circle(screen, BLUE, bob_pos, bob_radius)
    pygame.draw.circle(screen, DARK_BLUE, bob_pos, bob_radius, 2)
    
    # Draw physics values
    period = 2 * math.pi * math.sqrt(length / gravity)
    period_text = font.render(f"Period (T): {period:.2f} seconds", True, BLACK)
    screen.blit(period_text, (30, HEIGHT - 280))
    
    angular_velocity_text = font.render(f"Angular Velocity (ω): {angular_velocity:.2f} rad/s", True, BLACK)
    screen.blit(angular_velocity_text, (30, HEIGHT - 260))
    
    # Calculate energy
    mass = 1.0  # Assuming unit mass
    bob_y = bob_pos[1] / pixels_per_meter
    kinetic_energy = 0.5 * mass * length * length * angular_velocity * angular_velocity
    potential_energy = mass * gravity * (bob_y - (pivot_y / pixels_per_meter))
    total_energy = kinetic_energy + potential_energy
    
    energy_text = font.render(f"Energy: {total_energy:.2f} J", True, BLACK)
    screen.blit(energy_text, (30, HEIGHT - 240))
    
    # Draw buttons
    start_button.draw(screen)
    pause_button.draw(screen)
    reset_button.draw(screen)
    
    # Draw sliders
    length_slider.draw(screen)
    gravity_slider.draw(screen)
    dampening_slider.draw(screen)
    angle_slider.draw(screen)
    
    pygame.display.flip()

# Main simulation variables
running = True
simulation_running = False
last_time = pygame.time.get_ticks()

# Main game loop
while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0  # Convert to seconds
    last_time = current_time
    
    # Event handling
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            mouse_clicked = True
    
    # Update button hover states
    start_button.check_hover(mouse_pos)
    pause_button.check_hover(mouse_pos)
    reset_button.check_hover(mouse_pos)
    
    # Handle button clicks
    if start_button.is_clicked(mouse_pos, mouse_clicked):
        simulation_running = True
    elif pause_button.is_clicked(mouse_pos, mouse_clicked):
        simulation_running = False
    elif reset_button.is_clicked(mouse_pos, mouse_clicked):
        reset_simulation()
    
    # Handle slider interactions
    length_slider.check_click(mouse_pos, mouse_clicked)
    gravity_slider.check_click(mouse_pos, mouse_clicked)
    dampening_slider.check_click(mouse_pos, mouse_clicked)
    angle_slider.check_click(mouse_pos, mouse_clicked)
    
    slider_updated = (
        length_slider.update(mouse_pos, pygame.mouse.get_pressed()[0]) or
        gravity_slider.update(mouse_pos, pygame.mouse.get_pressed()[0]) or
        dampening_slider.update(mouse_pos, pygame.mouse.get_pressed()[0]) or
        angle_slider.update(mouse_pos, pygame.mouse.get_pressed()[0])
    )
    
    # Update physics values if sliders changed
    if slider_updated:
        length = length_slider.value
        gravity = gravity_slider.value
        dampening = dampening_slider.value
        if angle_slider.update(mouse_pos, pygame.mouse.get_pressed()[0]):
            angle = math.radians(angle_slider.value)
    
    # Update simulation if running
    if simulation_running:
        update_physics(min(dt, 0.05))  # Cap delta time to avoid physics instability
        
        # Add to trail
        bob_pos = get_bob_position()
        trail_points.append(bob_pos)
        if len(trail_points) > max_trail_points:
            trail_points.pop(0)
    
    # Draw everything
    draw()
    
    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
