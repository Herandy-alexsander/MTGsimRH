class CardEffects:
    """
    Tradutor de interações da UI para comandos do Controller.
    Decide o que acontece quando uma carta é clicada dependendo do contexto.
    """
    
    @staticmethod
    def handle_click(controller, player_id, card_ui):
        """
        Ponto central de decisão de clique em cartas no campo.
        """
        card_model = card_ui.card

        # SE FOR TERRENO: Tenta gerar mana
        if card_model.is_land:
            if not card_model.is_tapped:
                controller.virar_terreno_para_mana(player_id, card_model)
            else:
                print(f"[UI] {card_model.name} já está virado.")
        
        # SE FOR CRIATURA: (Futuramente: Declarar ataque, ativar habilidade, etc)
        elif card_model.is_creature:
            print(f"[UI] Clicou na criatura: {card_model.name}")
            # controller.declarar_ataque(player_id, card_model)
