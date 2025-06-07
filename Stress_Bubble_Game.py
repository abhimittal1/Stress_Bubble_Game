import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Stress Bubble Pop + Breathing Trainer")

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 100, 100)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)

# Clock
clock = pygame.time.Clock()
fps = 60

# Bubble properties
bubble_radius = 30
bubble_spawn_time = 0
current_bubble = None
bubble_lifespan = 3000  # start with 3 seconds

# Breathing trainer
breath_min = 50
breath_max = 150
breath_duration = 4000
breath_start_time = pygame.time.get_ticks()

# Game states
POP_PHASE = 'pop'
BREATH_PHASE = 'breath'
phase_duration = 15000
phase_start_time = pygame.time.get_ticks()
current_phase = POP_PHASE

# Score, stress, level
score = 0
stress = 0
max_stress = 10
level = 1
last_score_level_up = 0
game_over = False

# Affirmations
affirmations = [
    "Great job!", "Keep it up!", "You're doing awesome!", "Well done!",
    "Stay strong!", "Nice pop!", "You got this!", "Fantastic!", "Keep breathing!"
]
affirmation_show_time = 1500
affirmation_start_time = 0
current_affirmation = ""
show_affirmation = False

font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 60)

def spawn_bubble():
    global current_bubble, bubble_spawn_time
    x = random.randint(bubble_radius, screen_width - bubble_radius)
    y = random.randint(bubble_radius, screen_height - bubble_radius)
    current_bubble = {'pos': (x, y), 'radius': bubble_radius}
    bubble_spawn_time = pygame.time.get_ticks()

def draw_bubble():
    if current_bubble:
        pygame.draw.circle(screen, BLUE, current_bubble['pos'], current_bubble['radius'])
        pygame.draw.circle(screen, WHITE, current_bubble['pos'], current_bubble['radius'] - 5)

def check_bubble_click(pos):
    global score, show_affirmation, current_affirmation, affirmation_start_time, current_bubble
    if current_bubble:
        bx, by = current_bubble['pos']
        dist = math.hypot(pos[0] - bx, pos[1] - by)
        if dist <= current_bubble['radius']:
            current_bubble = None
            score += 1
            current_affirmation = random.choice(affirmations)
            show_affirmation = True
            affirmation_start_time = pygame.time.get_ticks()
            return

def get_breath_radius():
    elapsed = (pygame.time.get_ticks() - breath_start_time) % (2 * breath_duration)
    if elapsed < breath_duration:
        return breath_min + (breath_max - breath_min) * (elapsed / breath_duration)
    else:
        return breath_max - (breath_max - breath_min) * ((elapsed - breath_duration) / breath_duration)

def draw_breathing_circle():
    radius = int(get_breath_radius())
    center = (screen_width // 2, screen_height // 2)
    pygame.draw.circle(screen, GREEN, center, radius)
    pygame.draw.circle(screen, WHITE, center, radius - 20)
    prompt = "Breathe In" if (pygame.time.get_ticks() - breath_start_time) % (2 * breath_duration) < breath_duration else "Breathe Out"
    text = font.render(prompt, True, BLACK)
    text_rect = text.get_rect(center=(center[0], center[1] + radius + 30))
    screen.blit(text, text_rect)

def draw_ui():
    score_text = font.render(f"Score: {score}", True, BLACK)
    stress_text = font.render(f"Stress: {stress}/{max_stress}", True, BLACK)
    phase_text = font.render(f"Phase: {current_phase.upper()}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(stress_text, (10, 40))
    screen.blit(phase_text, (10, 70))
    screen.blit(level_text, (10, 100))
    if show_affirmation:
        affirmation_text = font.render(current_affirmation, True, (0, 100, 0))
        affirmation_rect = affirmation_text.get_rect(center=(screen_width // 2, screen_height - 50))
        screen.blit(affirmation_text, affirmation_rect)

def draw_game_over():
    screen.fill(WHITE)
    over_text = big_font.render("Game Over", True, RED)
    final_score_text = font.render(f"Final Score: {score}", True, BLACK)
    final_level_text = font.render(f"Level Reached: {level}", True, BLACK)
    final_stress_text = font.render(f"Stress Level: {stress}/{max_stress}", True, BLACK)
    restart_text = font.render("Press R to Restart or Esc to Quit", True, BLACK)

    screen.blit(over_text, over_text.get_rect(center=(screen_width//2, screen_height//2 - 60)))
    screen.blit(final_score_text, final_score_text.get_rect(center=(screen_width//2, screen_height//2 - 20)))
    screen.blit(final_level_text, final_level_text.get_rect(center=(screen_width//2, screen_height//2 + 10)))
    screen.blit(final_stress_text, final_stress_text.get_rect(center=(screen_width//2, screen_height//2 + 40)))
    screen.blit(restart_text, restart_text.get_rect(center=(screen_width//2, screen_height//2 + 90)))

# Main loop
running = True
while running:
    screen.fill(WHITE)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0
                    stress = 0
                    level = 1
                    last_score_level_up = 0
                    current_phase = POP_PHASE
                    phase_start_time = pygame.time.get_ticks()
                    game_over = False
                    current_bubble = None
                    bubble_lifespan = 3000
                elif event.key == pygame.K_ESCAPE:
                    running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and current_phase == POP_PHASE:
            pos = pygame.mouse.get_pos()
            check_bubble_click(pos)

    if game_over:
        draw_game_over()
        pygame.display.flip()
        clock.tick(fps)
        continue

    # Level up (max 3 levels)
    if score >= last_score_level_up + 10 and level < 3:
        level += 1
        last_score_level_up = score
        if level == 2:
            bubble_lifespan = 2000
        elif level == 3:
            bubble_lifespan = 1000

    # Check for stress max
    if stress >= max_stress:
        game_over = True

    # Phase switching
    if now - phase_start_time > phase_duration:
        phase_start_time = now
        if current_phase == POP_PHASE:
            current_phase = BREATH_PHASE
            breath_start_time = now
            current_bubble = None
        else:
            current_phase = POP_PHASE

    if current_phase == POP_PHASE:
        # Handle bubble timeout
        if current_bubble:
            if now - bubble_spawn_time > bubble_lifespan:
                current_bubble = None
                stress = min(max_stress, stress + 1)
        else:
            spawn_bubble()
        draw_bubble()
    else:
        draw_breathing_circle()

    if show_affirmation and now - affirmation_start_time > affirmation_show_time:
        show_affirmation = False

    draw_ui()
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
