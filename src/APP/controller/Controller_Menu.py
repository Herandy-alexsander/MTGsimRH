class MenuController:
    def __init__(self, view_manager):
        self.view_manager = view_manager

    def execute_action(self, action_name):
        """
        Recebe o texto do botão e decide o que o ViewManager deve fazer.
        """
        actions = {
            "JOGAR": "JOGAR",
            "LISTAR DECK": "LISTAR",
            "CADASTRAR": "CADASTRAR",
            "SAIR": "EXIT"
        }

        next_state = actions.get(action_name)
        
        if next_state == "EXIT":
            self.view_manager.running = False
        elif next_state:
            self.view_manager.change_state(next_state)