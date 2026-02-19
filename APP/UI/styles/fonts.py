# fonts.py
import pygame

def get_fonts():
    """Retorna as fontes instaladas no sistema."""
    if not pygame.font.get_init():
        pygame.font.init()

    return {
        'titulo': pygame.font.SysFont("Georgia", 60, bold=True),
        'menu':   pygame.font.SysFont("Verdana", 22),             
        'label':  pygame.font.SysFont("Verdana", 16, bold=True), 
        'status': pygame.font.SysFont("Arial", 14),             
        'popup':  pygame.font.SysFont("Georgia", 24, italic=True)
    }