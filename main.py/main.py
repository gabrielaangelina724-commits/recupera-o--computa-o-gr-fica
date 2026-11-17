
import pygame
import sys
import math
import struct

pygame.init()

# CONFIGURACOES DA JANELA
LARGURA = 900
ALTURA = 600
TILE = 40
FPS = 60

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Missao dos Cristais")

relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 23)
titulo = pygame.font.SysFont("Arial", 48, bold=True)

# CORES
BRANCO = (255, 255, 255)
AZUL = (40, 130, 255)
VERDE = (40, 180, 80)
AMARELO = (255, 220, 0)
VERMELHO = (220, 45, 45)
ROXO = (150, 60, 220)
CINZA = (95, 105, 120)
FUNDO = (15, 22, 45)

# SOM GERADO PELO PROPRIO CODIGO
som = None

try:
    pygame.mixer.init()
    dados = bytearray()

    for i in range(5000):
        valor = int(
            10000 * math.sin(2 * math.pi * 600 * i / 22050)
            * (1 - i / 5000)
        )
        dados.extend(struct.pack("<h", valor))

    som = pygame.mixer.Sound(buffer=bytes(dados))

except pygame.error:
    pass


# MATRIZ DO CENARIO
# P = plataforma
# C = cristal
# E = inimigo
# J = jogador
# S = portal
# X = area perigosa

MAPA = [list("." * 48) for _ in range(15)]


def colocar(linha, coluna, simbolo):
    MAPA[linha][coluna] = simbolo


def plataforma(linha, inicio, fim):
    for coluna in range(inicio, fim):
        colocar(linha, coluna, "P")


# Construindo as plataformas
plataforma(13, 0, 48)
plataforma(10, 3, 9)
plataforma(9, 12, 18)
plataforma(10, 22, 28)
plataforma(8, 31, 37)
plataforma(10, 40, 46)
plataforma(6, 15, 20)

# Posicoes dos cristais
for pos in [
    (5, 5), (8, 14), (5, 17),
    (8, 24), (7, 33), (8, 42), (11, 27)
]:
    colocar(pos[0], pos[1], "C")

# Posicoes dos inimigos
colocar(12, 10, "E")
colocar(12, 35, "E")

# Areas perigosas
colocar(12, 20, "X")
colocar(12, 21, "X")

# Jogador e portal
colocar(12, 1, "J")
colocar(11, 47, "S")

MAPA = ["".join(linha) for linha in MAPA]


# CLASSE PLATAFORMA
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(CINZA)

        pygame.draw.rect(
            self.image, VERDE, (0, 0, TILE, 7)
        )

        self.rect = self.image.get_rect(topleft=(x, y))


# CLASSE CRISTAL
class Cristal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Surface transparente para o cristal
        self.image = pygame.Surface(
            (28, 32), pygame.SRCALPHA
        )

        pygame.draw.polygon(
            self.image, AMARELO,
            [(14, 0), (27, 13), (14, 31), (1, 13)]
        )

        pygame.draw.polygon(
            self.image, BRANCO,
            [(14, 3), (20, 13), (14, 22)]
        )

        self.rect = self.image.get_rect(
            center=(x + TILE // 2, y + TILE // 2)
        )


# CLASSE INIMIGO
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface(
            (30, 30), pygame.SRCALPHA
        )

        pygame.draw.rect(
            self.image, VERMELHO, (0, 0, 30, 30)
        )

        pygame.draw.circle(
            self.image, BRANCO, (9, 10), 4
        )
        pygame.draw.circle(
            self.image, BRANCO, (21, 10), 4
        )

        self.rect = self.image.get_rect(topleft=(x, y))

        self.minimo = x - 80
        self.maximo = x + 80
        self.velocidade = 100

    def update(self, dt):
        # Inimigo patrulha entre dois limites
        self.rect.x += round(self.velocidade * dt)

        if self.rect.left <= self.minimo:
            self.rect.left = self.minimo
            self.velocidade = abs(self.velocidade)

        if self.rect.right >= self.maximo:
            self.rect.right = self.maximo
            self.velocidade = -abs(self.velocidade)


# CLASSE JOGADOR
class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface(
            (30, 36), pygame.SRCALPHA
        )

        pygame.draw.rect(
            self.image, AZUL, (2, 5, 26, 30)
        )

        pygame.draw.circle(
            self.image, (255, 190, 130), (15, 8), 8
        )

        pygame.draw.rect(
            self.image, BRANCO, (8, 14, 4, 4)
        )
        pygame.draw.rect(
            self.image, BRANCO, (19, 14, 4, 4)
        )

        self.rect = self.image.get_rect(topleft=(x, y))
        self.spawn = (x, y)

        self.vel_y = 0
        self.no_chao = False

        self.vidas = 3
        self.pontos = 0
        self.protecao = 0

    def mover(self, teclas, plataformas, dt):
        dx = 0

        # MOVIMENTACAO HORIZONTAL
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx -= 230 * dt

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx += 230 * dt

        self.rect.x += round(dx)

        # COLISAO HORIZONTAL
        for p in plataformas:
            if self.rect.colliderect(p.rect):

                if dx > 0:
                    self.rect.right = p.rect.left

                elif dx < 0:
                    self.rect.left = p.rect.right

        # GRAVIDADE
        self.vel_y = min(self.vel_y + 850 * dt, 600)

        dy = self.vel_y * dt
        self.rect.y += round(dy)

        self.no_chao = False

        # COLISAO VERTICAL
        for p in plataformas:
            if self.rect.colliderect(p.rect):

                if dy > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.no_chao = True

                elif dy < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

    def pular(self):
        # Salto permitido somente quando esta apoiado
        if self.no_chao:
            self.vel_y = -430
            self.no_chao = False


# CLASSE CAMERA
class Camera:
    def __init__(self):
        self.x = 0

    def atualizar(self, jogador, largura_mapa):
        self.x = jogador.rect.centerx - LARGURA // 2

        # Impede a camera de sair dos limites do mapa
        self.x = max(0, min(self.x, largura_mapa - LARGURA))


# CRIAR FASE PELA MATRIZ
def criar_fase():
    plataformas = pygame.sprite.Group()
    cristais = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()

    perigos = []
    jogador = None
    portal = None

    for linha, caracteres in enumerate(MAPA):
        for coluna, simbolo in enumerate(caracteres):

            x = coluna * TILE
            y = linha * TILE

            if simbolo == "P":
                plataformas.add(Plataforma(x, y))

            elif simbolo == "C":
                cristais.add(Cristal(x, y))

            elif simbolo == "E":
                inimigos.add(Inimigo(x, y))

            elif simbolo == "J":
                jogador = Jogador(x, y)

            elif simbolo == "S":
                portal = pygame.Rect(x, y - 40, 35, 80)

            elif simbolo == "X":
                perigos.append(
                    pygame.Rect(x, y, TILE, TILE)
                )

    return jogador, plataformas, cristais, inimigos, perigos, portal


# REINICIAR O JOGO
def reiniciar():
    return criar_fase()


# DESENHAR TEXTO
def escrever(texto, x, y, cor=BRANCO, tipo=fonte):
    imagem = tipo.render(texto, True, cor)
    tela.blit(imagem, (x, y))


# INICIALIZACAO
jogador, plataformas, cristais, inimigos, perigos, portal = criar_fase()

camera = Camera()

largura_mapa = len(MAPA[0]) * TILE
altura_mapa = len(MAPA) * TILE

estado = "inicio"


# LOOP PRINCIPAL
while True:

    dt = min(relogio.tick(FPS) / 1000, 0.04)

    # EVENTOS
    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:

            if estado == "inicio":
                if evento.key == pygame.K_RETURN:
                    estado = "jogando"

            elif estado == "jogando":
                if evento.key in (
                    pygame.K_SPACE,
                    pygame.K_UP,
                    pygame.K_w
                ):
                    jogador.pular()

            elif estado in ("vitoria", "derrota"):
                if evento.key == pygame.K_r:
                    jogador, plataformas, cristais, inimigos, perigos, portal = reiniciar()
                    camera = Camera()
                    estado = "jogando"

    # ATUALIZAR PARTIDA
    if estado == "jogando":

        teclas = pygame.key.get_pressed()

        jogador.mover(teclas, plataformas, dt)
        inimigos.update(dt)

        # COLETA DOS CRISTAIS
        coletados = pygame.sprite.spritecollide(
            jogador, cristais, True
        )

        if coletados:
            jogador.pontos += len(coletados) * 10

            if som:
                som.play()

        agora = pygame.time.get_ticks()

        # DANO E INVULNERABILIDADE
        if agora >= jogador.protecao:

            atingido = (
                pygame.sprite.spritecollide(
                    jogador, inimigos, False
                )
                or any(
                    jogador.rect.colliderect(p)
                    for p in perigos
                )
            )

            if atingido:
                jogador.vidas -= 1
                jogador.protecao = agora + 1500

                jogador.rect.topleft = jogador.spawn
                jogador.vel_y = 0

        # QUEDA ABAIXO DA FASE
        if jogador.rect.top > altura_mapa:
            jogador.vidas -= 1
            jogador.rect.topleft = jogador.spawn
            jogador.vel_y = 0
            jogador.protecao = agora + 1500

        # VITORIA
        if jogador.rect.colliderect(portal):
            if len(cristais) == 0:
                estado = "vitoria"

        # DERROTA
        if jogador.vidas <= 0:
            estado = "derrota"

        camera.atualizar(jogador, largura_mapa)

    # DESENHAR CENARIO
    tela.fill(FUNDO)

    for p in plataformas:
        tela.blit(
            p.image,
            (p.rect.x - camera.x, p.rect.y)
        )

    for c in cristais:
        tela.blit(
            c.image,
            (c.rect.x - camera.x, c.rect.y)
        )

    for e in inimigos:
        tela.blit(
            e.image,
            (e.rect.x - camera.x, e.rect.y)
        )

    for p in perigos:
        pygame.draw.rect(
            tela, VERMELHO,
            (p.x - camera.x, p.y, p.width, p.height)
        )

    pygame.draw.ellipse(
        tela, ROXO,
        (portal.x - camera.x, portal.y,
         portal.width, portal.height)
    )

    # DESENHAR JOGADOR COM PISCADA DURANTE A PROTECAO
    if estado != "inicio":
        if (
            pygame.time.get_ticks() >= jogador.protecao
            or pygame.time.get_ticks() // 100 % 2 == 0
        ):
            tela.blit(
                jogador.image,
                (jogador.rect.x - camera.x, jogador.rect.y)
            )

    # INTERFACE
    if estado == "jogando":
        escrever(
            f"Pontos: {jogador.pontos}  "
            f"Vidas: {jogador.vidas}  "
            f"Cristais: {len(cristais)}",
            15, 15
        )

    elif estado == "inicio":
        escrever("MISSAO DOS CRISTAIS", 160, 210, AMARELO, titulo)
        escrever("ENTER para iniciar", 330, 300)
        escrever("Setas ou A/D para andar", 300, 350)
        escrever("ESPACO para pular", 335, 390)

    elif estado == "vitoria":
        escrever("VOCE VENCEU!", 260, 220, AMARELO, titulo)
        escrever(f"Pontuacao: {jogador.pontos}", 330, 300)
        escrever("R para reiniciar", 350, 350)

    elif estado == "derrota":
        escrever("GAME OVER", 290, 220, VERMELHO, titulo)
        escrever("R para reiniciar", 340, 310)

    pygame.display.flip()
