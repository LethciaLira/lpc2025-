# warplane/main.py

import pygame
import sys
import math

# Importações Modulares (Aproveitando os mesmos módulos)
from core.settings import *
from core.sprites import Bullet  # Usaremos a mesma classe Bullet, mas chamaremos de Missile
from core.ui import Scoreboard 

# --- CLASSE WARPLANE ---
class Warplane(pygame.sprite.Sprite):
    
    def __init__(self, color, x, y, controls):
        super().__init__()
        
        # 1. CRIAÇÃO e DEFINIÇÃO de self.image
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Desenho de um triângulo simples (representando um avião de cima)
        points = [(20, 0), (40, 40), (0, 40)]
        pygame.draw.polygon(self.image, color, points)
        
        # 2. CÓPIA para self.original_image (Base para rotação)
        self.original_image = self.image.copy() 
        
        # 3. DEFINIÇÃO do Retângulo
        self.rect = self.image.get_rect(center=(x, y))
        
        # 4. Propriedades de Movimento e Controles
        self.controls = controls
        self.fire_cooldown = 0
        self.angle = 0 
        self.speed = 0.5  # Velocidade atual (constante para voo)
        self.rotation_speed = 3
        self.max_speed = 5
        self.acceleration = 0.05

    def rotate(self, angle_change):
        self.angle += angle_change
        self.angle %= 360
        original_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=original_center)
        
    def fire(self, missiles_group):
        if self.fire_cooldown <= 0:
            
            # Mísseis também saem da ponta do avião (metade da altura 40/2 = 20)
            rad = math.radians(self.angle)
            muzzle_dist = 20
            
            # Cálculo do ponto de saída
            start_x = self.rect.centerx + muzzle_dist * math.sin(rad)
            start_y = self.rect.centery - muzzle_dist * math.cos(rad) 

            # Usamos a classe Bullet, mas a chamamos de Míssil
            new_missile = Bullet(start_x, start_y, self.angle, owner=self)
            missiles_group.add(new_missile)
            self.fire_cooldown = 20 # Cooldown um pouco menor

    def update(self, keys, missiles_group, planes_group=None):
        # Rotação (Esquerda/Direita)
        if keys[self.controls["left"]]: self.rotate(self.rotation_speed)
        if keys[self.controls["right"]]: self.rotate(-self.rotation_speed)
            
        # Controle de Aceleração (Aumenta ou diminui a velocidade base)
        if keys[self.controls["forward"]]:
            self.speed = min(self.max_speed, self.speed + self.acceleration)
        elif keys[self.controls["backward"]]:
            self.speed = max(0.5, self.speed - self.acceleration) # Velocidade mínima para voar
            
        # Movimento Contínuo (Voo)
        rad = math.radians(self.angle)
        dx = self.speed * math.sin(rad)
        dy = self.speed * math.cos(rad)
        self.rect.x += dx
        self.rect.y += dy
        
        # Colisão com outros aviões (apenas para evitar que fiquem exatamente no mesmo lugar)
        if planes_group:
            for plane in planes_group:
                if plane != self and self.rect.colliderect(plane.rect):
                    self.rect.x -= dx * 0.5 # Empurra de volta, suavemente
                    self.rect.y -= dy * 0.5
                    break

        # Limite da Tela (O avião pode sumir se sair, ou pode quicar. Optamos por quicar/limitar)
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if keys[self.controls["fire"]]:
            self.fire(missiles_group)

        if self.fire_cooldown > 0: self.fire_cooldown -= 1


# --- FUNÇÃO DE EXECUÇÃO DO JOGO DE AVIÕES ---
def run_warplane_game():
    
    if not pygame.get_init():
        pygame.init()
        
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Combate - Aéreo")
    clock = pygame.time.Clock()
    
    scoreboard = Scoreboard(screen) 

    # Controles do P1 (A, W, D, S, SPACE)
    controls_p1 = { "left": pygame.K_a, "right": pygame.K_d, "forward": pygame.K_w, "backward": pygame.K_s, "fire": pygame.K_SPACE }
    # Controles do P2 (Setas + RETURN/ENTER)
    controls_p2 = { "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "forward": pygame.K_UP, "backward": pygame.K_DOWN, "fire": pygame.K_RETURN }

    # Criação dos aviões
    plane1 = Warplane(GREEN, 200, 300, controls_p1)
    plane2 = Warplane(BLUE, 600, 300, controls_p2) # Usamos BLUE para o avião P2

    planes_group = pygame.sprite.Group(plane1, plane2)
    missiles_group = pygame.sprite.Group() # Grupo para os mísseis

    running = True
    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False 

        # Atualiza aviões e mísseis
        planes_group.update(keys, missiles_group, planes_group) 
        missiles_group.update()
        
        # Colisões Míssil vs. Aviões
        for plane in planes_group:
            hit_missiles = pygame.sprite.spritecollide(plane, missiles_group, False) 
            
            for missile in hit_missiles:
                if missile.owner != plane and missile.delay == 0:
                    
                    if plane == plane1:
                        scoreboard.add_score(2) # P2 pontuou
                    elif plane == plane2:
                        scoreboard.add_score(1) # P1 pontuou
                    
                    missile.kill()

        screen.fill(BLACK)
        planes_group.draw(screen)
        missiles_group.draw(screen)
        scoreboard.draw() 

        pygame.display.flip()
        clock.tick(FPS)
    
    # Nota: Não chamamos pygame.quit() para permitir o retorno ao menu

if __name__ == "__main__":
    # Rodar diretamente
    run_warplane_game()
    pygame.quit()
    sys.exit()
