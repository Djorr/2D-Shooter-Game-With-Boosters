import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Shooter Game with Boosters and Faster Mechanics")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game variables
PLAYER_SIZE = 50
ENEMY_SIZE = 50
BOOSTER_SIZE = 20
BOMB_SIZE = 15  # Larger size for bomb
PLAYER_HEALTH = 100
ENEMY_HEALTH = 30
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2 * PLAYER_SIZE]
enemy_list = []
bullet_list = []
booster_list = []
score = 0
bullet_speed = 20
player_speed = 15  # Increased player speed for faster movement
enemy_speed = 2  # Slower initial speed for enemies
max_enemy_speed = 5  # Maximum speed for enemies
wave = 1
enemies_to_spawn = 5
triple_shot = False
bomb = False
booster_message = None
booster_timer = 0
triple_shot_timer = 0  # To track triple shot duration
last_shot_time = 0  # To control rapid fire

# Fonts
font = pygame.font.SysFont("monospace", 35)
small_font = pygame.font.SysFont("monospace", 20)


# Functions
def spawn_enemy():
    if len(enemy_list) < enemies_to_spawn:
        x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
        y = 0
        enemy_list.append([x, y, ENEMY_HEALTH])


def draw_enemies():
    for enemy in enemy_list:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], ENEMY_SIZE, ENEMY_SIZE))
        health_text = small_font.render(str(enemy[2]), True, WHITE)
        screen.blit(health_text, (enemy[0], enemy[1] - 20))


def update_enemy_positions():
    global PLAYER_HEALTH
    for enemy in enemy_list[:]:
        enemy[1] += enemy_speed
        if enemy[1] >= SCREEN_HEIGHT:
            enemy_list.remove(enemy)
            PLAYER_HEALTH -= 10  # Health decreases only if an enemy reaches the bottom


def spawn_booster():
    booster_type = random.choice(["triple_shot", "bomb"])
    x = random.randint(0, SCREEN_WIDTH - BOOSTER_SIZE)
    y = 0
    booster_list.append({"type": booster_type, "pos": [x, y]})


def draw_boosters():
    for booster in booster_list:
        color = BLUE if booster["type"] == "triple_shot" else YELLOW
        pygame.draw.circle(screen, color, booster["pos"], BOOSTER_SIZE // 2)


def update_booster_positions():
    for booster in booster_list[:]:
        booster["pos"][1] += 3
        if booster["pos"][1] >= SCREEN_HEIGHT:
            booster_list.remove(booster)


def activate_booster(booster_type):
    global triple_shot, bomb, booster_message, booster_timer, triple_shot_timer
    if booster_type == "triple_shot":
        triple_shot = True
        booster_message = "Triple Shot Activated!"
        triple_shot_timer = pygame.time.get_ticks()  # Start 10-second timer
    elif booster_type == "bomb":
        bomb = True
        booster_message = "Bomb Activated!"
    booster_timer = pygame.time.get_ticks()


def check_booster_collision():
    for booster in booster_list[:]:
        if detect_collision(player_pos, booster["pos"], BOOSTER_SIZE):
            activate_booster(booster["type"])
            booster_list.remove(booster)


def shoot_bullet():
    global bomb, triple_shot
    center_x = player_pos[0] + PLAYER_SIZE // 2
    if bomb:
        # Fire a bomb and deactivate bomb power-up
        bullet_list.append({"pos": [center_x, player_pos[1]], "type": "bomb"})
        bomb = False
    elif triple_shot:
        # Fire three bullets in a spread pattern
        bullet_list.append({"pos": [center_x, player_pos[1]], "angle": 0})
        bullet_list.append({"pos": [center_x, player_pos[1]], "angle": -45})
        bullet_list.append({"pos": [center_x, player_pos[1]], "angle": 45})
    else:
        # Normal bullet
        bullet_list.append({"pos": [center_x, player_pos[1]], "angle": 0})


def update_bullets():
    for bullet in bullet_list[:]:
        bullet_pos = bullet["pos"]
        if bullet.get("type") == "bomb":
            # Bomb moves slower and has a larger size
            bullet_pos[1] -= bullet_speed // 2
            if bullet_pos[1] < 0:
                bullet_list.remove(bullet)
        else:
            # Calculate the new position based on angle
            angle_rad = math.radians(bullet["angle"])
            bullet_pos[0] += bullet_speed * math.sin(angle_rad)
            bullet_pos[1] -= bullet_speed * math.cos(angle_rad)
            if bullet_pos[1] < 0 or bullet_pos[0] < 0 or bullet_pos[0] > SCREEN_WIDTH:
                bullet_list.remove(bullet)


def detect_collision(obj1, obj2, size):
    return (obj1[0] < obj2[0] + size and
            obj1[0] + PLAYER_SIZE > obj2[0] and
            obj1[1] < obj2[1] + size and
            obj1[1] + PLAYER_SIZE > obj2[1])


def check_bullet_collision():
    global score
    for bullet in bullet_list[:]:
        bullet_pos = bullet["pos"]
        if bullet.get("type") == "bomb":
            # If a bomb hits any enemy, destroy all enemies on screen
            for enemy in enemy_list[:]:
                if detect_collision(bullet_pos, enemy, ENEMY_SIZE):
                    score += len(enemy_list)  # Increase score by number of enemies cleared
                    enemy_list.clear()
                    bullet_list.remove(bullet)
                    break
        else:
            # Normal bullet or triple shot bullet
            for enemy in enemy_list[:]:
                if detect_collision(bullet_pos, enemy, ENEMY_SIZE):
                    enemy[2] -= 10  # Normal bullet damage
                    if enemy[2] <= 0:
                        enemy_list.remove(enemy)
                        score += 1  # Increase score by 1 for each enemy defeated
                    bullet_list.remove(bullet)
                    break


def next_wave():
    global wave, enemies_to_spawn, enemy_speed
    wave += 1
    enemies_to_spawn += 3  # Increase enemy count with each wave
    if enemy_speed < max_enemy_speed:  # Increase speed until max speed
        enemy_speed += 1


def display_booster_message():
    global booster_message
    if booster_message:
        message_text = small_font.render(booster_message, True, WHITE)
        screen.blit(message_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        if pygame.time.get_ticks() - booster_timer > 2000:
            booster_message = None


def display_wave_message():
    wave_text = font.render(f"Wave {wave}", True, WHITE)
    screen.blit(wave_text, (SCREEN_WIDTH // 2 - 50, 50))


def reset_game():
    global PLAYER_HEALTH, player_pos, enemy_list, bullet_list, booster_list, score, wave, enemies_to_spawn, enemy_speed, triple_shot, bomb
    PLAYER_HEALTH = 100
    player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2 * PLAYER_SIZE]
    enemy_list = []
    bullet_list = []
    booster_list = []
    score = 0
    wave = 1
    enemies_to_spawn = 5
    enemy_speed = 2
    triple_shot = False
    bomb = False


def display_game_over():
    game_over_text = font.render("Game Over", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 40))
    play_again_text = font.render("Play Again", True, WHITE)
    play_again_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20, 160, 40)
    pygame.draw.rect(screen, BLUE, play_again_rect)
    screen.blit(play_again_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 25))
    return play_again_rect


# Main game loop
clock = pygame.time.Clock()
game_over = False

while True:
    if game_over:
        screen.fill(BLACK)
        play_again_rect = display_game_over()
        pygame.display.update()

        # Check for play again button click
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    reset_game()
                    game_over = False
        continue

    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Continuous shooting with spacebar held down
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time > 150:  # Faster shooting rate with shorter delay
            shoot_bullet()
            last_shot_time = current_time

    # Player movement
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] and player_pos[0] < SCREEN_WIDTH - PLAYER_SIZE:
        player_pos[0] += player_speed

    # Enemy and booster logic
    spawn_enemy()
    if random.randint(1, 400) == 1:  # Adjust spawn rate for boosters
        spawn_booster()
    update_enemy_positions()
    draw_enemies()
    update_booster_positions()
    draw_boosters()
    check_booster_collision()

    # Bullet logic
    update_bullets()
    check_bullet_collision()

    # Triple shot timer check
    if triple_shot and pygame.time.get_ticks() - triple_shot_timer > 10000:
        triple_shot = False

    # Check wave completion
    if len(enemy_list) == 0:
        next_wave()

    # Draw player, bullets, and HUD
    pygame.draw.rect(screen, GREEN, (player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE))
    for bullet in bullet_list:
        bullet_pos = bullet["pos"]
        color = YELLOW if bullet.get("type") == "bomb" else WHITE
        size = BOMB_SIZE if bullet.get("type") == "bomb" else 5
        pygame.draw.rect(screen, color, (*bullet_pos, size, size))

    # Display health, score, wave, and booster message
    health_text = font.render(f"Health: {PLAYER_HEALTH}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
    display_booster_message()
    display_wave_message()

    # Check game over
    if PLAYER_HEALTH <= 0:
        game_over = True

    pygame.display.update()
    clock.tick(30)
