import pygame
from core.settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed=8):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = speed

    # core/sprites.py - DENTRO DA CLASSE BULLET (Método update)

class Bullet(pygame.sprite.Sprite):
    # ... (o método __init__ permanece o mesmo)

    def update(self):
        # 1. Converte o ângulo do PRÓPRIO projétil para radianos
        # ESTE É O AJUSTE CRÍTICO! Ele usa o self.angle passado no __init__
        rad = math.radians(self.angle)
        
        # 2. Calcula o movimento baseado no ângulo do projétil
        # Usa seno para X e cosseno para Y, com ajuste para o sistema Pygame.
        # Lembra-se que o ângulo 0 no Pygame é para cima? Seno ajusta X e Cosseno Y.
        self.rect.x += self.speed * math.sin(rad)
        self.rect.y -= self.speed * math.cos(rad) # Subtrai Y porque Y cresce para baixo
        
        # Reduz o delay
        if self.delay > 0:
            self.delay -= 1
        
        # Remove o projétil se sair da tela
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).contains(self.rect):
            self.kill()
