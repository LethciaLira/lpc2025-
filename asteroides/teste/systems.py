import math 
import random
from random import uniform

import pygame as pg

import config as C
from sprites import Ship, UFO, Bullet
from utils import Vec, rand_edge_pos, rand_unit_vec
from sound import SoundManager
from sprites import Particle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Scene, Game


class World:
    def __init__(self, game):
        self.game = game  

        # Ship e grupos
        self.ship = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()

        # Asteroides removidos (não usados)
        # self.asteroids = pg.sprite.Group()

        self.ufos = pg.sprite.Group()
        self.particles = pg.sprite.Group()

        # all_sprites para facilitar update/draw
        self.all_sprites = pg.sprite.Group(self.ship)
        
        # controles (setados pelo game)
        self.rt_accel = False
        self.dpad_up = False

        # estado do jogo
        self.score = 0
        self.lives = C.START_LIVES

        # NOVO SISTEMA DE HORDAS
        self.wave = 1
        self.wave_timer = 0
        self.time_between_waves = 4.0

        # Atributos de dificuldade progressiva
        self.ufo_spawn_rate = 0.015
        self.ufo_speed_mult = 1.0

        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY

        self.sound = SoundManager()

        # -------------------------
        # Background (carrega com fallback)
        # -------------------------
        try:
            self.bg = pg.image.load("assets/background.png").convert()
            # garantir tamanho correto
            if self.bg.get_size() != (C.WIDTH, C.HEIGHT):
                self.bg = pg.transform.scale(self.bg, (C.WIDTH, C.HEIGHT))
        except Exception:
            self.bg = None  # fallback: será preenchido com cor sólida no draw


    # --------------------------------------------------------
    # SISTEMA DE HORDAS
    # --------------------------------------------------------
    def update_wave_system(self, dt):
        # Se não há UFOs, conta para próxima horda
        if len(self.ufos) == 0:
            self.wave_timer += dt
            if self.wave_timer >= self.time_between_waves:
                self.start_next_wave()
        else:
            self.wave_timer = 0

    def start_next_wave(self):
        self.wave += 1
        self.wave_timer = 0

        # Aumenta dificuldade
        self.ufo_spawn_rate += 0.006
        self.ufo_speed_mult += 0.15

        # Spawn inicial de UFO com base na horda
        initial = min(4, self.wave)
        for _ in range(initial):
            self.spawn_ufo()

        print(f"--- Horda {self.wave} iniciada ---")
        


    # --------------------------------------------------------
    # UFO — sempre pequeno
    # --------------------------------------------------------
    def spawn_ufo(self):
        import random
        small = True  
        y = uniform(0, C.HEIGHT)
        x_left = random.random() < 0.5
        x = 0 if x_left else C.WIDTH

        # NOTE: a classe UFO deve aceitar (pos, small) ou (pos, small=True)
        ufo = UFO(Vec(x, y), small=True)
        ufo.dir = Vec(1, 0) if x_left else Vec(-1, 0)
        ufo.shoot_cool = 0.0

        # Aumenta velocidade proporcional à horda
        ufo.speed = C.UFO_SPEED * self.ufo_speed_mult

        self.ufos.add(ufo)
        self.all_sprites.add(ufo)
        self.sound.play_ufo_appear()



    # --------------------------------------------------------
    # Tiro do jogador
    # --------------------------------------------------------
    def try_fire(self):
        if len(self.bullets) >= C.MAX_BULLETS:
            return

        b = self.ship.fire()
        if b:
            self.bullets.add(b)
            self.all_sprites.add(b)
            self.sound.play_player_shoot()

    # --------------------------------------------------------
    # HIPERESPAÇO — teleporte com cooldown
    # --------------------------------------------------------
    def hyperspace(self):
        # Se estiver em cooldown, ignora
        if getattr(self, "hyperspace_cd", 0) > 0:
            return

        # Teleporta para posição aleatória
        self.ship.pos.xy = (
            random.uniform(0, C.WIDTH),
            random.uniform(0, C.HEIGHT)
        )

        # zera velocidade
        self.ship.vel.xy = (0, 0)

        # invulnerável por 1 segundo
        self.ship.invuln = 1.0

        # cooldown de 10 segundos
        self.hyperspace_cd = 10.0

        # som opcional
        if hasattr(self.sound, "play_hyperspace"):
            self.sound.play_hyperspace()



    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------
    def update(self, dt: float, keys):
        # passar controle para a ship (ela lida com entrada básica)
        self.ship.control(keys, dt)

        # Cooldown do hiperespaço
        if hasattr(self, "hyperspace_cd") and self.hyperspace_cd > 0:
            self.hyperspace_cd -= dt

        # atualizar todos sprites (Ship e UFOs animados devem ter update)
        self.all_sprites.update(dt)

        # thrust via RT/dpad -> Ship tem método thrust()
        if self.rt_accel or self.dpad_up:
            # Ship deve definir thrust() — caso não tenha, use vel increment
            if hasattr(self.ship, "thrust"):
                self.ship.thrust()
            else:
                # fallback simples: empurra na direção atual
                try:
                    dirv = Vec(math.cos(math.radians(self.ship.angle)),
                               math.sin(math.radians(self.ship.angle)))
                    self.ship.vel += dirv * (C.SHIP_THRUST * dt)
                except Exception:
                    pass

        # UFO behavior: perseguir e ajustar velocidade
        for ufo in self.ufos:
            to_ship = self.ship.pos - ufo.pos
            if to_ship.length() > 0:
                ufo.dir = to_ship.normalize()
            ufo.speed = C.UFO_SPEED * self.ufo_speed_mult

        # Invulnerabilidade inicial do spawn
        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5

        # Timer para spawn de UFO random
        self.ufo_timer -= dt
        if self.ufo_timer <= 0:
            # probabilidade por frame aumentada conforme wave
            if random.random() < self.ufo_spawn_rate:
                self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        # Sistema de waves
        self.update_wave_system(dt)

        # tiros de UFO
        self.update_ufo_shots(dt)

        # colisões (mantém bullets x UFO e UFO x player)
        self.handle_collisions()



    # --------------------------------------------------------
    # UFO Shots
    # --------------------------------------------------------
    def update_ufo_shots(self, dt):
        for ufo in self.ufos:
            ufo.shoot_cool = getattr(ufo, "shoot_cool", 0.0) - dt

            if ufo.shoot_cool <= 0:
                # mira na ship
                if (self.ship.pos - ufo.pos).length() > 0:
                    dirv = (self.ship.pos - ufo.pos).normalize()
                else:
                    dirv = Vec(0, -1)

                vel = dirv * C.SHIP_BULLET_SPEED
                b = Bullet(ufo.pos, vel)
                self.ufo_bullets.add(b)
                self.all_sprites.add(b)

                self.sound.play_ufo_shoot()
                
                # UFO atira mais rápido conforme wave
                ufo.shoot_cool = max(0.35, 1.4 - self.wave * 0.1)



    # --------------------------------------------------------
    # COLLISIONS
    # --------------------------------------------------------
    def handle_collisions(self):

        # Player versus UFO
        if self.ship.invuln <= 0 and self.safe <= 0:
            for ufo in list(self.ufos):
                if (ufo.pos - self.ship.pos).length() < (ufo.r + self.ship.r):
                    self.ship_die()
                    break

            for b in list(self.ufo_bullets):
                if (b.pos - self.ship.pos).length() < (b.r + self.ship.r):
                    b.kill()
                    self.ship_die()
                    break

        # Player mata UFO
        for ufo in list(self.ufos):
            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    self.score += C.UFO_SMALL["score"]
                    ufo.hit_timer = 0.15
                    ufo.kill()
                    b.kill()
                    self.sound.play_ufo_death()


    # --------------------------------------------------------
    # EXPLOSÃO (usa partículas)
    # --------------------------------------------------------
    def spawn_explosion(self, pos, amount=30):
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(50, 200)

            vel = Vec(math.cos(angle), math.sin(angle)) * speed

            # NOVO: radius + ttl
            radius = random.uniform(2, 4)
            ttl = random.uniform(0.4, 0.9)

            p = Particle(pos.xy, vel, radius, ttl)
            self.particles.add(p)
            self.all_sprites.add(p)


    # --------------------------------------------------------
    # SHIP DEATH
    # --------------------------------------------------------
    def ship_die(self):
        self.spawn_explosion(self.ship.pos, amount=50)
        self.sound.play_player_death()
        self.lives -= 1
 
        if self.lives > 0:
            self.ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
            self.ship.vel.xy = (0, 0)
            # garantir ângulo consistente se usar sprite animada
            if hasattr(self.ship, "angle"):
                self.ship.angle = -90
            self.ship.invuln = C.SAFE_SPAWN_TIME
            self.safe = C.SAFE_SPAWN_TIME

        else:
            from game import Scene
            self.game.scene = Scene("gameover")



    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------
    def draw(self, surf: pg.Surface, font: pg.font.Font):
        # desenha background (fallback para cor sólida)
        if self.bg:
            surf.blit(self.bg, (0, 0))
        else:
            surf.fill(C.BLACK)

        # desenha todos sprites (Ship, UFOs, Bullets, Particles)
        for spr in self.all_sprites:
            # cada sprite deve implementar draw(surf)
            try:
                spr.draw(surf)
            except Exception:
                # fallback: se for um sprite padrão, tenta blit image
                if hasattr(spr, "image") and spr.image:
                    surf.blit(spr.image, getattr(spr, "rect", spr.image.get_rect()))
                else:
                    pass

        # desenha HUD
        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))

        # mostrar cooldown do hiperespaço, se existir
        if getattr(self, "hyperspace_cd", 0) > 0:
            cd_txt = f"HYPER COOLDOWN: {int(self.hyperspace_cd)}s"
            cd_label = font.render(cd_txt, True, C.WHITE)
            surf.blit(cd_label, (10, 36))
