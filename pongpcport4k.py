# test.py
#
# To run this game, you need to have Pygame and NumPy installed.
# Open your terminal or command prompt and type:
# pip install pygame numpy

import pygame
import sys
import random
import numpy

# --- Game Setup ---
# Initialize mixer first to control its settings
pygame.mixer.pre_init(44100, -16, 2, 512) # Forcing stereo with 2 channels
pygame.init()

SCREEN_WIDTH = 854
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("VIBE PONG")
clock = pygame.time.Clock()
game_font = pygame.font.Font(None, 40)

# --- Sound Generation (No Files Needed) ---
def generate_beep(frequency, duration, volume=0.15):
    """Generates a simple sine wave beep."""
    sample_rate = pygame.mixer.get_init()[0]
    n_samples = int(round(duration * sample_rate))
    
    # Create a 1D mono buffer first
    buf = numpy.zeros((n_samples,), dtype=numpy.int16)
    max_sample = 2**(pygame.mixer.get_init()[1] * -1 - 1) - 1
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        buf[i] = int(round(max_sample * volume * numpy.sin(2 * numpy.pi * frequency * t)))
        
    # --- FIX IS HERE ---
    # Convert the 1D mono buffer to a 2D stereo buffer by stacking it
    stereo_buf = numpy.c_[buf, buf]
    
    return pygame.sndarray.make_sound(stereo_buf)

# Beeps n Boops
beep_sound = generate_beep(frequency=440.0, duration=0.05) # A4 note for bounces
boop_sound = generate_beep(frequency=587.33, duration=0.2) # D5 note for scores

# --- Game Objects and Variables ---
BALL_RADIUS = 8
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100

ball = pygame.Rect(SCREEN_WIDTH / 2 - BALL_RADIUS, SCREEN_HEIGHT / 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
player = pygame.Rect(10, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ai = pygame.Rect(SCREEN_WIDTH - 10 - PADDLE_WIDTH, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Colors (PS2 Vibes)
BG_COLOR = pygame.Color('grey12')
FG_COLOR = pygame.Color('whitesmoke')

# Game State
ball_speed_x = 6 * random.choice((1, -1))
ball_speed_y = 6 * random.choice((1, -1))
player_score = 0
ai_score = 0
score_limit = 5
game_over = False
winner_text = ""

def reset_ball():
    """Resets the ball to the center with a random direction."""
    global ball_speed_x, ball_speed_y
    ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    ball_speed_y = 6 * random.choice((1, -1))
    ball_speed_x = 6 * random.choice((1, -1))

# --- Main Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                player_score = 0
                ai_score = 0
                reset_ball()
                game_over = False
            if event.key == pygame.K_n:
                pygame.quit()
                sys.exit()

    if not game_over:
        # --- Game Logic ---
        # Ball Movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Player Control (Mouse)
        player.y = pygame.mouse.get_pos()[1] - PADDLE_HEIGHT / 2
        if player.top < 0:
            player.top = 0
        if player.bottom > SCREEN_HEIGHT:
            player.bottom = SCREEN_HEIGHT

        # AI Control
        ai_speed = 5
        if ai.centery < ball.centery:
            ai.y += ai_speed
        if ai.centery > ball.centery:
            ai.y -= ai_speed
        if ai.top < 0:
            ai.top = 0
        if ai.bottom > SCREEN_HEIGHT:
            ai.bottom = SCREEN_HEIGHT

        # Collision Detection
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_speed_y *= -1
            beep_sound.play()

        if ball.colliderect(player) and ball_speed_x < 0:
            ball_speed_x *= -1
            beep_sound.play()
        
        if ball.colliderect(ai) and ball_speed_x > 0:
            ball_speed_x *= -1
            beep_sound.play()

        # Scoring
        if ball.left <= 0:
            ai_score += 1
            boop_sound.play()
            reset_ball()

        if ball.right >= SCREEN_WIDTH:
            player_score += 1
            boop_sound.play()
            reset_ball()
        
        # Check for Game Over
        if player_score >= score_limit:
            game_over = True
            winner_text = "PLAYER 1 WINS"
        if ai_score >= score_limit:
            game_over = True
            winner_text = "AI WINS"

    # --- Drawing ---
    screen.fill(BG_COLOR)
    
    # Center Line
    pygame.draw.aaline(screen, FG_COLOR, (SCREEN_WIDTH / 2, 0), (SCREEN_WIDTH / 2, SCREEN_HEIGHT))

    if game_over:
        winner_surf = game_font.render(winner_text, True, FG_COLOR)
        winner_rect = winner_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        
        prompt_surf = game_font.render("PLAY AGAIN? (Y/N)", True, FG_COLOR)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20))
        
        screen.blit(winner_surf, winner_rect)
        screen.blit(prompt_surf, prompt_rect)
    else:
        # Draw game objects
        pygame.draw.rect(screen, FG_COLOR, player)
        pygame.draw.rect(screen, FG_COLOR, ai)
        pygame.draw.ellipse(screen, FG_COLOR, ball)

        # Draw scores
        player_text = game_font.render(f"{player_score}", True, FG_COLOR)
        screen.blit(player_text, (SCREEN_WIDTH / 2 - 50, 20))

        ai_text = game_font.render(f"{ai_score}", True, FG_COLOR)
        screen.blit(ai_text, (SCREEN_WIDTH / 2 + 30, 20))

    # --- Update Screen ---
    pygame.display.flip()
    clock.tick(60)
