# core/sprites.py

import pygame
import math
from core.settings import *

# CLASSE BASE COMUM: GameSprite
class GameSprite(pygame.sprite.Sprite):
    # Mantemos esta classe como base para modularidade, mesmo que não a usemos para carregar imagens agora.
    def __init__(self, *args):
        super().__init__()
        # Se for desenhar, ela deve ser sobrescrita pelo Tank ou Warplane.

# CLASSE BULLET (Corrigida com owner e delay)
class Bullet(pygame.sprite.Sprite):
    # CRÍTICO: Agora aceita 'owner'
    def __init__(self, x, y, angle, owner): 
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(YELLOW) 
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = BULLET_SPEED
        
        self.owner = owner 
        self.delay = 10    # 10 frames de invulnerabilidade ao próprio dono

    def update(self):
        rad = math.radians(self.angle)
        self.rect.x += self.speed * math.sin(rad)
        self.rect.y += self.speed * math.cos(rad)
        
        if self.delay > 0:
            self.delay -= 1
        
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).contains(self.rect):
            self.kill()
