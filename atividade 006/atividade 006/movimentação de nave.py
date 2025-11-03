import pygame
import sys
import math
import os

pygame.init()

# === CORES ===
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# === TELA ===
screen_width, screen_height = 500, 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Movimentação de Nave")

# === LOCALIZAÇÃO DO ARQUIVO ===
base_path = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_path, "assets", "look.png")


print("Procurando imagem em:", image_path)

# === CARREGAR IMAGEM ===
try:
    image = pygame.image.load(image_path).convert_alpha()
    print("Imagem carregada com sucesso!")
except pygame.error as e:
    print(f"Erro ao carregar a imagem da nave: {e}")
    print("Usando forma triangular substituta.")
    image = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.polygon(image, WHITE, [(30, 0), (50, 60), (10, 60)])

# === AJUSTE DE TAMANHO ===
image = pygame.transform.scale(image, (60, 60))

# === POSIÇÃO E MOVIMENTO ===
position_x = screen_width // 2
position_y = screen_height // 2
angle = 0
rotation_speed = 3
move_speed = 0
acceleration = 0.2

# === FLAG DE FREIO ===
BRAKE = 1  # 0 = continua andando, 1 = só anda enquanto segura ↑

# === LOOP PRINCIPAL ===
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # --- ROTACIONAR ---
    if keys[pygame.K_LEFT]:
        angle += rotation_speed
    if keys[pygame.K_RIGHT]:
        angle -= rotation_speed

    # --- MOVER ---
    if keys[pygame.K_UP]:
        move_speed += acceleration
    else:
        if BRAKE == 1:
            move_speed = 0

    # Calcula deslocamento
    angle_rad = math.radians(angle)
    position_x += move_speed * math.cos(angle_rad)
    position_y -= move_speed * math.sin(angle_rad)

    # Mantém dentro da tela
    position_x %= screen_width
    position_y %= screen_height

    # --- ROTAÇÃO VISUAL ---
    rotated_image = pygame.transform.rotate(image, angle - 90)
    rotated_rect = rotated_image.get_rect(center=(position_x, position_y))

    # --- DESENHAR ---
    screen.fill(BLUE)
    screen.blit(rotated_image, rotated_rect)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
