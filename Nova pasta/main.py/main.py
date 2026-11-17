
import pygame
import random
import math
import sys

pygame.init()

# CONFIGURAÇÕES DA JANELA
LARGURA = 900
ALTURA = 650
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Defesa Orbital")

RELOGIO = pygame.time.Clock()
FPS = 60

# CORES
PRETO = (10, 10, 25)
BRANCO = (255, 255, 255)
VERDE = (0, 220, 80)
VERMELHO = (230, 50, 50)
AZUL = (50, 150, 255)
AMARELO = (255, 220, 0)
CINZA = (100, 100, 100)

FONTE = pygame.font.SysFont("Arial", 25)
FONTE_GRANDE = pygame.font.SysFont("Arial", 55)


# NAVE DO JOGADOR
class Nave(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            AZUL,
            [(20, 0), (40, 38), (20, 28), (0, 38)]
        )

        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(LARGURA // 2, ALTURA // 2))

        self.pos = pygame.Vector2(self.rect.center)

        self.velocidade = 300
        self.vida = 100
        self.ultimo_dano = 0
        self.intervalo_dano = 1000

    def update(self, dt):

        teclas = pygame.key.get_pressed()

        direcao = pygame.Vector2(0, 0)

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            direcao.y -= 1

        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            direcao.y += 1

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            direcao.x -= 1

        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            direcao.x += 1

        if direcao.length_squared() > 0:
            direcao = direcao.normalize()

        self.pos += direcao * self.velocidade * dt

        # LIMITES DA JANELA
        self.pos.x = max(20, min(LARGURA - 20, self.pos.x))
        self.pos.y = max(20, min(ALTURA - 20, self.pos.y))

        self.rect.center = self.pos

        # MIRA NO MOUSE
        mouse = pygame.Vector2(pygame.mouse.get_pos())
        vetor = mouse - self.pos

        if vetor.length_squared() > 0:
            angulo = -math.degrees(math.atan2(vetor.y, vetor.x))
            self.image = pygame.transform.rotate(
                self.original_image, angulo - 90
            )

            self.rect = self.image.get_rect(center=self.pos)


# PROJÉTIL
class Projetil(pygame.sprite.Sprite):

    def __init__(self, origem, destino):
        super().__init__()

        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, AMARELO, (5, 5), 5)

        self.rect = self.image.get_rect(center=origem)

        self.pos = pygame.Vector2(origem)

        direcao = pygame.Vector2(destino) - self.pos

        if direcao.length_squared() > 0:
            direcao = direcao.normalize()
        else:
            direcao = pygame.Vector2(0, 0)

        self.velocidade = 600
        self.movimento = direcao * self.velocidade

    def update(self, dt):

        self.pos += self.movimento * dt
        self.rect.center = self.pos

        # REMOVE PROJÉTIL FORA DA TELA
        if not TELA.get_rect().colliderect(self.rect):
            self.kill()


# INIMIGO EM LINHA RETA
class InimigoReto(pygame.sprite.Sprite):

    def __init__(self, velocidade):
        super().__init__()

        self.image = pygame.Surface((30, 30))
        self.image.fill(VERMELHO)

        lado = random.randint(0, 3)

        if lado == 0:
            pos = (-30, random.randint(0, ALTURA))
        elif lado == 1:
            pos = (LARGURA + 30, random.randint(0, ALTURA))
        elif lado == 2:
            pos = (random.randint(0, LARGURA), -30)
        else:
            pos = (random.randint(0, LARGURA), ALTURA + 30)

        self.pos = pygame.Vector2(pos)

        centro = pygame.Vector2(LARGURA / 2, ALTURA / 2)

        direcao = centro - self.pos

        if direcao.length_squared() > 0:
            direcao = direcao.normalize()

        self.velocidade = velocidade
        self.movimento = direcao * velocidade

        self.rect = self.image.get_rect(center=self.pos)

        self.vida = 1

    def update(self, dt):

        self.pos += self.movimento * dt
        self.rect.center = self.pos


# INIMIGO PERSEGUIDOR
class InimigoPerseguidor(pygame.sprite.Sprite):

    def __init__(self, velocidade):
        super().__init__()

        self.image = pygame.Surface((35, 35))
        self.image.fill((180, 50, 255))

        lado = random.randint(0, 3)

        if lado == 0:
            pos = (-35, random.randint(0, ALTURA))
        elif lado == 1:
            pos = (LARGURA + 35, random.randint(0, ALTURA))
        elif lado == 2:
            pos = (random.randint(0, LARGURA), -35)
        else:
            pos = (random.randint(0, LARGURA), ALTURA + 35)

        self.pos = pygame.Vector2(pos)
        self.velocidade = velocidade

        self.rect = self.image.get_rect(center=self.pos)

        self.vida = 1

    def update(self, dt):

        jogador = pygame.Vector2(nave.pos)

        direcao = jogador - self.pos

        if direcao.length_squared() > 0:
            direcao = direcao.normalize()

        self.pos += direcao * self.velocidade * dt

        self.rect.center = self.pos


# CONFIGURAÇÃO DAS ONDAS
ondas = {
    1: {"quantidade": 5, "velocidade": 100},
    2: {"quantidade": 8, "velocidade": 150},
    3: {"quantidade": 12, "velocidade": 200}
}


# INICIALIZAÇÃO DO JOGO
def reiniciar():

    global nave, todos, inimigos, projeteis
    global pontuacao, onda, gerados
    global ultimo_disparo, jogo_estado
    global tempo_geracao

    nave = Nave()

    todos = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()
    projeteis = pygame.sprite.Group()

    todos.add(nave)

    pontuacao = 0
    onda = 1
    gerados = 0

    ultimo_disparo = 0
    tempo_geracao = 0

    jogo_estado = "jogando"


reiniciar()


# FUNÇÃO PARA GERAR INIMIGOS
def gerar_inimigo():

    global gerados

    dados = ondas[onda]

    velocidade = dados["velocidade"]

    if random.random() < 0.5:
        inimigo = InimigoReto(velocidade)
    else:
        inimigo = InimigoPerseguidor(velocidade * 0.8)

    inimigos.add(inimigo)
    todos.add(inimigo)

    gerados += 1


# INTERFACE
def desenhar_interface():

    # VIDA
    pygame.draw.rect(TELA, CINZA, (20, 20, 200, 22))

    largura_vida = max(0, nave.vida) * 2

    cor = VERDE if nave.vida > 30 else VERMELHO

    pygame.draw.rect(
        TELA,
        cor,
        (20, 20, largura_vida, 22)
    )

    pygame.draw.rect(TELA, BRANCO, (20, 20, 200, 22), 2)

    vida_texto = FONTE.render(
        f"Vida: {nave.vida}",
        True,
        BRANCO
    )

    TELA.blit(vida_texto, (20, 48))

    # PONTUAÇÃO
    texto_pontos = FONTE.render(
        f"Pontos: {pontuacao}",
        True,
        BRANCO
    )

    TELA.blit(texto_pontos, (350, 20))

    # ONDA
    texto_onda = FONTE.render(
        f"Onda: {onda}/3",
        True,
        BRANCO
    )

    TELA.blit(texto_onda, (730, 20))


# LOOP PRINCIPAL
while True:

    dt = RELOGIO.tick(FPS) / 1000

    tempo_atual = pygame.time.get_ticks()

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_p:

                if jogo_estado == "jogando":
                    jogo_estado = "pausado"

                elif jogo_estado == "pausado":
                    jogo_estado = "jogando"

            if evento.key == pygame.K_r:

                if jogo_estado in ("vitoria", "derrota"):
                    reiniciar()

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1 and jogo_estado == "jogando":

                if tempo_atual - ultimo_disparo >= 250:

                    tiro = Projetil(
                        nave.pos,
                        pygame.mouse.get_pos()
                    )

                    projeteis.add(tiro)
                    todos.add(tiro)

                    ultimo_disparo = tempo_atual

    # DESENHO DO FUNDO
    TELA.fill(PRETO)

    if jogo_estado == "jogando":

        # MOVIMENTAÇÃO
        nave.update(dt)
        projeteis.update(dt)
        inimigos.update(dt)

        # GERAÇÃO DOS INIMIGOS
        dados = ondas[onda]

        if gerados < dados["quantidade"]:

            tempo_geracao += dt

            if tempo_geracao >= 1:
                gerar_inimigo()
                tempo_geracao = 0

        # COLISÃO DOS PROJÉTEIS COM INIMIGOS
        for projetil in list(projeteis):

            atingidos = pygame.sprite.spritecollide(
                projetil,
                inimigos,
                False
            )

            if atingidos:

                inimigo = atingidos[0]

                inimigo.vida -= 1

                projetil.kill()

                if inimigo.vida <= 0:

                    inimigo.kill()
                    pontuacao += 10

        # COLISÃO DOS INIMIGOS COM A NAVE
        colisoes = pygame.sprite.spritecollide(
            nave,
            inimigos,
            True
        )

        if colisoes:

            if tempo_atual - nave.ultimo_dano >= nave.intervalo_dano:

                nave.vida -= 10
                nave.ultimo_dano = tempo_atual

        # DERROTA
        if nave.vida <= 0:
            nave.vida = 0
            jogo_estado = "derrota"

        # PROGRESSÃO DAS ONDAS
        if (
            gerados == dados["quantidade"]
            and len(inimigos) == 0
        ):

            if onda < 3:

                onda += 1
                gerados = 0
                tempo_geracao = 0

            else:

                jogo_estado = "vitoria"

    # DESENHAR OBJETOS
    todos.draw(TELA)

    desenhar_interface()

    # PAUSA
    if jogo_estado == "pausado":

        texto = FONTE_GRANDE.render(
            "JOGO PAUSADO",
            True,
            AMARELO
        )

        TELA.blit(
            texto,
            texto.get_rect(center=(LARGURA // 2, ALTURA // 2))
        )

    # VITORIA
    elif jogo_estado == "vitoria":

        texto = FONTE_GRANDE.render(
            "VOCE VENCEU!",
            True,
            VERDE
        )

        TELA.blit(
            texto,
            texto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 30))
        )

        reinicio = FONTE.render(
            "Pressione R para jogar novamente",
            True,
            BRANCO
        )

        TELA.blit(
            reinicio,
            reinicio.get_rect(center=(LARGURA // 2, ALTURA // 2 + 40))
        )

    # DERROTA
    elif jogo_estado == "derrota":

        texto = FONTE_GRANDE.render(
            "GAME OVER",
            True,
            VERMELHO
        )

        TELA.blit(
            texto,
            texto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 30))
        )

        reinicio = FONTE.render(
            "Pressione R para tentar novamente",
            True,
            BRANCO
        )

        TELA.blit(
            reinicio,
            reinicio.get_rect(center=(LARGURA // 2, ALTURA // 2 + 40))
        )

    pygame.display.flip()
