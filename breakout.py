import pygame
import sys
import os
import random
import math

pygame.init()

# Paths
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

# Sounds
try:
    bounce_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "bounce.wav"))
except:
    bounce_sound = None

try:
    score_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "258020_kodack_arcade-bleep-sound.wav"))
except:
    score_sound = None

# Text
try:
    score_font = pygame.font.Font(os.path.join(ASSETS_PATH, "PressStart2P.ttf"), 30)
    menu_font = pygame.font.Font(os.path.join(ASSETS_PATH, "PressStart2P.ttf"), 45)
except:
    score_font = pygame.font.SysFont("Arial", 44)
    menu_font = pygame.font.SysFont("Arial", 60)

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_ORANGE = (255, 190, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLUE = (0, 0, 255)

# Speed table by color
speed_boost = {
    COLOR_YELLOW: 1.1, 
    COLOR_GREEN: 1.2,  
    COLOR_ORANGE: 1.3,
    COLOR_RED: 1.4    }


# Constants
SCREEN_WIDTH = 906
SCREEN_HEIGHT = 800
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 14
BALL_SIZE = 10
BLOCK_WIDTH = 60
BLOCK_HEIGHT = 10

# Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BREAKOUT")
clock = pygame.time.Clock()

# Function for menu
def show_menu():
    waiting = True
    blocks = create_blocks()

    while waiting:
        screen.fill(COLOR_BLACK)

        # Draw the blocks in menu
        for block in blocks:
            if block["visible"]:
                pygame.draw.rect(screen, block["color"], block["rect"])

        title_text = menu_font.render("BREAKOUT", True, COLOR_WHITE)
        screen.blit(title_text, (SCREEN_WIDTH //2 - title_text.get_width()//2, 400))

        # Flashes text effect
        time_now = pygame.time.get_ticks()
        if (time_now // 500) % 2 == 0:
            start_text = score_font.render("Press SPACE to Play", True, COLOR_WHITE)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2,550))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# Create blocks
def create_blocks(rows=8, cols=14, spacing=5, top_offset=200):
    blocks = []
    # Colors organized by layers, from top (harder) to bottom (easier)
    colors = [COLOR_RED, COLOR_ORANGE, COLOR_GREEN, COLOR_YELLOW]
    for row in range(rows):
        for col in range(cols):
            x = col * (BLOCK_WIDTH + spacing)
            y = row * (BLOCK_HEIGHT + spacing) + top_offset
            rect = pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
            # Set the color based on the layer (every two lines)
            color = colors[(row // 2) % len(colors)]
            blocks.append({"rect": rect, "color": color, "visible": True})
    return blocks

# Function to reset the positions of the ball and paddle
def reset_positions(paddle_rect, ball_rect):
    """Reseta a bola para o centro do paddle, mas não lança."""
    # Reposition the paddle to the center (standard width)
    paddle_rect.width = PADDLE_WIDTH 
    paddle_rect.x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
    # Repositions the ball at the center of the paddle
    ball_rect.x = paddle_rect.centerx - BALL_SIZE // 2
    ball_rect.y = paddle_rect.top - BALL_SIZE
    return False # launched = False

# Helper function to generate the launch speed
def generate_launch_speed(base_speed=4):
    """Gera o vetor de velocidade para um de três lançamentos: Cima, Diag. Esq. ou Diag. Dir."""
    
    # 3 options: 0 (Up), 1 (Diagonal Left), 2 (Diagonal Right)
    choice = random.randint(0, 2) 

    # Vertical velocity is always negative (upwards)
    vy = -base_speed 

    if choice == 0:
        # Up (Vector X zero)
        vx = 0
        vy = -base_speed
    elif choice == 1:
        # Diagonal Left (Vector X negative)
        vx = -3.5 
        vy = -3.5 

    else: # choice == 2
        # Diagonal Right (Vector X positive)
        vx = 3.5 
        vy = -3.5 
        
    return [vx, vy]


# Game loop
def game_loop():
    paddle = pygame.Rect(
        SCREEN_WIDTH//2 - PADDLE_WIDTH//2,  # x: horizontal center
        SCREEN_HEIGHT - 50,                 # y: near the bottom
        PADDLE_WIDTH,
        PADDLE_HEIGHT
    )
    paddle_color = COLOR_BLUE
    # The ball starts in the center of the paddle
    ball = pygame.Rect(paddle.centerx - BALL_SIZE//2, paddle.top - BALL_SIZE, BALL_SIZE, BALL_SIZE)
    
    # State variables
    speed = 4
    # The initial speed is defined neutrally before the first launch
    ball_speed = [0, 0] 

    score = 0
    lives = 3 
    launched = False 
    spectator_mode = False 

    blocks = create_blocks()
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                # Throwing the ball (only works if it hasn't been thrown and is not in spectator mode)
                if event.key == pygame.K_SPACE and not launched and not spectator_mode:
                    launched = True
                    # Define the speed based on the 3-way launch function
                    ball_speed = generate_launch_speed(base_speed=4) 
                
                # Quit or restart in spectator mode
                if event.key == pygame.K_SPACE and spectator_mode:
                    return True # Back to menu/restart
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        # Player moviment keys
        keys = pygame.key.get_pressed()
        
        # Allows Movement only if: 1. You are not in spectator mode AND 2. The ball has been thrown
        if not spectator_mode and launched:
            if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
                paddle.x += 7
            if keys[pygame.K_LEFT] and paddle.left > 0:
                paddle.x -= 7
        
        # Locks ball with the paddle
        if not launched:
            ball.x = paddle.centerx - BALL_SIZE//2
            ball.y = paddle.top - BALL_SIZE
        else:
            # Ball moviment
            ball.x += ball_speed[0]
            ball.y += ball_speed[1]

            # Colision with the top
            if ball.top <= 0:
                ball_speed[1] *= -1
                if bounce_sound: bounce_sound.play()

            # Colision with sides
            if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
                ball_speed[0] *= -1
                if bounce_sound: bounce_sound.play()
            
            # Colision with paddle 
            if ball.colliderect(paddle):
                # If it's the stretched paddle, just reflect it vertically
                if spectator_mode:
                    ball_speed[1] *= -1
                # If it's the normal paddle, apply dynamic rebound
                elif ball_speed[1] > 0: # Only bounces off if the ball is descendo going down
                    ball_speed[1] *= -1
                    hit_pos = (ball.centerx - paddle.left) / PADDLE_WIDTH
                    ball_speed[0] = (hit_pos - 0.5) * 10 # Bounces off based on position
                if bounce_sound: bounce_sound.play()

            # Colisão with blocks
            for block in blocks:
                if block["visible"] and ball.colliderect(block["rect"]):
                    
                    # The ball only breaks the block if it is not in spectator mode
                    if not spectator_mode:
                        block["visible"] = False

                    # Colision logic
                    if abs(ball.bottom - block["rect"].top) < 10 and ball_speed[1] > 0:
                        ball_speed[1] *= -1
                    elif abs(ball.top - block["rect"].bottom) < 10 and ball_speed[1] < 0:
                        ball_speed[1] *= -1
                    elif abs(ball.right - block["rect"].left) < 10 and ball_speed[0] > 0:
                        ball_speed[0] *= -1
                    elif abs(ball.left - block["rect"].right) < 10 and ball_speed[0] < 0:
                        ball_speed[0] *= -1

                    # Acceleration and speed limit ONLY occur if it is not spectator mode
                    if not spectator_mode:
                        # Applys boosts
                        if block["color"] in speed_boost:
                            ball_speed[0] *= speed_boost[block["color"]]
                            ball_speed[1] *= speed_boost[block["color"]]

                        # Speed limit
                        max_speed_by_color = {COLOR_YELLOW: 5, COLOR_GREEN: 6, COLOR_ORANGE: 7, COLOR_RED: 8}
                        if block["color"] in max_speed_by_color:
                            max_s = max_speed_by_color[block["color"]]
                            # Ensures that the speed does not exceed the limit by color
                            ball_speed[0] = max_s * (ball_speed[0] / abs(ball_speed[0])) if abs(ball_speed[0]) > max_s else ball_speed[0]
                            ball_speed[1] = max_s * (ball_speed[1] / abs(ball_speed[1])) if abs(ball_speed[1]) > max_s else ball_speed[1]

                        # Points
                        if block["color"] == COLOR_YELLOW: score += 1
                        elif block["color"] == COLOR_ORANGE: score += 5
                        elif block["color"] == COLOR_GREEN: score += 3
                        elif block["color"] == COLOR_RED: score += 7

                    if score_sound: score_sound.play()
                    break

            # Life loss logic
            if not spectator_mode and ball.bottom >= SCREEN_HEIGHT:
                lives -= 1
                if lives <= 0:
                    spectator_mode = True # Game Over!
                    
                    # Reposition the ball to the center of the screen
                    ball.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
                    ball.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
                    
                    # Stretch the paddle to cover the exit
                    paddle.width = SCREEN_WIDTH
                    paddle.x = 0
                else:
                    # You lost a life, reset the position (to the center)
                    launched = reset_positions(paddle, ball)
                    # Set the initial speed, but don't launch yet
                    ball_speed = generate_launch_speed(base_speed=4)
            
            # If the ball goes out at the bottom in SPECTATOR MODE (bounces off the extended paddle)
            elif spectator_mode and ball.bottom >= SCREEN_HEIGHT:
                 ball_speed[1] *= -1
                 if bounce_sound: bounce_sound.play()


        # --- Draws ---
        screen.fill(COLOR_BLACK)
        
        # Draw blocks
        for block in blocks:
            if block["visible"]:
                pygame.draw.rect(screen, block["color"], block["rect"])
        
        # Draw the paddle (red if is on the spectator mode)
        paddle_draw_color = COLOR_RED if spectator_mode else paddle_color
        pygame.draw.rect(screen, paddle_draw_color, paddle)
        
        # Draw the ball
        pygame.draw.ellipse(screen, COLOR_WHITE, ball)


        # Score flashes
        time_now = pygame.time.get_ticks()
        score_color = COLOR_WHITE if (time_now // 500) % 2 == 0 else COLOR_BLACK
        
        # Score and Lives display
        score_label = score_font.render(f"SCORE:", True, COLOR_WHITE)
        screen.blit(score_label, (20, 10)) 
        score_text = score_font.render(f" {score} ", True, score_color)
        screen.blit(score_text, (20 + score_label.get_width() + 10, 10)) 

        lives_text = score_font.render(f"LIVES: {lives}", True, COLOR_WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 10)) 

        # Spectator mode text
        if spectator_mode:
             msg_text = menu_font.render("GAME OVER", True, COLOR_RED)
             # Centered at Y=380
             screen.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
             
             restart_text = score_font.render("SPACE to Restart/Q to Quit", True, COLOR_WHITE)
             # Positioned 50 pixels below the center Y=400 (at Y=430)
             screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 30))


        pygame.display.flip()

    return True 

# Main loop
while True:
    show_menu()
    play_again = game_loop()
    if play_again is False:
        pygame.quit()
        sys.exit()
