class BaseScreen:
    def __init__(self, screen, controller):
        self.screen = screen
        self.controller = controller
        self.width, self.height = screen.get_size()

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self):
        pass
