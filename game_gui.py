import pygame
import sys
from game import start_new_game, load_game_menu, game_loop
from save_manager import SaveManager

# Inicialização do Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 40)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
GOLD = (255, 215, 0)
RED = (200, 50, 50)
DARK_RED = (150, 30, 30)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 150, 30)
BLUE = (50, 100, 200)
DARK_BLUE = (30, 60, 150)

class Button:
    """Classe para criar botões interativos"""
    
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.action = action
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, screen):
        """Desenha o botão"""
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, self.rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_hovered(self, mouse_pos):
        """Verifica se o mouse está sobre o botão"""
        return self.rect.collidepoint(mouse_pos)
    
    def update(self, mouse_pos):
        """Atualiza a cor do botão baseado no hover"""
        if self.is_hovered(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
    
    def handle_click(self, mouse_pos):
        """Executa a ação do botão se clicado"""
        if self.is_hovered(mouse_pos) and self.action:
            return self.action()
        return None


class MainMenu:
    """Menu principal do jogo"""
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.save_manager = SaveManager()
        
        # Fontes
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 40)
        
        # Botões
        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 250
        spacing = 80
        
        self.buttons = [
            Button(button_x, start_y, button_width, button_height,
                   "NOVO JOGO", DARK_GREEN, GREEN, self.new_game),
            Button(button_x, start_y + spacing, button_width, button_height,
                   "CARREGAR JOGO", DARK_BLUE, BLUE, self.load_game),
            Button(button_x, start_y + spacing * 2, button_width, button_height,
                   "SAIR", DARK_RED, RED, self.quit_game)
        ]
    
    def new_game(self):
        """Inicia novo jogo"""
        print("\n🎮 Iniciando novo jogo...")
        result = start_new_game()
        if result:
            player, world = result
            game_loop(player, world)
        return "menu"
    
    def load_game(self):
        """Carrega jogo salvo"""
        print("\n📂 Carregando jogo...")
        result = load_game_menu(self.save_manager)
        if result:
            player, world = result
            game_loop(player, world)
        return "menu"
    
    def quit_game(self):
        """Sai do jogo"""
        return "quit"
    
    def draw_background(self):
        """Desenha o fundo com gradiente"""
        for y in range(SCREEN_HEIGHT):
            color_value = int(20 + (y / SCREEN_HEIGHT) * 30)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 10),
                           (0, y), (SCREEN_WIDTH, y))
    
    def draw_title(self):
        """Desenha o título do jogo"""
        # Título principal
        title_text = "DUNGEON OF THE FORGOTTEN"
        title_surface = self.title_font.render(title_text, True, GOLD)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        
        # Sombra do título
        shadow_surface = self.title_font.render(title_text, True, BLACK)
        shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 3, 83))
        
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(title_surface, title_rect)
        
        # Subtítulo
        subtitle_text = "⚔️  Uma Aventura Épica  ⚔️"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, LIGHT_GRAY)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Decoração
        pygame.draw.line(self.screen, GOLD, (200, 180), (600, 180), 2)
    
    def run(self):
        """Loop principal do menu"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Botão esquerdo
                        for button in self.buttons:
                            result = button.handle_click(mouse_pos)
                            if result == "quit":
                                return "quit"
                            elif result == "menu":
                                # Volta ao menu após jogar
                                pass
            
            # Atualizar botões
            for button in self.buttons:
                button.update(mouse_pos)
            
            # Desenhar
            self.draw_background()
            self.draw_title()
            
            for button in self.buttons:
                button.draw(self.screen)
            
            # Versão
            version_font = pygame.font.Font(None, 24)
            version_surface = version_font.render("v2.0 - GUI Edition", True, GRAY)
            version_rect = version_surface.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
            self.screen.blit(version_surface, version_rect)
            
            pygame.display.flip()
        
        return "quit"


def main():
    """Função principal"""
    try:
        # Configurar janela
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon of the Forgotten")
        
        # Ícone (opcional - você pode adicionar um arquivo .png depois)
        # icon = pygame.image.load("icon.png")
        # pygame.display.set_icon(icon)
        
        # Criar e executar menu
        menu = MainMenu(screen)
        menu.run()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
