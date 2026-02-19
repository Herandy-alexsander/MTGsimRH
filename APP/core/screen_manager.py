# APP/core/screen_manager.py

class ScreenManager:
    def __init__(self):
        self.current_screen = None

    def set_screen(self, screen):
        """Troca a tela atual exibida no jogo."""
        self.current_screen = screen

    def handle_events(self, events):
        """Repassa os eventos do teclado/mouse para a tela atual."""
        if self.current_screen:
            return self.current_screen.handle_events(events)
        return None

    def draw(self):
        """Pede para a tela atual se desenhar."""
        if self.current_screen:
            self.current_screen.draw()