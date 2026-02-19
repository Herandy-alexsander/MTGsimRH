import pygame
from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles import colors, settings
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.button import MenuButton
from APP.UI.components.input_field import InputField
from APP.UI.components.label import Label

class WelcomeView(BaseScreen):
    def __init__(self, screen, controller, storage):
        """
        Responsável por capturar o primeiro acesso do usuário e criar o perfil.
        :param storage: Aqui passamos o ProfileController ou ProfileRepository.
        """
        super().__init__(screen, controller)
        self.storage = storage
        self.largura, self.altura = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        
        self.fontes = get_fonts()
        cx, cy = self.largura // 2, self.altura // 2

        # --- Componentes Modulares ---
        self.label_titulo = Label("BEM-VINDO", (cx, 150), self.fontes['titulo'], colors.ACCENT)
        self.label_instrucao = Label("Digite seu Nickname para começar:", (cx, cy - 80), self.fontes['label'], (200, 200, 200))
        
        # Campo de entrada de texto
        self.input_nickname = InputField(pygame.Rect(cx - 150, cy - 25, 300, 50), self.fontes['menu'], "Nickname...")
        
        # Botão de confirmação
        self.btn_confirmar = MenuButton(
            pygame.Rect(cx - 100, cy + 80, 200, 50),
            "INICIAR", 
            self.fontes['menu']
        )
        
        # Feedback visual para o usuário
        self.status_msg = Label("Aguardando seu nome...", (cx, cy + 50), self.fontes['status'], (150, 150, 150))

    def handle_events(self, events):
        """Processa interações e retorna a próxima ação para o controlador mestre."""
        mouse_pos = pygame.mouse.get_pos()
        self.btn_confirmar.update(mouse_pos)

        for event in events:
            # Encaminha o evento para o InputField (digitação, foco, etc.)
            if hasattr(self.input_nickname, 'handle_event'):
                self.input_nickname.handle_event(event)
            
            # Valida ao pressionar Enter
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return self._tentar_confirmar()
            
            # Valida ao clicar no botão
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_confirmar.is_clicked(event):
                    return self._tentar_confirmar()
                
        return None

    def _tentar_confirmar(self):
        """Valida o nome (não vazio, min. 3 chars) e utiliza o storage para salvar."""
        # Usa o get_value() do InputField para obter o texto limpo
        nickname = self.input_nickname.get_value()
        
        # Validação de Input: Verifica se está vazio ou é o placeholder
        if not nickname or nickname == "Nickname...":
            self.status_msg.set_text("⚠️ Digite um nome válido!")
            self.status_msg.color = (255, 80, 80) # Vermelho de erro
            return None

        # Regra de negócio: Mínimo de 3 caracteres
        if len(nickname) < 3:
            self.status_msg.set_text("⚠️ O nome deve ter pelo menos 3 letras!")
            self.status_msg.color = (255, 80, 80)
            return None

        # Se passou pelas validações, tenta salvar
        try:
            # Verifica qual tipo de storage foi injetado (Controller ou Repo)
            if hasattr(self.storage, 'inicializar_perfil_usuario'):
                self.storage.inicializar_perfil_usuario(nickname)
            elif hasattr(self.storage, 'cadastrar_nickname'):
                self.storage.cadastrar_nickname(nickname)
            else:
                raise AttributeError("Método de salvamento não encontrado no storage.")
            
            return "MENU"
        
        except Exception as e:
            self.status_msg.set_text(f"Erro ao salvar: {str(e)}")
            self.status_msg.color = (255, 80, 80)
            return None

    def draw(self):
        """Renderiza os elementos na tela usando o esquema de cores global."""
        self.screen.fill(colors.BG)
        
        self.label_titulo.draw(self.screen)
        self.label_instrucao.draw(self.screen)
        self.input_nickname.draw(self.screen)
        self.status_msg.draw(self.screen)
        self.btn_confirmar.draw(self.screen)