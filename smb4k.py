# Super Mario Bros. 2025 PC Port
# Engine: Pygame
# Graphics: Procedural (vibes=on, files=off)
# FPS: 60

import pygame
import sys

# --- Initialization ---
pygame.init()

# --- Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Colors ---
BACKGROUND_COLOR = (107, 140, 255) # Sky Blue
PLAYER_COLOR = (255, 0, 0)         # Red
GROUND_COLOR = (222, 138, 54)      # Brown
BRICK_COLOR = (181, 71, 0)         # Dark Orange
ENEMY_COLOR = (124, 66, 11)        # Goomba Brown
TEXT_COLOR = (255, 255, 255)

# --- Game Physics & Player Stats ---
GRAVITY = 0.8
PLAYER_ACC = 0.7
PLAYER_FRICTION = -0.12
PLAYER_JUMP_STRENGTH = -18

# --- Screen Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros. 2025")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 40))
        self.surf.fill(PLAYER_COLOR)
        self.rect = self.surf.get_rect(center=(100, SCREEN_HEIGHT - 100))
        
        # Vectors for motion
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        self.is_grounded = False

    def move(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acc.x = PLAYER_ACC
            
        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        
        # Equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        
        # Screen boundary
        if self.pos.x > SCREEN_WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = SCREEN_WIDTH
            
        self.rect.topleft = self.pos

    def jump(self):
        if self.is_grounded:
            self.vel.y = PLAYER_JUMP_STRENGTH
            self.is_grounded = False

    def update(self, platforms):
        self.move()
        self.check_collision(platforms)

    def check_collision(self, platforms):
        # Vertical Collision
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1
        
        if self.vel.y > 0 and hits:
            platform = hits[0]
            if self.rect.bottom < platform.rect.bottom:
                self.pos.y = platform.rect.top - self.rect.height
                self.vel.y = 0
                self.is_grounded = True
        
        # Horizontal Collision
        self.rect.x += self.vel.x
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            platform = hits[0]
            # Moving right
            if self.vel.x > 0:
                self.rect.right = platform.rect.left
            # Moving left
            if self.vel.x < 0:
                self.rect.left = platform.rect.right
            self.pos.x = self.rect.x

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        super().__init__()
        self.surf = pygame.Surface((w, h))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(topleft=(x, y))

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.surf = pygame.Surface((32, 32))
        self.surf.fill(ENEMY_COLOR)
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.speed = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 200 or self.rect.right > 600:
            self.speed *= -1

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# --- Level Creation ---
player = Player()
all_sprites.add(player)

# Ground
ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, GROUND_COLOR)
platforms.add(ground)
all_sprites.add(ground)

# Add some platforms
level_layout = [
    (200, SCREEN_HEIGHT - 120, 120, 40),
    (400, SCREEN_HEIGHT - 200, 120, 40),
    (550, SCREEN_HEIGHT - 320, 80, 40),
]
for x, y, w, h in level_layout:
    p = Platform(x, y, w, h, BRICK_COLOR)
    platforms.add(p)
    all_sprites.add(p)

# Add an enemy
enemy = Enemy(350, SCREEN_HEIGHT - 72)
enemies.add(enemy)
all_sprites.add(enemy)

# --- Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_SPACE or event.key == pygame.K_w:
                player.jump()

    # --- Updates ---
    player.update(platforms)
    enemies.update()

    # Enemy collision
    enemy_hit = pygame.sprite.spritecollideany(player, enemies)
    if enemy_hit:
        # Check for stomp
        if player.vel.y > 1 and player.rect.bottom < enemy_hit.rect.centery:
            enemy_hit.kill() # Enemy is defeated
        else:
            # Player is hit, reset for simplicity
            player.pos = pygame.math.Vector2(100, SCREEN_HEIGHT - 100)
            player.vel = pygame.math.Vector2(0, 0)


    # --- Drawing ---
    screen.fill(BACKGROUND_COLOR)
    
    # Draw all sprites
    for sprite in all_sprites:
        screen.blit(sprite.surf, sprite.rect)

    # --- Display FPS (optional) ---
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, TEXT_COLOR)
    screen.blit(fps_text, (10, 10))

    # --- Flip Display ---
    pygame.display.flip()

    # --- Tick Clock ---
    clock.tick(FPS)

# --- Quit ---
pygame.quit()
sys.exit()
