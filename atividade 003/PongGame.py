import pygame

pygame.init()

bounce_sound = bounce_sound = pygame.mixer.Sound("sounds\\bounce.wav")

score_sound = pygame.mixer.Sound("sounds\git\pong-turtle_258020__kodack__arcade-bleep-sound.wav")


# cores
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

# constantes
SCORE_MAX = 11
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MyPong - PyGame Edition - 2024 (sem assets)")

# fonte do sistema
score_font = pygame.font.SysFont(None, 44)
victory_font = pygame.font.SysFont(None, 100)

# placar inicial
score_1 = 0
score_2 = 0

# player 1
player_1_x = 50
player_1_y = 300
player_width = 20
player_height = 150
player_speed = 5
player_1_move_up = False
player_1_move_down = False

# player 2 (robô)
player_2_x = SCREEN_WIDTH - 70
player_2_y = 300

# bola
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_radius = 15
ball_dx = 5
ball_dy = 5

# clock
game_loop = True
game_clock = pygame.time.Clock()

while game_loop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_loop = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_1_move_up = True
            if event.key == pygame.K_DOWN:
                player_1_move_down = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player_1_move_up = False
            if event.key == pygame.K_DOWN:
                player_1_move_down = False

    # verificando condição de vitória
    if score_1 < SCORE_MAX and score_2 < SCORE_MAX:

        # limpar tela
        screen.fill(COLOR_BLACK)

        # movimento da bola
        ball_x += ball_dx
        ball_y += ball_dy

        # colisão da bola com parede superior/inferior
        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= SCREEN_HEIGHT:
            ball_dy *= -1
            bounce_sound.play()

        # colisão da bola com player 1
        if (player_1_x < ball_x - ball_radius < player_1_x + player_width and
            player_1_y < ball_y < player_1_y + player_height):
            ball_dx *= -1
            bounce_sound.play()

        # colisão da bola com player 2
        if (player_2_x < ball_x + ball_radius < player_2_x + player_width and
            player_2_y < ball_y < player_2_y + player_height):
            ball_dx *= -1
            bounce_sound.play()

        # pontuação
        if ball_x < 0:
            score_2 += 1
            ball_x = SCREEN_WIDTH // 2
            ball_y = SCREEN_HEIGHT // 2
            ball_dx *= -1
            score_sound.play()
        elif ball_x > SCREEN_WIDTH:
            score_1 += 1
            ball_x = SCREEN_WIDTH // 2
            ball_y = SCREEN_HEIGHT // 2
            ball_dx *= -1
            score_sound.play()

        # movimento player 1
        if player_1_move_up:
            player_1_y -= player_speed
        if player_1_move_down:
            player_1_y += player_speed

        # limites da tela player 1
        if player_1_y < 0:
            player_1_y = 0
        if player_1_y > SCREEN_HEIGHT - player_height:
            player_1_y = SCREEN_HEIGHT - player_height

        # player 2 (robô segue a bola)
        if player_2_y + player_height // 2 < ball_y:
            player_2_y += 4
        elif player_2_y + player_height // 2 > ball_y:
            player_2_y -= 4

        # limites da tela player 2
        if player_2_y < 0:
            player_2_y = 0
        if player_2_y > SCREEN_HEIGHT - player_height:
            player_2_y = SCREEN_HEIGHT - player_height

        # desenhar bola
        pygame.draw.circle(screen, COLOR_WHITE, (ball_x, ball_y), ball_radius)

        # desenhar jogadores
        pygame.draw.rect(screen, COLOR_WHITE, (player_1_x, player_1_y, player_width, player_height))
        pygame.draw.rect(screen, COLOR_WHITE, (player_2_x, player_2_y, player_width, player_height))

        # desenhar placar
        score_text = score_font.render(f"{score_1} x {score_2}", True, COLOR_WHITE)
        score_text_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        screen.blit(score_text, score_text_rect)

    else:
        # desenhar tela de vitória
        screen.fill(COLOR_BLACK)
        victory_text = victory_font.render("VICTORY", True, COLOR_WHITE)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(victory_text, victory_rect)
        

        score_text = score_font.render(f"{score_1} x {score_2}", True, COLOR_WHITE)
        score_text_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(score_text, score_text_rect)

    pygame.display.flip()
    game_clock.tick(60)

pygame.quit()