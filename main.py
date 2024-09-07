import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
STAR_COLOR = (255, 255, 255)
PLAYER_COLOR = (255, 0, 0)  # Color for the player
ENEMY_SPEED = 5
LASER_SPEED = 7
LIVES = 3
SCORE = 0
LASER_LIMIT = 3  # Limit the number of lasers fired at once
LASER_INTERVAL = 1000  # Interval between lasers in milliseconds

# Font setup
font = pygame.font.SysFont(None, 36)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starry Background Shooter Game")

# Set up the clock
clock = pygame.time.Clock()

# Star setup
stars = []

def spawn_star():
    star_x = WIDTH
    star_y = random.randint(0, HEIGHT)
    star_size = random.randint(1, 3)
    stars.append({'x': star_x, 'y': star_y, 'size': star_size})

def move_stars():
    for star in stars[:]:
        star['x'] -= 2  # Move stars leftward at a slow speed
        if star['x'] < 0:
            stars.remove(star)

# Enemy setup
initial_enemy_speed = ENEMY_SPEED
enemies = []
enemy_shapes = ['rect', 'circle', 'triangle']  # Possible enemy shapes
shape_points = {
    'rect': 3,
    'circle': 10,
    'triangle': 5
}  # Points for each shape

def spawn_enemy():
    enemy_x = WIDTH
    enemy_y = random.randint(0, HEIGHT - 50)
    enemy_width = random.randint(30, 50)
    enemy_height = random.randint(30, 50)
    shape = random.choice(enemy_shapes)  # Randomly choose a shape
    color = random.choice([WHITE, BLUE, (255, 255, 0), (0, 255, 0), (255, 0, 255)])  # Random color
    enemies.append({
        'x': enemy_x,
        'y': enemy_y,
        'width': enemy_width,
        'height': enemy_height,
        'shape': shape,
        'color': color,
        'points': shape_points[shape]  # Assign points based on the shape
    })

def shoot_laser():
    global last_laser_time
    current_time = pygame.time.get_ticks()
    if len(lasers) < LASER_LIMIT and (current_time - last_laser_time >= LASER_INTERVAL):
        laser = pygame.Rect(player_x + player_width, player_y + player_height // 2 - 2, laser_width, laser_height)
        lasers.append(laser)
        last_laser_time = current_time  # Update the time of the last laser shot

# Game setup
lasers = []
laser_width, laser_height = 20, 5
last_laser_time = 0  # Time of the last laser shot

player_width, player_height = 50, 50
player_x, player_y = 10, HEIGHT // 2 - player_height // 2
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

def draw_enemy(enemy):
    x, y, width, height, shape, color = enemy['x'], enemy['y'], enemy['width'], enemy['height'], enemy['shape'], enemy['color']
    if shape == 'rect':
        pygame.draw.rect(screen, color, pygame.Rect(x, y, width, height))
    elif shape == 'circle':
        pygame.draw.circle(screen, color, (x + width // 2, y + height // 2), width // 2)
    elif shape == 'triangle':
        points = [(x, y + height), (x + width // 2, y), (x + width, y + height)]
        pygame.draw.polygon(screen, color, points)

def draw_shape_labels():
    center_x = WIDTH // 2
    text_surface = font.render('Triangle: 5 points', True, WHITE)
    text_rect = text_surface.get_rect(center=(center_x, 30))
    screen.blit(text_surface, text_rect)
    
    text_surface = font.render('Square: 3 points', True, WHITE)
    text_rect = text_surface.get_rect(center=(center_x, 60))
    screen.blit(text_surface, text_rect)
    
    text_surface = font.render('Circle: 10 points', True, WHITE)
    text_rect = text_surface.get_rect(center=(center_x, 90))
    screen.blit(text_surface, text_rect)

def adjust_difficulty():
    global enemy_speed
    if SCORE < 20:
        enemy_speed = initial_enemy_speed
    elif SCORE < 50:
        enemy_speed = initial_enemy_speed + 2
    elif SCORE < 100:
        enemy_speed = initial_enemy_speed + 4
    else:
        enemy_speed = initial_enemy_speed + 6

# Game loop
running = True
while running:
    clock.tick(FPS)  # Keep the game running at 60 FPS
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    # Get the keys pressed
    keys = pygame.key.get_pressed()
    
    # Move player position based on key press
    if keys[pygame.K_UP]:
        player_y -= 5
    if keys[pygame.K_DOWN]:
        player_y += 5
    if keys[pygame.K_SPACE]:
        shoot_laser()

    # Update player rectangle position
    player_rect.y = player_y

    # Ensure the player stays within window boundaries
    player_y = max(0, min(HEIGHT - player_height, player_y))

    # Spawn stars randomly
    if random.randint(1, 10) == 1:
        spawn_star()

    move_stars()  # Move stars

    # Adjust difficulty based on score
    adjust_difficulty()

    # Spawn enemies
    if random.randint(1, 50) == 1:  # Spawn an enemy every ~50 frames
        spawn_enemy()

    # Move enemies leftward
    for enemy in enemies[:]:
        enemy['x'] -= enemy_speed
        if enemy['x'] < -enemy['width']:
            enemies.remove(enemy)
        elif player_rect.colliderect(pygame.Rect(enemy['x'], enemy['y'], enemy['width'], enemy['height'])):
            enemies.remove(enemy)  # Remove enemy if it hits the player
            LIVES -= 1
            if LIVES <= 0:
                running = False

    # Move lasers rightward
    for laser in lasers[:]:
        laser.x += LASER_SPEED
        if laser.x > WIDTH:
            lasers.remove(laser)

    # Check laser-enemy collisions
    for laser in lasers[:]:
        for enemy in enemies[:]:
            if pygame.Rect(enemy['x'], enemy['y'], enemy['width'], enemy['height']).colliderect(laser):
                enemies.remove(enemy)
                lasers.remove(laser)
                SCORE += enemy['points']  # Add points based on the enemy's shape
                break

    # Fill the screen with black color
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        pygame.draw.circle(screen, STAR_COLOR, (star['x'], star['y']), star['size'])

    # Draw the player
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

    # Draw the enemies
    for enemy in enemies:
        draw_enemy(enemy)

    # Draw the lasers
    for laser in lasers:
        pygame.draw.rect(screen, WHITE, laser)

    # Draw shape labels in the top middle
    draw_shape_labels()

    # Display lives and score
    lives_text = font.render(f'Lives: {LIVES}', True, WHITE)
    score_text = font.render(f'Score: {SCORE}', True, WHITE)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (WIDTH - 150, 10))

    # Update the display
    pygame.display.flip()

# Close pygame
pygame.quit()

# Final message
print(f"Game Over! Your score: {SCORE}")
