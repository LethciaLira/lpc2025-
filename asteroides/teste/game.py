import random
import sys
from dataclasses import dataclass

import pygame as pg
from sound import SoundManager
import config as C
from systems import World
from utils import text


@dataclass
class Scene:
    name: str


class Game:
    def __init__(self):
        pg.init()

        # ---- JOYSTICK ----
        pg.joystick.init()
        self.joy = None
        if pg.joystick.get_count() > 0:
            self.joy = pg.joystick.Joystick(0)
            self.joy.init()

        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Asteroides")

        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 20)
        self.big = pg.font.SysFont("consolas", 48)

        self.scene = Scene("menu")
        self.world = World(self)
        self.sound = SoundManager()

        self.playing_intro = False

    def run(self):
        while True:
            dt = self.clock.tick(C.FPS) / 1000

            # valores do joystick (RT e D-pad)
            rt_value = 0
            dpad_up = False

            if self.joy:
                rt_value = (self.joy.get_axis(5) + 1) / 2  # 0 a 1
                hat = self.joy.get_hat(0)
                dpad_up = hat[1] == 1

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                # -------------------------
                #        MENU
                # -------------------------
                if self.scene.name == "menu":
                    if not self.playing_intro:
                        self.sound.play_intro()
                        self.playing_intro = True

                    # qualquer tecla inicia
                    if e.type == pg.KEYDOWN:
                        self.scene = Scene("play")
                        self.playing_intro = False
                        self.sound.play_track()

                    # botão Y sai do jogo
                    if e.type == pg.JOYBUTTONDOWN and e.button == 3:
                        pg.quit()
                        sys.exit()

                # -------------------------
                #        PLAY
                # -------------------------
                elif self.scene.name == "play":
                    if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                        self.world.try_fire()

                    if e.type == pg.JOYBUTTONDOWN and e.button == 0:  # A
                        self.world.try_fire()

                    if e.type == pg.KEYDOWN and e.key == pg.K_LSHIFT:
                        self.world.hyperspace()

                    if e.type == pg.JOYBUTTONDOWN and e.button == 2:  # X = hiper
                        self.world.hyperspace()

                    # botão Y sai do jogo
                    if e.type == pg.JOYBUTTONDOWN and e.button == 3:
                        pg.quit()
                        sys.exit()

                # -------------------------
                #      GAME OVER
                # -------------------------
                elif self.scene.name == "gameover":

                    # ENTER reinicia
                    if e.type == pg.KEYDOWN and e.key == pg.K_RETURN:
                        self.world = World(self)
                        self.scene = Scene("play")
                        self.sound.play_track()

                    # ESC sai
                    if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                        pg.quit()
                        sys.exit()

                    # START reinicia
                    if e.type == pg.JOYBUTTONDOWN and e.button == 7:
                        self.world = World(self)
                        self.scene = Scene("play")
                        self.sound.play_track()

                    # Y sai do jogo
                    if e.type == pg.JOYBUTTONDOWN and e.button == 3:
                        pg.quit()
                        sys.exit()

            keys = pg.key.get_pressed()
            self.screen.fill(C.BLACK)

            # ---- ACELERAÇÃO POR RT OU DPAD ↑ ----
            self.world.rt_accel = rt_value > 0.1
            self.world.dpad_up = dpad_up

            # Desenho da cena atual
            if self.scene.name == "menu":
                self.draw_menu()

            elif self.scene.name == "play":
                self.world.update(dt, keys)
                self.world.draw(self.screen, self.font)

            elif self.scene.name == "gameover":
                self.draw_gameover()

            pg.display.flip()

    # -------------------------
    #     MENU
    # -------------------------
    def draw_menu(self):
        text(self.screen, self.big, "ASTEROIDS", C.WIDTH // 2 - 150, 180)
        text(self.screen, self.font,
             "Setas/Analogico: girar   Espaço/A: tiro   Shift/X: hiper",
             120, 300)
        text(self.screen, self.font,
             "RT ou D-Pad UP: acelerar", 280, 330)
        text(self.screen, self.font,
             "Pressione qualquer tecla...", 260, 380)
        text(self.screen, self.font,
             "Made by: Lethicia Lira e Guilherme Mota...", 260, 600)

    # -------------------------
    #     GAME OVER
    # -------------------------
    def draw_gameover(self):
        text(self.screen, self.big, "GAME OVER", C.WIDTH // 2 - 150, 200)
        text(self.screen, self.font,
             "ENTER / START para reiniciar",
             C.WIDTH // 2 - 140, 350)
        text(self.screen, self.font,
             "ESC / Y para sair",
             C.WIDTH // 2 - 50, 400)
