import pygame
from mtg_commander_app.utils.base import ViewComponent
from mtg_commander_app.utils.ui_components import MenuButton, UIComponents
from mtg_commander_app.utils.style import GameStyle

class WelcomeView(ViewComponent):
    def __init__(self, screen, controller, storage):
        """
        Responsável por capturar o primeiro acesso do usuário.
        """
        super().__init__(screen, controller)
        self.storage = storage
        self.largura, self.altura = self.screen.get_size()
        
        # Carrega fontes e componentes de UI padronizados
        self.fontes = GameStyle.get_fonts()
        self.ui = UIComponents(self.largura, self.altura)
        
        # Estado do input
        self.nickname = ""
        self.status_msg = "Aguardando seu nome..."
        
        # Definição de layout
        cx, cy = self.largura // 2, self.altura // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 25, 300, 50)
        self.btn_confirmar = MenuButton(
            pygame.Rect(cx - 100, cy + 60, 200, 50),
            "INICIAR", 
            self.fontes['menu']
        )

    def handle_events(self, events):
        """Processa a digitação do nickname e a confirmação."""
        mouse_pos = pygame.mouse.get_pos()
        self.btn_confirmar.update(mouse_pos)

        for event in events:
            if event.type == pygame.KEYDOWN:
                # Lógica de apagar e digitar
                if event.key == pygame.K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    return self._tentar_confirmar()
                elif len(self.nickname) < 15:
                    # Filtra apenas caracteres visíveis
                    if event.unicode.isprintable():
                        self.nickname += event.unicode
            
            if self.btn_confirmar.is_clicked(event):
                return self._tentar_confirmar()
                
        return None

    def _tentar_confirmar(self):
        """Valida o nome e inicializa o profiler.json via storage."""
        if len(self.nickname.strip()) >= 3:
            # Chama o método que implementamos no storage.py
            self.storage.inicializar_perfil_usuario(self.nickname.strip())
            return "MENU"
        else:
            self.status_msg = "O nome deve ter pelo menos 3 caracteres!"
            return None

    def draw(self):
        """Renderiza a interface de boas-vindas com estilo MTG."""
        self.screen.fill(GameStyle.COLOR_BG)
        
        # Título Central
        txt_titulo = self.fontes['titulo'].render("BEM-VINDO", True, GameStyle.COLOR_ACCENT)
        self.screen.blit(txt_titulo, (self.largura // 2 - txt_titulo.get_width() // 2, 100))
        
        # Subtítulo/Instrução
        txt_instr = self.fontes['label'].render("Digite seu Nickname para começar:", True, (200, 200, 200))
        self.screen.blit(txt_instr, (self.largura // 2 - txt_instr.get_width() // 2, self.altura // 2 - 70))
        
        # Caixa de Input
        pygame.draw.rect(self.screen, (30, 30, 35), self.input_rect, border_radius=5)
        pygame.draw.rect(self.screen, GameStyle.COLOR_ACCENT, self.input_rect, 2, border_radius=5)
        
        # Texto digitado
        surf_nick = self.fontes['menu'].render(self.nickname, True, (255, 255, 255))
        self.screen.blit(surf_nick, (self.input_rect.x + 10, self.input_rect.centery - surf_nick.get_height() // 2))
        
        # Mensagem de Status/Aviso
        cor_status = (200, 200, 200) if "Aguardando" in self.status_msg else GameStyle.COLOR_DANGER
        surf_status = self.fontes['status'].render(self.status_msg, True, cor_status)
        self.screen.blit(surf_status, (self.largura // 2 - surf_status.get_width() // 2, self.altura // 2 + 35))
        
        # Botão Confirmar
        self.btn_confirmar.draw(self.screen)