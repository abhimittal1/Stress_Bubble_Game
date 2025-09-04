import pygame
import random
import math
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Stress Bubble Pop + Breathing Trainer")

# Water blue and white color palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Water-inspired gradient colors
GRADIENT_TOP = (230, 245, 255)  # Very light water blue
GRADIENT_BOTTOM = (200, 230, 255)  # Light water blue
SECONDARY_GRADIENT_TOP = (240, 250, 255)  # Almost white blue
SECONDARY_GRADIENT_BOTTOM = (210, 235, 255)  # Soft water blue

# Water blue UI colors
CARD_BG = (255, 255, 255)
CARD_SHADOW = (180, 210, 240, 80)  # Water blue shadow
TEXT_PRIMARY = (60, 120, 180)  # Deep water blue
TEXT_SECONDARY = (100, 150, 200)  # Medium water blue
ACCENT_COLOR = (120, 180, 240)  # Water blue
ACCENT_HOVER = (80, 150, 220)  # Deeper water blue
SUCCESS_COLOR = (100, 170, 220)  # Ocean blue
WARNING_COLOR = (150, 190, 230)  # Light water blue
DANGER_COLOR = (120, 160, 210)  # Muted water blue

# Game bubble colors - water themed
BUBBLE_COLOR = (160, 210, 255)  # Clear water blue
BUBBLE_HIGHLIGHT = (240, 250, 255)  # White with hint of blue
BREATHING_COLOR = (140, 200, 255)  # Deep water blue
BREATHING_HIGHLIGHT = (220, 240, 255)  # Light water white

# Pop animation colors
POP_COLORS = [
    (200, 230, 255),  # Light water blue
    (180, 220, 255),  # Medium water blue
    (220, 240, 255),  # Very light blue
    (160, 210, 255),  # Clear blue
    (240, 250, 255),  # Almost white blue
]

# Clock
clock = pygame.time.Clock()
fps = 60

# Game states
WELCOME_STATE = 'welcome'
GAME_STATE = 'game'
GAME_OVER_STATE = 'game_over'
LEADERBOARD_STATE = 'leaderboard'
NAME_INPUT_STATE = 'name_input'
current_state = WELCOME_STATE

# Leaderboard system
LEADERBOARD_FILE = "bubble_pop_scores.json"
MAX_LEADERBOARD_ENTRIES = 10

class LeaderboardManager:
    def __init__(self):
        self.scores = self.load_scores()
    
    def load_scores(self):
        try:
            if os.path.exists(LEADERBOARD_FILE):
                with open(LEADERBOARD_FILE, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_scores(self):
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except:
            pass
    
    def add_score(self, name, score, level, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        entry = {
            'name': name,
            'score': score,
            'level': level,
            'date': date
        }
        
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:MAX_LEADERBOARD_ENTRIES]
        self.save_scores()
    
    def is_high_score(self, score):
        if len(self.scores) < MAX_LEADERBOARD_ENTRIES:
            return True
        return score > self.scores[-1]['score']
    
    def get_rank(self, score):
        rank = 1
        for entry in self.scores:
            if score > entry['score']:
                return rank
            rank += 1
        return rank if len(self.scores) < MAX_LEADERBOARD_ENTRIES else None

leaderboard = LeaderboardManager()

# Name input system
player_name = ""
name_input_active = False
cursor_visible = True
cursor_timer = 0

# Welcome screen floating bubbles with water colors
welcome_bubbles = []
bubble_colors = [
    (200, 230, 255, 60),  # Light water blue
    (180, 220, 255, 50),  # Medium water blue
    (220, 240, 255, 55),  # Very light blue
    (160, 210, 255, 65),  # Clear blue
]

for i in range(15):
    welcome_bubbles.append({
        'x': random.randint(50, screen_width - 50),
        'y': random.randint(50, screen_height - 50),
        'radius': random.randint(12, 35),
        'speed_x': random.uniform(-0.5, 0.5),
        'speed_y': random.uniform(-0.5, 0.5),
        'color': random.choice(bubble_colors),
        'pulse': random.uniform(0, math.pi * 2),
        'pulse_speed': random.uniform(0.02, 0.05)
    })

# Bubble properties (game)
bubble_radius = 30
bubble_spawn_time = 0
current_bubble = None
bubble_lifespan = 3000  # start with 3 seconds

# Pop animation system
pop_animations = []

class PopParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y
        self.velocity_x = random.uniform(-4, 4)
        self.velocity_y = random.uniform(-6, -2)
        self.gravity = 0.2
        self.size = random.randint(3, 8)
        self.color = random.choice(POP_COLORS)
        self.alpha = 255
        self.fade_speed = random.uniform(3, 6)
        self.life = random.uniform(30, 60)  # frames
        self.max_life = self.life
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-0.2, 0.2)

    def update(self):
        # Physics
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.velocity_x *= 0.98  # Air resistance
        
        # Rotation
        self.rotation += self.rotation_speed
        
        # Fade out
        self.life -= 1
        life_ratio = self.life / self.max_life
        self.alpha = int(255 * life_ratio)
        self.size = max(1, int(self.size * life_ratio))
        
        return self.life > 0

    def draw(self, surface):
        if self.alpha > 0:
            # Create particle surface with alpha
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, max(0, min(255, self.alpha)))
            
            # Draw soft particle with glow effect
            for i in range(2):
                glow_size = self.size + i
                glow_alpha = self.alpha // (i + 2)
                glow_color = (*self.color, glow_alpha)
                pygame.draw.circle(particle_surface, glow_color, (self.size, self.size), glow_size)
            
            # Main particle
            pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
            
            surface.blit(particle_surface, (self.x - self.size, self.y - self.size))

class PopAnimation:
    def __init__(self, x, y, bubble_radius):
        self.particles = []
        self.ripples = []
        self.duration = 90  # frames
        self.time = 0
        
        # Create particles
        num_particles = random.randint(12, 20)
        for _ in range(num_particles):
            # Spawn particles in a circle around the pop position
            angle = random.uniform(0, math.pi * 2)
            spawn_radius = random.uniform(0, bubble_radius * 0.8)
            spawn_x = x + math.cos(angle) * spawn_radius
            spawn_y = y + math.sin(angle) * spawn_radius
            self.particles.append(PopParticle(spawn_x, spawn_y))
        
        # Create ripple effects
        for i in range(3):
            self.ripples.append({
                'x': x,
                'y': y,
                'radius': 0,
                'max_radius': bubble_radius + i * 15,
                'alpha': 255,
                'delay': i * 5,
                'started': False
            })

    def update(self):
        self.time += 1
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update ripples
        for ripple in self.ripples:
            if self.time >= ripple['delay']:
                if not ripple['started']:
                    ripple['started'] = True
                
                if ripple['started']:
                    ripple['radius'] += 2
                    ripple['alpha'] = max(0, ripple['alpha'] - 4)
        
        return self.time < self.duration and (len(self.particles) > 0 or any(r['alpha'] > 0 for r in self.ripples))

    def draw(self, surface):
        # Draw ripples first
        for ripple in self.ripples:
            if ripple['started'] and ripple['alpha'] > 0 and ripple['radius'] < ripple['max_radius']:
                ripple_surface = pygame.Surface((ripple['radius'] * 2 + 10, ripple['radius'] * 2 + 10), pygame.SRCALPHA)
                ripple_color = (200, 230, 255, ripple['alpha'])
                
                # Outer ripple
                pygame.draw.circle(ripple_surface, ripple_color, 
                                 (ripple['radius'] + 5, ripple['radius'] + 5), 
                                 ripple['radius'], 2)
                
                surface.blit(ripple_surface, 
                           (ripple['x'] - ripple['radius'] - 5, ripple['y'] - ripple['radius'] - 5))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

# Breathing trainer
breath_min = 50
breath_max = 150
breath_duration = 2000
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
    "Stay calm!", "Nice pop!", "You got this!", "Fantastic!", "Keep breathing!",
    "Relax and breathe", "You're amazing!", "Stay peaceful"
]
affirmation_show_time = 1500
affirmation_start_time = 0
current_affirmation = ""
show_affirmation = False

# Soft, readable fonts
font_small = pygame.font.SysFont('Segoe UI', 18)
font_medium = pygame.font.SysFont('Segoe UI', 24)
font_large = pygame.font.SysFont('Segoe UI', 32)
font_title = pygame.font.SysFont('Segoe UI', 52, bold=True)
font_subtitle = pygame.font.SysFont('Segoe UI', 20)

def reset_game():
    global score, stress, level, last_score_level_up, current_phase, phase_start_time, game_over, current_bubble, bubble_lifespan, pop_animations
    score = 0
    stress = 0
    level = 1
    last_score_level_up = 0
    current_phase = POP_PHASE
    phase_start_time = pygame.time.get_ticks()
    game_over = False
    current_bubble = None
    bubble_lifespan = 3000
    pop_animations = []

def draw_gradient_background(top_color=GRADIENT_TOP, bottom_color=GRADIENT_BOTTOM):
    """Draw a smooth, water-inspired gradient background"""
    for y in range(screen_height):
        ratio = y / screen_height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (screen_width, y))

def draw_soft_card(surface, rect, shadow_offset=3):
    """Draw a soft card with gentle water blue shadow"""
    # Soft shadow
    shadow_rect = rect.copy()
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, CARD_SHADOW, (0, 0, shadow_rect.width, shadow_rect.height), border_radius=20)
    surface.blit(shadow_surface, shadow_rect.topleft)
    
    # Main card with very soft border
    pygame.draw.rect(surface, CARD_BG, rect, border_radius=20)
    pygame.draw.rect(surface, (180, 210, 240, 50), rect, width=1, border_radius=20)

def draw_soft_button(surface, rect, text, font, is_hovering=False, is_primary=True):
    """Draw a soft, water-themed button"""
    if is_primary:
        bg_color = ACCENT_HOVER if is_hovering else ACCENT_COLOR
        text_color = WHITE
    else:
        bg_color = WHITE
        text_color = ACCENT_COLOR
        
    # Button background with soft shadow
    if is_hovering:
        shadow_rect = rect.copy()
        shadow_rect.y += 2
        pygame.draw.rect(surface, (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2], 30), shadow_rect, border_radius=30)
    
    pygame.draw.rect(surface, bg_color, rect, border_radius=30)
    
    # Soft border for secondary buttons
    if not is_primary:
        pygame.draw.rect(surface, ACCENT_COLOR, rect, width=2, border_radius=30)
    
    # Button text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_welcome_screen():
    # Water gradient background
    draw_gradient_background()
    
    # Update and draw floating bubbles with water effects
    for bubble in welcome_bubbles:
        # Update gentle pulse
        bubble['pulse'] += bubble['pulse_speed']
        pulse_scale = 1 + 0.05 * math.sin(bubble['pulse'])
        
        # Gentle movement
        bubble['x'] += bubble['speed_x']
        bubble['y'] += bubble['speed_y']
        
        # Soft bounce off edges
        if bubble['x'] <= bubble['radius'] or bubble['x'] >= screen_width - bubble['radius']:
            bubble['speed_x'] *= -1
        if bubble['y'] <= bubble['radius'] or bubble['y'] >= screen_height - bubble['radius']:
            bubble['speed_y'] *= -1
            
        # Draw bubble with water-like styling
        current_radius = int(bubble['radius'] * pulse_scale)
        bubble_surface = pygame.Surface((current_radius * 2 + 8, current_radius * 2 + 8), pygame.SRCALPHA)
        
        # Gentle outer glow
        for i in range(2):
            glow_alpha = 15 - i * 5
            glow_radius = current_radius + i * 2
            color_with_alpha = (*bubble['color'][:3], glow_alpha)
            pygame.draw.circle(bubble_surface, color_with_alpha, 
                             (current_radius + 4, current_radius + 4), glow_radius)
        
        # Main bubble with water color
        pygame.draw.circle(bubble_surface, bubble['color'], 
                          (current_radius + 4, current_radius + 4), current_radius)
        
        # Very soft inner highlight
        highlight_pos = (current_radius + 4 - current_radius//4, current_radius + 4 - current_radius//4)
        highlight_color = (*WHITE, 40)
        pygame.draw.circle(bubble_surface, highlight_color, highlight_pos, current_radius//5)
        
        screen.blit(bubble_surface, (bubble['x'] - current_radius - 4, bubble['y'] - current_radius - 4))
    
    # Main card container
    card_width, card_height = 480, 580
    card_rect = pygame.Rect(screen_width//2 - card_width//2, screen_height//2 - card_height//2, card_width, card_height)
    draw_soft_card(screen, card_rect)
    
    # Water-themed app icon
    icon_rect = pygame.Rect(screen_width//2 - 35, screen_height//2 - 250, 70, 70)
    pygame.draw.circle(screen, ACCENT_COLOR, icon_rect.center, 35)
    pygame.draw.circle(screen, BUBBLE_HIGHLIGHT, (icon_rect.centerx - 10, icon_rect.centery - 10), 8)
    pygame.draw.circle(screen, BUBBLE_HIGHLIGHT, (icon_rect.centerx + 6, icon_rect.centery + 6), 6)
    pygame.draw.circle(screen, BUBBLE_HIGHLIGHT, (icon_rect.centerx + 12, icon_rect.centery - 8), 4)
    
    # Title with water blue color
    title_text = font_title.render("Bubble Pop", True, TEXT_PRIMARY)
    title_rect = title_text.get_rect(center=(screen_width//2, screen_height//2 - 160))
    screen.blit(title_text, title_rect)
    
    # Water-themed subtitle
    subtitle_text = font_subtitle.render("Dive into Calm • Breathe & Flow", True, TEXT_SECONDARY)
    subtitle_rect = subtitle_text.get_rect(center=(screen_width//2, screen_height//2 - 125))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Features section with water-inspired descriptions
    features_y_start = screen_height//2 - 80
    features = [
        ("🫧", "Gently pop bubbles like ocean waves"),
        ("🌊", "Practice flowing breathing exercises"),
        ("✨", "Drift at your own peaceful pace"),
        ("💧", "Create your moment of tranquility")
    ]
    
    for i, (icon, text) in enumerate(features):
        y_pos = features_y_start + i * 30
        
        # Feature icon
        icon_text = pygame.font.SysFont('Segoe UI Emoji', 18).render(icon, True, ACCENT_COLOR)
        screen.blit(icon_text, (screen_width//2 - 190, y_pos))
        
        # Feature text
        feature_text = font_small.render(text, True, TEXT_SECONDARY)
        screen.blit(feature_text, (screen_width//2 - 160, y_pos + 1))
    
    # Buttons
    button_width, button_height = 200, 45
    start_button_rect = pygame.Rect(screen_width//2 - button_width//2, screen_height//2 + 80, button_width, button_height)
    leaderboard_button_rect = pygame.Rect(screen_width//2 - button_width//2, screen_height//2 + 135, button_width, button_height)
    
    # Check hover states
    mouse_pos = pygame.mouse.get_pos()
    start_hovering = start_button_rect.collidepoint(mouse_pos)
    leaderboard_hovering = leaderboard_button_rect.collidepoint(mouse_pos)
    
    draw_soft_button(screen, start_button_rect, "DIVE IN", font_medium, start_hovering, True)
    draw_soft_button(screen, leaderboard_button_rect, "🏆 LEADERBOARD", font_medium, leaderboard_hovering, False)
    
    # Gentle instruction text
    instruction_text = font_small.render("Press SPACE to start • L for leaderboard", True, TEXT_SECONDARY)
    instruction_rect = instruction_text.get_rect(center=(screen_width//2, screen_height//2 + 200))
    screen.blit(instruction_text, instruction_rect)
    
    # Water-themed credits
    credits_text = pygame.font.SysFont('Segoe UI', 12).render("Flow with the rhythm of calm waters", True, (TEXT_SECONDARY[0], TEXT_SECONDARY[1], TEXT_SECONDARY[2], 100))
    screen.blit(credits_text, (screen_width//2 - credits_text.get_width()//2, screen_height - 25))
    
    return start_button_rect, leaderboard_button_rect

def draw_leaderboard():
    # Water gradient background
    draw_gradient_background()
    
    # Update floating bubbles
    for bubble in welcome_bubbles:
        bubble['pulse'] += bubble['pulse_speed']
        pulse_scale = 1 + 0.03 * math.sin(bubble['pulse'])
        bubble['x'] += bubble['speed_x'] * 0.3
        bubble['y'] += bubble['speed_y'] * 0.3
        
        if bubble['x'] <= bubble['radius'] or bubble['x'] >= screen_width - bubble['radius']:
            bubble['speed_x'] *= -1
        if bubble['y'] <= bubble['radius'] or bubble['y'] >= screen_height - bubble['radius']:
            bubble['speed_y'] *= -1
    
    # Leaderboard card
    card_width, card_height = 600, 520
    card_rect = pygame.Rect(screen_width//2 - card_width//2, screen_height//2 - card_height//2, card_width, card_height)
    draw_soft_card(screen, card_rect)
    
    # Title
    title_text = font_large.render("🏆 Ocean Champions", True, TEXT_PRIMARY)
    title_rect = title_text.get_rect(center=(screen_width//2, screen_height//2 - 220))
    screen.blit(title_text, title_rect)
    
    subtitle_text = font_subtitle.render("Ride the waves of excellence", True, TEXT_SECONDARY)
    subtitle_rect = subtitle_text.get_rect(center=(screen_width//2, screen_height//2 - 190))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Headers
    headers_y = screen_height//2 - 150
    pygame.draw.line(screen, ACCENT_COLOR, (screen_width//2 - 250, headers_y + 25), (screen_width//2 + 250, headers_y + 25), 2)
    
    rank_text = font_medium.render("Rank", True, TEXT_PRIMARY)
    name_text = font_medium.render("Navigator", True, TEXT_PRIMARY)
    score_text = font_medium.render("Bubbles", True, TEXT_PRIMARY)
    level_text = font_medium.render("Level", True, TEXT_PRIMARY)
    date_text = font_medium.render("Date", True, TEXT_PRIMARY)
    
    screen.blit(rank_text, (screen_width//2 - 250, headers_y))
    screen.blit(name_text, (screen_width//2 - 180, headers_y))
    screen.blit(score_text, (screen_width//2 - 50, headers_y))
    screen.blit(level_text, (screen_width//2 + 50, headers_y))
    screen.blit(date_text, (screen_width//2 + 120, headers_y))
    
    # Scores
    start_y = headers_y + 40
    for i, entry in enumerate(leaderboard.scores[:8]):  # Show top 8
        y_pos = start_y + i * 35
        
        # Medal emojis for top 3
        if i == 0:
            rank_display = "🥇"
        elif i == 1:
            rank_display = "🥈"
        elif i == 2:
            rank_display = "🥉"
        else:
            rank_display = f"{i + 1}"
        
        # Alternate row colors
        if i % 2 == 0:
            row_rect = pygame.Rect(screen_width//2 - 280, y_pos - 5, 560, 30)
            pygame.draw.rect(screen, (240, 248, 255, 100), row_rect, border_radius=5)
        
        rank_surface = font_medium.render(rank_display, True, TEXT_PRIMARY)
        name_surface = font_medium.render(entry['name'][:12], True, TEXT_PRIMARY)  # Limit name length
        score_surface = font_medium.render(str(entry['score']), True, SUCCESS_COLOR)
        level_surface = font_medium.render(str(entry['level']), True, TEXT_SECONDARY)
        date_surface = font_small.render(entry['date'][:10], True, TEXT_SECONDARY)  # Show only date part
        
        screen.blit(rank_surface, (screen_width//2 - 250, y_pos))
        screen.blit(name_surface, (screen_width//2 - 180, y_pos))
        screen.blit(score_surface, (screen_width//2 - 50, y_pos))
        screen.blit(level_surface, (screen_width//2 + 50, y_pos))
        screen.blit(date_surface, (screen_width//2 + 120, y_pos))
    
    # No scores message
    if not leaderboard.scores:
        no_scores_text = font_medium.render("No voyages recorded yet...", True, TEXT_SECONDARY)
        no_scores_rect = no_scores_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
        screen.blit(no_scores_text, no_scores_rect)
        
        encourage_text = font_small.render("Be the first to make waves!", True, TEXT_SECONDARY)
        encourage_rect = encourage_text.get_rect(center=(screen_width//2, screen_height//2 - 20))
        screen.blit(encourage_text, encourage_rect)
    
    # Back button
    back_button_rect = pygame.Rect(screen_width//2 - 100, screen_height//2 + 190, 200, 45)
    mouse_pos = pygame.mouse.get_pos()
    back_hovering = back_button_rect.collidepoint(mouse_pos)
    draw_soft_button(screen, back_button_rect, "🌊 BACK TO SHORE", font_medium, back_hovering, True)
    
    # Instructions
    instruction_text = font_small.render("Press ESC or click to return", True, TEXT_SECONDARY)
    instruction_rect = instruction_text.get_rect(center=(screen_width//2, screen_height//2 + 250))
    screen.blit(instruction_text, instruction_rect)
    
    return back_button_rect

def draw_name_input():
    global cursor_visible, cursor_timer
    
    # Water gradient background
    draw_gradient_background()
    
    # Name input card
    card_width, card_height = 500, 300
    card_rect = pygame.Rect(screen_width//2 - card_width//2, screen_height//2 - card_height//2, card_width, card_height)
    draw_soft_card(screen, card_rect)
    
    # Congratulations message
    congrats_text = font_large.render("🎉 New High Score!", True, SUCCESS_COLOR)
    congrats_rect = congrats_text.get_rect(center=(screen_width//2, screen_height//2 - 100))
    screen.blit(congrats_text, congrats_rect)
    
    score_text = font_medium.render(f"You scored {score} points!", True, TEXT_PRIMARY)
    score_rect = score_text.get_rect(center=(screen_width//2, screen_height//2 - 60))
    screen.blit(score_text, score_rect)
    
    # Name input prompt
    prompt_text = font_medium.render("Enter your captain's name:", True, TEXT_PRIMARY)
    prompt_rect = prompt_text.get_rect(center=(screen_width//2, screen_height//2 - 20))
    screen.blit(prompt_text, prompt_rect)
    
    # Name input box
    input_rect = pygame.Rect(screen_width//2 - 150, screen_height//2 + 10, 300, 40)
    pygame.draw.rect(screen, WHITE, input_rect, border_radius=5)
    pygame.draw.rect(screen, ACCENT_COLOR, input_rect, width=2, border_radius=5)
    
    # Display current name input with cursor
    cursor_timer += 1
    if cursor_timer > 30:  # Blink every 30 frames
        cursor_visible = not cursor_visible
        cursor_timer = 0
    
    display_text = player_name
    if cursor_visible and name_input_active:
        display_text += "|"
    
    name_surface = font_medium.render(display_text, True, TEXT_PRIMARY)
    name_rect = name_surface.get_rect(center=input_rect.center)
    screen.blit(name_surface, name_rect)
    
    # Submit button
    submit_button_rect = pygame.Rect(screen_width//2 - 100, screen_height//2 + 70, 200, 40)
    mouse_pos = pygame.mouse.get_pos()
    submit_hovering = submit_button_rect.collidepoint(mouse_pos)
    
    # Only enable button if name is entered
    if len(player_name.strip()) > 0:
        draw_soft_button(screen, submit_button_rect, "SET SAIL! ⚓", font_medium, submit_hovering, True)
    else:
        draw_soft_button(screen, submit_button_rect, "Enter Name", font_medium, False, False)
    
    # Instructions
    instruction_text = font_small.render("Type your name and press ENTER or click SET SAIL", True, TEXT_SECONDARY)
    instruction_rect = instruction_text.get_rect(center=(screen_width//2, screen_height//2 + 130))
    screen.blit(instruction_text, instruction_rect)
    
    return submit_button_rect

def spawn_bubble():
    global current_bubble, bubble_spawn_time
    x = random.randint(bubble_radius, screen_width - bubble_radius)
    y = random.randint(bubble_radius, screen_height - bubble_radius)
    current_bubble = {'pos': (x, y), 'radius': bubble_radius}
    bubble_spawn_time = pygame.time.get_ticks()

def draw_bubble():
    if current_bubble:
        # Water-like bubble with blue tones
        pos = current_bubble['pos']
        radius = current_bubble['radius']
        
        # Outer glow
        glow_surface = pygame.Surface((radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*BUBBLE_COLOR, 30), (radius + 10, radius + 10), radius + 10)
        pygame.draw.circle(glow_surface, (*BUBBLE_COLOR, 60), (radius + 10, radius + 10), radius + 5)
        screen.blit(glow_surface, (pos[0] - radius - 10, pos[1] - radius - 10))
        
        # Main bubble
        pygame.draw.circle(screen, BUBBLE_COLOR, pos, radius)
        pygame.draw.circle(screen, BUBBLE_HIGHLIGHT, pos, radius - 8)
        
        # Soft highlight
        highlight_pos = (pos[0] - radius//3, pos[1] - radius//3)
        pygame.draw.circle(screen, WHITE, highlight_pos, radius//4)

def check_bubble_click(pos):
    global score, show_affirmation, current_affirmation, affirmation_start_time, current_bubble, pop_animations
    if current_bubble:
        bx, by = current_bubble['pos']
        dist = math.hypot(pos[0] - bx, pos[1] - by)
        if dist <= current_bubble['radius']:
            # Create pop animation
            pop_animations.append(PopAnimation(bx, by, current_bubble['radius']))
            
            current_bubble = None
            score += 1
            current_affirmation = random.choice(affirmations)
            show_affirmation = True
            affirmation_start_time = pygame.time.get_ticks()
            return

def update_pop_animations():
    global pop_animations
    # Update all pop animations and remove finished ones
    pop_animations = [anim for anim in pop_animations if anim.update()]

def draw_pop_animations():
    # Draw all active pop animations
    for anim in pop_animations:
        anim.draw(screen)

def get_breath_radius():
    elapsed = (pygame.time.get_ticks() - breath_start_time) % (2 * breath_duration)
    if elapsed < breath_duration:
        return breath_min + (breath_max - breath_min) * (elapsed / breath_duration)
    else:
        return breath_max - (breath_max - breath_min) * ((elapsed - breath_duration) / breath_duration)

def draw_breathing_circle():
    radius = int(get_breath_radius())
    center = (screen_width // 2, screen_height // 2)
    
    # Water-like breathing circle
    glow_surface = pygame.Surface((radius * 2 + 40, radius * 2 + 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*BREATHING_COLOR, 20), (radius + 20, radius + 20), radius + 20)
    pygame.draw.circle(glow_surface, (*BREATHING_COLOR, 40), (radius + 20, radius + 20), radius + 10)
    screen.blit(glow_surface, (center[0] - radius - 20, center[1] - radius - 20))
    
    pygame.draw.circle(screen, BREATHING_COLOR, center, radius)
    pygame.draw.circle(screen, BREATHING_HIGHLIGHT, center, radius - 15)
    
    # Water-themed breathing prompt
    is_inhale = (pygame.time.get_ticks() - breath_start_time) % (2 * breath_duration) < breath_duration
    prompt = "Flow In... 🌊" if is_inhale else "Flow Out... 💧"
    text = font_medium.render(prompt, True, TEXT_PRIMARY)
    text_rect = text.get_rect(center=(center[0], center[1] + radius + 40))
    screen.blit(text, text_rect)
    
    # Water instruction
    instruction = "Let yourself drift with each breath"
    inst_text = font_small.render(instruction, True, TEXT_SECONDARY)
    inst_rect = inst_text.get_rect(center=(center[0], center[1] + radius + 70))
    screen.blit(inst_text, inst_rect)

def draw_soft_ui_panel(rect, alpha=200):
    """Draw a soft UI panel with water theme"""
    panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, (*WHITE, alpha), (0, 0, rect.width, rect.height), border_radius=15)
    pygame.draw.rect(panel_surface, (*ACCENT_COLOR, 50), (0, 0, rect.width, rect.height), width=2, border_radius=15)
    screen.blit(panel_surface, rect.topleft)

def draw_ui():
    # Water-themed UI panel
    ui_panel_rect = pygame.Rect(15, 15, 200, 140)
    draw_soft_ui_panel(ui_panel_rect)
    
    # Stats with water blue colors
    score_text = font_medium.render(f"Score: {score}", True, TEXT_PRIMARY)
    
    # Stress indicator with water colors
    stress_color = TEXT_PRIMARY
    if stress > 7:
        stress_color = DANGER_COLOR
    elif stress > 4:
        stress_color = WARNING_COLOR
    
    stress_text = font_medium.render(f"Tension: {stress}/{max_stress}", True, stress_color)
    phase_text = font_medium.render(f"Mode: {current_phase.upper()}", True, TEXT_PRIMARY)
    level_text = font_medium.render(f"Level: {level}", True, TEXT_PRIMARY)
    
    screen.blit(score_text, (25, 25))
    screen.blit(stress_text, (25, 55))
    screen.blit(phase_text, (25, 85))
    screen.blit(level_text, (25, 115))
    
    # Water-themed affirmation display
    if show_affirmation:
        affirmation_surface = pygame.Surface((400, 50), pygame.SRCALPHA)
        pygame.draw.rect(affirmation_surface, (*SUCCESS_COLOR, 180), (0, 0, 400, 50), border_radius=25)
        
        affirmation_text = font_medium.render(current_affirmation, True, WHITE)
        affirmation_rect = affirmation_text.get_rect(center=(200, 25))
        affirmation_surface.blit(affirmation_text, affirmation_rect)
        
        screen.blit(affirmation_surface, (screen_width // 2 - 200, screen_height - 80))

def draw_game_over():
    global current_state, player_name, name_input_active
    
    # Water gradient background
    draw_gradient_background(SECONDARY_GRADIENT_TOP, SECONDARY_GRADIENT_BOTTOM)
    
    # Check if this is a high score
    is_high_score = leaderboard.is_high_score(score)
    
    # Game over card
    card_rect = pygame.Rect(screen_width//2 - 250, screen_height//2 - 150, 500, 300)
    draw_soft_card(screen, card_rect)
    
    # Water-themed game over message
    over_text = font_large.render("Session Complete", True, TEXT_PRIMARY)
    over_rect = over_text.get_rect(center=(screen_width//2, screen_height//2 - 80))
    screen.blit(over_text, over_rect)
    
    # Stats with water-themed encouragement
    encouragement = font_medium.render("Like gentle waves, you did beautifully!", True, TEXT_SECONDARY)
    enc_rect = encouragement.get_rect(center=(screen_width//2, screen_height//2 - 50))
    screen.blit(encouragement, enc_rect)
    
    final_score_text = font_medium.render(f"Bubbles Popped: {score}", True, TEXT_PRIMARY)
    final_level_text = font_medium.render(f"Level Reached: {level}", True, TEXT_PRIMARY)
    
    screen.blit(final_score_text, final_score_text.get_rect(center=(screen_width//2, screen_height//2 - 10)))
    screen.blit(final_level_text, final_level_text.get_rect(center=(screen_width//2, screen_height//2 + 20)))
    
    # High score notification
    if is_high_score:
        high_score_text = font_medium.render("🎉 NEW HIGH SCORE! 🎉", True, SUCCESS_COLOR)
        high_score_rect = high_score_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
        screen.blit(high_score_text, high_score_rect)
        
        enter_name_text = font_small.render("Press N to enter your name for the leaderboard!", True, TEXT_PRIMARY)
        enter_name_rect = enter_name_text.get_rect(center=(screen_width//2, screen_height//2 + 75))
        screen.blit(enter_name_text, enter_name_rect)
    
    restart_text = font_small.render("Press R to dive again • ESC for main menu • N for name entry", True, TEXT_SECONDARY)
    screen.blit(restart_text, restart_text.get_rect(center=(screen_width//2, screen_height//2 + 110)))

# Main loop
running = True
start_button_rect = None
leaderboard_button_rect = None
back_button_rect = None
submit_button_rect = None

while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == WELCOME_STATE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_state = GAME_STATE
                    reset_game()
                elif event.key == pygame.K_l:
                    current_state = LEADERBOARD_STATE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect and start_button_rect.collidepoint(event.pos):
                    current_state = GAME_STATE
                    reset_game()
                elif leaderboard_button_rect and leaderboard_button_rect.collidepoint(event.pos):
                    current_state = LEADERBOARD_STATE

        elif current_state == LEADERBOARD_STATE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = WELCOME_STATE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect and back_button_rect.collidepoint(event.pos):
                    current_state = WELCOME_STATE

        elif current_state == NAME_INPUT_STATE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(player_name.strip()) > 0:
                        leaderboard.add_score(player_name.strip(), score, level)
                        player_name = ""
                        name_input_active = False
                        current_state = LEADERBOARD_STATE
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    player_name = ""
                    name_input_active = False
                    current_state = WELCOME_STATE
                else:
                    if len(player_name) < 15 and event.unicode.isprintable():
                        player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if submit_button_rect and submit_button_rect.collidepoint(event.pos) and len(player_name.strip()) > 0:
                    leaderboard.add_score(player_name.strip(), score, level)
                    player_name = ""
                    name_input_active = False
                    current_state = LEADERBOARD_STATE

        elif current_state == GAME_OVER_STATE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    current_state = GAME_STATE
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    current_state = WELCOME_STATE
                elif event.key == pygame.K_n and leaderboard.is_high_score(score):
                    current_state = NAME_INPUT_STATE
                    name_input_active = True
                    player_name = ""

        elif current_state == GAME_STATE:
            if event.type == pygame.MOUSEBUTTONDOWN and current_phase == POP_PHASE:
                pos = pygame.mouse.get_pos()
                check_bubble_click(pos)

    if current_state == WELCOME_STATE:
        start_button_rect, leaderboard_button_rect = draw_welcome_screen()
        
    elif current_state == LEADERBOARD_STATE:
        back_button_rect = draw_leaderboard()
        
    elif current_state == NAME_INPUT_STATE:
        submit_button_rect = draw_name_input()
        
    elif current_state == GAME_OVER_STATE:
        draw_game_over()
        
    elif current_state == GAME_STATE:
        # Water gradient background
        draw_gradient_background()

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
            current_state = GAME_OVER_STATE

        # Phase switching
        if now - phase_start_time > phase_duration:
            phase_start_time = now
            if current_phase == POP_PHASE:
                current_phase = BREATH_PHASE
                breath_start_time = now
                current_bubble = None
            else:
                current_phase = POP_PHASE

        # Update pop animations
        update_pop_animations()

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

        # Draw pop animations on top of everything
        draw_pop_animations()

        if show_affirmation and now - affirmation_start_time > affirmation_show_time:
            show_affirmation = False

        draw_ui()

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()