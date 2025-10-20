# tank/main.py

import pygame  # Garante que 'pygame' esteja definido
import sys
import math

# Importações Modulares (AGORA SEPARADAS EM LINHAS DIFERENTES)
from core.settings import *
from core.sprites import Bullet 
from core.ui import Scoreboard 

# --- CLASSE TANK (Com __init__ corrigido) ---
class Tank(pygame.sprite.Sprite): 
    
    def __init__(self, color, x, y, controls):
        super().__init__()
        
        # 1. CRIAÇÃO e DEFINIÇÃO de self.image (Solução do AttributeError)
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        
        # 2. DESENHO na Surface self.image
        pygame.draw.rect(self.image, color, (0, 0, 40, 60))
        
        # 3. CÓPIA para self.original_image (Base para rotação)
        self.original_image = self.image.copy() 
        
        # 4. DEFINIÇÃO do Retângulo
        self.rect = self.image.get_rect(center=(x, y))
        
        # 5. Outras Propriedades
        self.controls = controls
        self.fire_cooldown = 0
        self.angle = 0 
        self.speed = PLAYER_SPEED 
        self.rotation_speed = 3


    def rotate(self, angle_change):
        self.angle += angle_change
        self.angle %= 360
        original_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=original_center)
        
    def fire(self, bullets_group):
        if self.fire_cooldown <= 0:
            
            # Cálculo da ponta do canhão
            rad = math.radians(self.angle)
            muzzle_dist = 30 
            start_x = self.rect.centerx + muzzle_dist * math.sin(rad)
            start_y = self.rect.centery - muzzle_dist * math.cos(rad) 

            new_bullet = Bullet(start_x, start_y, self.angle, owner=self)
            bullets_group.add(new_bullet)
            self.fire_cooldown = 30 

    def update(self, keys, bullets_group, tanks_group=None):
        if keys[self.controls["left"]]: self.rotate(self.rotation_speed)
        if keys[self.controls["right"]]: self.rotate(-self.rotation_speed)
            
        current_speed = 0
        if keys[self.controls["forward"]]: current_speed = self.speed
        elif keys[self.controls["backward"]]: current_speed = -self.speed * 0.5
            
        if current_speed != 0:
            rad = math.radians(self.angle)
            dx = current_speed * math.sin(rad)
            dy = current_speed * math.cos(rad)
            self.rect.x += dx
            self.rect.y += dy
            
            # Colisão com tanques
            if tanks_group:
                for tank in tanks_group:
                    if tank != self and self.rect.colliderect(tank.rect):
                        self.rect.x -= dx
                        self.rect.y -= dy
                        break

        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if keys[self.controls["fire"]]:
            self.fire(bullets_group)

        if self.fire_cooldown > 0: self.fire_cooldown -= 1


# --- FUNÇÃO DE EXECUÇÃO DO JOGO ---
def run_tank_game():
    
    if not pygame.get_init():
        pygame.init()
        
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Combate - Tanques")
    clock = pygame.time.Clock()
    
    scoreboard = Scoreboard(screen) 

    controls_p1 = { "left": pygame.K_a, "right": pygame.K_d, "forward": pygame.K_w, "backward": pygame.K_s, "fire": pygame.K_SPACE }
    controls_p2 = { "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "forward": pygame.K_UP, "backward": pygame.K_DOWN, "fire": pygame.K_RETURN }

    tank1 = Tank(GREEN, 200, 300, controls_p1)
    tank2 = Tank(RED, 600, 300, controls_p2)

    tanks_group = pygame.sprite.Group(tank1, tank2)
    bullets_group = pygame.sprite.Group()

    running = True
    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False 

        tanks_group.update(keys, bullets_group, tanks_group) 
        bullets_group.update()
        
        for tank in tanks_group:
            hit_bullets = pygame.sprite.spritecollide(tank, bullets_group, False) 
            
            for bullet in hit_bullets:
                if bullet.owner != tank and bullet.delay == 0:
                    
                    if tank == tank1:
                        scoreboard.add_score(2) 
                    elif tank == tank2:
                        scoreboard.add_score(1) 
                    
                    bullet.kill()

        screen.fill(BLACK)
        tanks_group.draw(screen)
        bullets_group.draw(screen)
        scoreboard.draw() 

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    run_tank_game()
    pygame.quit()
    sys.exit()