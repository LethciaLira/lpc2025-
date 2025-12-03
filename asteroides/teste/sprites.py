import pygame as pg
from PIL import Image
from utils import Vec
import math
import random

def load_gif(path, scale=1):
    gif = Image.open(path)
    frames = []

    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_img = gif.convert("RGBA")
        frame_pg = pg.image.fromstring(frame_img.tobytes(), frame_img.size, "RGBA")

        if scale != 1:
            w = int(frame_pg.get_width() * scale)
            h = int(frame_pg.get_height() * scale)
            frame_pg = pg.transform.scale(frame_pg, (w, h))

        frames.append(frame_pg)

    return frames


class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self, pos, gif_path, scale=1, fps=12):
        super().__init__()
        self.frames = load_gif(gif_path, scale)
        self.frame_index = 0
        self.fps = fps
        self.timer = 0
        self.pos = Vec(pos)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.timer += dt
        if self.timer >= (1 / self.fps):
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=self.pos)

    def draw(self, surf):
        surf.blit(self.image, self.rect.topleft)


# 🔥 Nave com animação
class Ship(AnimatedSprite):
    def __init__(self, pos):
        super().__init__(pos, "assets/ship.gif", scale=1.2)
        self.vel = Vec(0, 0)
        self.angle = 0
        self.thrust = 0
        self.rotation_speed = 180  # graus por segundo
        self.acceleration = 200    # pixels por segundo²
        self.max_speed = 300       # velocidade máxima
        self.drag = 0.98

    def rotate(self, angle):
        self.angle += angle
        self.image = pg.transform.rotate(self.frames[self.frame_index], -self.angle)
        self.rect = self.image.get_rect(center=self.pos)
    
    def control(self, keys, dt):
        """Controla a nave baseado nas teclas pressionadas"""
        # Rotação (setas esquerda/direita ou A/D)
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rotate(self.rotation_speed * dt)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rotate(-self.rotation_speed * dt)
            
        # Aceleração (seta para cima ou W)
        if keys[pg.K_UP] or keys[pg.K_w]:
            # Calcular vetor de direção baseado no ângulo
            rad_angle = math.radians(self.angle)
            thrust_vec = Vec(math.cos(rad_angle), -math.sin(rad_angle))
            
            # Aplicar aceleração
            self.vel += thrust_vec * self.acceleration * dt
            
            # Limitar velocidade máxima
            if self.vel.length() > self.max_speed:
                self.vel = self.vel.normalize() * self.max_speed
                
            self.thrust = 1  # Para efeitos visuais
        else:
            self.thrust = 0
            
        # Aplicar fricção/drag
        self.vel *= self.drag
        
        # Atualizar posição
        self.pos += self.vel * dt
        
        # Atualizar retângulo para colisão
        self.rect.center = self.pos.xy
        
        # Wrap-around (teleporte nas bordas)
        screen_width = 800  # Ajuste conforme sua tela
        screen_height = 600  # Ajuste conforme sua tela
        
        if self.pos.x < 0:
            self.pos.x = screen_width
        elif self.pos.x > screen_width:
            self.pos.x = 0
            
        if self.pos.y < 0:
            self.pos.y = screen_height
        elif self.pos.y > screen_height:
            self.pos.y = 0
            
        self.rect.center = self.pos.xy
    
        def shoot(self):

            rad_angle = math.radians(self.angle)
            direction = Vec(math.cos(rad_angle), -math.sin(rad_angle))
            bullet_pos = self.pos + direction * 20  # 20 pixels à frente da nave
            return Bullet(bullet_pos, direction, owner="ship")


# 👾 UFO animado
class UFO(AnimatedSprite):
    def __init__(self, pos, speed):
        super().__init__(pos, "assets/ufo.gif", scale=1.2)
        self.speed = speed

    def update(self, dt):
        super().update(dt)
        self.pos.x += self.speed * dt
        self.rect.center = self.pos.xy

# ðŸ”¥ Bala para nave e UFO
class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, direction, speed=500, owner="ship"):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(direction).normalize() * speed
        self.owner = owner  # "ship" ou "ufo" para identificar quem atirou
        
        # Criar uma bala simples (pode personalizar depois)
        self.image = pg.Surface((4, 4), pg.SRCALPHA)
        
        # Cor diferente para cada dono
        if owner == "ship":
            pg.draw.circle(self.image, (255, 255, 255), (2, 2), 2)  # Branco para nave
        else:
            pg.draw.circle(self.image, (255, 100, 100), (2, 2), 2)  # Vermelho para UFO
            
        self.rect = self.image.get_rect(center=self.pos.xy)
        self.lifetime = 2.0  # 2 segundos de vida
        self.time_alive = 0
        
    def update(self, dt):
        # Atualizar posição
        self.pos += self.vel * dt
        self.rect.center = self.pos.xy
        
        # Atualizar tempo de vida
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()  # Remove a bala quando o tempo acaba
            
        # Verificar limites da tela (wrap-around como no Asteroids)
        screen_width = 800  # Ajuste conforme o tamanho da sua tela
        screen_height = 600
        
        if self.pos.x < 0:
            self.pos.x = screen_width
        elif self.pos.x > screen_width:
            self.pos.x = 0
            
        if self.pos.y < 0:
            self.pos.y = screen_height
        elif self.pos.y > screen_height:
            self.pos.y = 0
            
        self.rect.center = self.pos.xy
        
    def draw(self, surf):
        surf.blit(self.image, self.rect.topleft)

# ✨ Partículas para efeitos (explosões, propulsão, etc.)
class Particle(pg.sprite.Sprite):
    def __init__(self, pos, velocity, color=(255, 255, 255), size=3, lifetime=1.0):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(velocity)
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.time_alive = 0
        
        # Criar partícula redonda
        self.image = pg.Surface((size*2, size*2), pg.SRCALPHA)
        pg.draw.circle(self.image, color, (size, size), size)
        self.rect = self.image.get_rect(center=self.pos.xy)
        
    def update(self, dt):
        # Atualizar posição com velocidade
        self.pos += self.vel * dt
        self.rect.center = self.pos.xy
        
        # Atualizar tempo de vida
        self.time_alive += dt
        
        # Efeito de fade out
        alpha = max(0, int(255 * (1 - self.time_alive / self.lifetime)))
        if alpha <= 0:
            self.kill()
            return
            
        # Atualizar transparência
        self.image.set_alpha(alpha)
        
    def draw(self, surf):
        surf.blit(self.image, self.rect.topleft)