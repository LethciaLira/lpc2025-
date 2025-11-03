import pygame
from core.settings import * 

class Scoreboard:
    def __init__(self, screen):
        self.screen = screen
        try:
            self.font = pygame.font.Font(None, 36) 
        except pygame.error:
            # Em caso de erro na inicialização da fonte (raro), use uma alternativa
            print("Atenção: Fonte padrão do Pygame não carregada.")
            self.font = None 
            
        self.score_p1 = 0
        self.score_p2 = 0

    def draw(self):
        if not self.font: return # Se a fonte falhou, não desenhe

        # Desenhar Placar P1 
        text_p1 = self.font.render(f"P1: {self.score_p1}", True, (0, 255, 0)) # Usando verde direto por segurança
        self.screen.blit(text_p1, (100, 10))

        # Desenhar Placar P2 
        text_p2 = self.font.render(f"P2: {self.score_p2}", True, (255, 0, 0)) # Usando vermelho direto por segurança
        self.screen.blit(text_p2, (SCREEN_WIDTH - text_p2.get_width() - 100, 10))

    def add_score(self, player_number, points=1):
        if player_number == 1:
            self.score_p1 += points
        elif player_number == 2:
            self.score_p2 += points
