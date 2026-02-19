# main.py
from APP.controllers.app_controller import AppController
from APP.infrastructure.storage.profile_repository import ProfileRepository

def main():
    # 1. Inicializa a infraestrutura básica (Onde os dados vivem)
    profile_repo = ProfileRepository()

    # 2. Inicializa o Maestro do jogo
    # O AppController agora cuida de iniciar o Engine internamente
    app = AppController(profile_repo)
    
    # 3. Dá a partida no simulador
    app.run()

if __name__ == "__main__":
    main()