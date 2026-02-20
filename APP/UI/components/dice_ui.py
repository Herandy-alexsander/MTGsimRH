import pygame
import random
import math
import os
from APP.UI.styles.colors import ACCENT, SUCCESS
from APP.UI.components.button import MenuButton

class DiceOverlayUI:
    def __init__(self, largura, altura, fontes):
        """
        Componente de D20 com Física Pseudo-3D (Pulos e Colisão Circular).
        """
        self.largura = largura
        self.altura = altura
        self.fontes = fontes

        self.ativo = False
        self.rolando = False
        self.resultado_final = 20
        self.display_atual = 20

        # Física Avançada (X, Y para a mesa, Z para a altura do pulo)
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0
        
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        
        self.rotacao = 0
        self.vel_rotacao = 0

        self.btn_continuar = MenuButton(
            pygame.Rect((self.largura // 2) - 125, (self.altura // 2) + 170, 250, 55),
            "CONTINUAR",
            self.fontes['menu']
        )
        
        # Spritesheet
        self.dado_frames = []
        self._carregar_sprites()

    def _carregar_sprites(self):
        """Corta a imagem e mantém a proporção perfeita do dado."""
        caminho_sprite = "assets/img/d20_MHG.png"
        
        if os.path.exists(caminho_sprite):
            try:
                sheet = pygame.image.load(caminho_sprite).convert_alpha()
                w_total, h_total = sheet.get_size()
                
                fw = w_total // 5
                fh = h_total // 4
                
                # Aumentei para 140 para o dado preencher melhor a bandeja
                escala = 140.0 / max(fw, fh)
                novo_w = int(fw * escala)
                novo_h = int(fh * escala)
                
                for row in range(4):
                    for col in range(5):
                        rect = pygame.Rect(col * fw, row * fh, fw, fh)
                        frame = sheet.subsurface(rect)
                        frame = pygame.transform.smoothscale(frame, (novo_w, novo_h))
                        self.dado_frames.append(frame)
                        
                print("[SISTEMA] D20 MHG carregado com física 3D pronta!")
            except Exception as e:
                print(f"[ERRO] Falha ao fatiar D20 MHG: {e}")
        else:
            print(f"[AVISO] Imagem '{caminho_sprite}' não achada. Usando Geometria 3D.")

    def rolar(self, resultado):
        """Joga o dado lá de cima para iniciar o sorteio."""
        self.ativo = True
        self.rolando = True
        self.resultado_final = resultado
        
        # O dado começa caindo (Z = 200)
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 200 
        
        # Joga o dado em direções aleatórias fortes
        self.vel_x = random.uniform(-15, 15)
        self.vel_y = random.uniform(-15, 15)
        self.vel_z = random.uniform(-5, 5)
        
        # Muito giro inicial
        self.vel_rotacao = random.uniform(20, 40) 

    def handle_events(self, events, mouse_pos):
        if not self.ativo:
            return False
            
        if not self.rolando:
            self.btn_continuar.update(mouse_pos)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_continuar.is_clicked(event):
                        self.ativo = False
        return True

    def draw(self, screen):
        if not self.ativo:
            return

        cx, cy = self.largura // 2, self.altura // 2
        raio = 170

        # Fundo escuro
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        screen.blit(overlay, (0, 0))

        # Desenha a Bandeja Redonda
        pygame.draw.circle(screen, (60, 35, 15), (cx, cy), raio) # Madeira
        pygame.draw.circle(screen, (20, 60, 35), (cx, cy), raio - 18) # Veludo verde

        # Executa as contas de pulo e colisão
        if self.rolando:
            self._atualizar_fisica()

        # O segredo do Pseudo-3D: Subtrair a altura Z do Y para o dado subir na tela!
        centro_x = cx + int(self.pos_x)
        centro_y = cy + int(self.pos_y) - int(self.pos_z)

        # RENDERIZA O DADO
        if self.dado_frames and len(self.dado_frames) == 20:
            frame_atual = self.dado_frames[self.display_atual - 1]
            frame_rotacionado = pygame.transform.rotate(frame_atual, self.rotacao)
            rect_rot = frame_rotacionado.get_rect(center=(centro_x, centro_y))
            screen.blit(frame_rotacionado, rect_rot.topleft)
        else:
            self._desenhar_poligono_fallback(screen, (centro_x, centro_y), 60)

        # Finalização da rolagem (Quando para)
        if not self.rolando:
            self.btn_continuar.draw(screen)

    def _atualizar_fisica(self):
        """Calcula os pulos, o giro e as batidas na parede circular."""
        # 1. Gravidade puxa para baixo
        self.vel_z -= 2.5 
        
        # 2. Aplica velocidade na posição
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.pos_z += self.vel_z
        self.rotacao += self.vel_rotacao

        # 3. Colisão com o CHÃO DO VELUDO (Pulos)
        if self.pos_z <= 0:
            self.pos_z = 0
            self.vel_z *= -0.6 # Quica perdendo força
            
            # O atrito com o veludo freia o dado
            self.vel_x *= 0.8
            self.vel_y *= 0.8
            self.vel_rotacao *= 0.85
        else:
            # Quando está no ar, gira mais solto
            self.vel_rotacao *= 0.98

        # 4. COLISÃO COM A BORDA REDONDA DA CUBA
        # O teorema de Pitágoras mede a distância do dado pro centro
        dist = math.hypot(self.pos_x, self.pos_y)
        
        # O raio máximo que ele pode ir (170 do raio total menos o tamanho do dado)
        limite = 110 
        
        if dist > limite:
            # Trava o dado exatamente na beira da cuba
            self.pos_x = (self.pos_x / dist) * limite
            self.pos_y = (self.pos_y / dist) * limite
            
            # Faz a parede rebater a velocidade (efeito estilingue)
            self.vel_x *= -0.8
            self.vel_y *= -0.8
            
            # Ao bater na parede, o dado gira maluco
            self.vel_rotacao = random.uniform(10, 40)

        # 5. CONDIÇÃO DE PARADA (Ficou parado no chão)
        if self.pos_z == 0 and abs(self.vel_z) < 1 and abs(self.vel_x) < 0.5 and abs(self.vel_y) < 0.5:
            self.rolando = False
            self.display_atual = self.resultado_final
            self.rotacao = 0 # Endireita para facilitar a leitura
        else:
            # Troca de imagem super rápido para simular que está rodando
            self.display_atual = random.randint(1, 20)

    def _desenhar_poligono_fallback(self, screen, centro, tamanho):
        """Geometria caso a imagem suma."""
        cx, cy = centro
        rot = math.radians(self.rotacao)
        pontos = []
        for i in range(6):
            angulo = math.radians(60 * i - 30) + rot
            pontos.append((cx + tamanho * math.cos(angulo), cy + tamanho * math.sin(angulo)))
        pygame.draw.polygon(screen, (180, 25, 25), pontos)
        pygame.draw.polygon(screen, ACCENT, pontos, 3)