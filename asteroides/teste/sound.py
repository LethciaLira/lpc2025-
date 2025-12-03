import pygame as pg
import os

MASTER_VOLUME = 0.5

SND_PLAYER_SHOOT = "assets/sounds/shot_player_sound.wav"
SND_UFO_SHOOT = "assets/sounds/ufo_shot.wav"
SND_A_DESTROY = "assets/sounds/asteroid_break.wav"
SND_UFO_APPEAR = "assets/sounds/ufo_appear.wav"
SND_UFO_DEATH = "assets/sounds/ufo_death.wav"
SND_PLAYER_DEATH = "assets/sounds/death_sound.wav"
SND_HIPER = "assets/sounds/hiper_sound.mp3"
MUSIC_INTRO = "assets/sounds/Intro Stage.mp3"
MUSIC_TRACK = "assets/sounds/guardian.mp3"

BASE = os.path.dirname(os.path.abspath(__file__))

def path(p):
    return os.path.join(BASE, p)


class SoundManager:
    def __init__(self):
        pg.mixer.init()
        self.load_sounds()

    def load_sounds(self):
        self.player_shoot = self.load_effect(SND_PLAYER_SHOOT)
        self.ufo_shoot = self.load_effect(SND_UFO_SHOOT)
        self.asteroid_explosion = self.load_effect(SND_A_DESTROY)
        self.ufo_appear = self.load_effect(SND_UFO_APPEAR)
        self.ufo_death = self.load_effect(SND_UFO_DEATH)
        self.player_death = self.load_effect(SND_PLAYER_DEATH)
        self.hiper_sound = self.load_effect(SND_HIPER)

    def load_effect(self, file):
        try:
            snd = pg.mixer.Sound(path(file))
            snd.set_volume(MASTER_VOLUME)
            return snd
        except Exception as e:
            print(f"Falha ao carregar: {file} -> {e}")
            return None

    # 🎵 INTRO
    def play_intro(self):
        pg.mixer.music.stop()
        pg.mixer.music.load(path(MUSIC_INTRO))
        pg.mixer.music.set_volume(0.4)
        pg.mixer.music.play(-1)

    # 🎮 GAME TRACK
    def play_track(self):
        pg.mixer.music.stop()
        pg.mixer.music.load(path(MUSIC_TRACK))
        pg.mixer.music.set_volume(0.2)
        pg.mixer.music.play(-1)

    def stop_music(self):
        pg.mixer.music.stop()

    def play_player_shoot(self):
        if self.player_shoot:
            self.player_shoot.play()

    def play_hiper_sound(self):
        if self.hiper_sound:
            self.hiper_sound.play()

    def play_ufo_shoot(self):
        if self.ufo_shoot:
            self.ufo_shoot.play()

    def play_asteroid_explosion(self):
        if self.asteroid_explosion:
            self.asteroid_explosion.play()

    def play_ufo_appear(self):
        if self.ufo_appear:
            self.ufo_appear.play()

    def play_ufo_death(self):
        if self.ufo_death:
            self.ufo_death.play()

    def play_player_death(self):
        if self.player_death:
            self.player_death.play()
