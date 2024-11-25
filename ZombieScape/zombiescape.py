import pygame
import sys
from collections import deque
import math
import constantes
import fases
from pygame.locals import *
from sys import exit
from random import randint
import os

pygame.init()
pygame.mixer.init()
#pygame.mixer.music.set_volume()
musica_pause = 'sons/CrEEP.wav'
musica_jogo = 'sons/atmoseerie01.mp3.flac'
musica_tela_inicial = 'sons/ambient_horror_track01.wav'

def tocar_musica(musica):
    pygame.mixer.music.stop()  
    pygame.mixer.music.load(musica)  
    pygame.mixer.music.play(-1)

tocar_musica(musica_tela_inicial)

diretorio_principal = os.path.dirname(__file__)
diretorio_sprites = os.path.join(diretorio_principal, 'sprites')
diretorio_sons = os.path.join(diretorio_principal, 'sons')

tela = pygame.display.set_mode((constantes.LARGURA, constantes.ALTURA))

pygame.display.set_caption('ZombiEscape')

# Estados do jogo
TELA_INICIAL = "tela_inicial"
JOGANDO = "jogando"
PAUSADO = "pausado"
ZERADO = "zerado"
GAME_OVER = "game_over"

estado_jogo = TELA_INICIAL

sprites_personagem = pygame.image.load(os.path.join(diretorio_sprites, 'Personagem.png')).convert_alpha()

class Personagem(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, personagem_grupo)
        self.imagens_personagem = []
        for i in range(3):
            img = sprites_personagem.subsurface((i*32,0), (32,32))
            img = pygame.transform.scale(img, (32*constantes.TAMANHO_PERSONAGEM, 32*constantes.TAMANHO_PERSONAGEM))
            self.imagens_personagem.append(img)

        self.vidas = constantes.VIDAS_PERSONAGEM
        self.inventario = {'chaves': 0, 'cristais': 0}
            
        self.x = constantes.POSICAO_PERSONAGEM[0]
        self.y = constantes.POSICAO_PERSONAGEM[1] 
        self.posicao = constantes.POSICAO_PERSONAGEM
        self.vel = constantes.VELOCIDADE_PERSONAGEM
        self.index_lista = 0
        self.image = self.imagens_personagem[self.index_lista]
        self.rect = self.image.get_rect()
        self.rect.center = (self.posicao)

        self.som = pygame.mixer.Sound('sons/Scream_Male_02.wav')
        self.som.set_volume(0.5)
        self.empurrao = pygame.mixer.Sound('sons/Stab_Knife_00.wav')

        self.mask = pygame.mask.from_surface(self.image)
        #self.radius = 25

    def update(self):
        if self.index_lista > 2:
            self.index_lista = 0
        
        self.index_lista += 0.25
        self.image = self.imagens_personagem[int(self.index_lista)]
        self.mask = pygame.mask.from_surface(self.image)
    
        self.walk()
        
        self.rect.center = (self.x, self.y)

        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            self.repelir_inimigos(inimigos_grupo)

    def walk(self):
        if pygame.key.get_pressed()[K_a] or pygame.key.get_pressed()[K_LEFT]:
            self.x -= self.vel
            self.rect.center = (self.x, self.y)
            if self.colidir_solidos():
                self.x += self.vel
                self.rect.center = (self.x, self.y)

        if pygame.key.get_pressed()[K_d] or pygame.key.get_pressed()[K_RIGHT]:
            self.x += self.vel
            self.rect.center = (self.x, self.y)
            if self.colidir_solidos():
                self.x -= self.vel
                self.rect.center = (self.x, self.y)

        if pygame.key.get_pressed()[K_w] or pygame.key.get_pressed()[K_UP]:
            self.y -= self.vel
            self.rect.center = (self.x, self.y)
            if self.colidir_solidos():
                self.y += self.vel
                self.rect.center = (self.x, self.y)

        if pygame.key.get_pressed()[K_s] or pygame.key.get_pressed()[K_DOWN]:
            self.y += self.vel
            self.rect.center = (self.x, self.y)
            if self.colidir_solidos():
                self.y -= self.vel
                self.rect.center = (self.x, self.y)
    
    def repelir_inimigos(self, inimigos_grupo, forca=20):

        for inimigo in inimigos_grupo:
            if pygame.sprite.collide_mask(self, inimigo):
                self.empurrao.play()
                # Calcula direção do empurrão (inimigo se afasta do personagem)
                direcao = pygame.math.Vector2(inimigo.rect.center) - pygame.math.Vector2(self.rect.center)
                if direcao.length() > 0:  # Certifica que a direção não é nula
                    direcao = direcao.normalize() * forca
                    inimigo.posicao += direcao  # Ajusta a posição do inimigo
                    inimigo.rect.center = inimigo.posicao  # Atualiza o retângulo de colisão

    def colidir_solidos(self):
        solidos_list = solidos.sprites()
        for solido in solidos_list:
            if solido != self and pygame.sprite.collide_mask(self, solido):
                return True   

    def empurrado(self, direcao, forca=10):
        if direcao.length() > 0:
            direcao = direcao.normalize() * forca
            self.rect.center += direcao

    def draw_mask(self, surface):
        mask_offset = (self.rect.x, self.rect.y)
        for x, y in self.mask.outline():
            pygame.draw.circle(surface, (255,0,0), (x + mask_offset[0], y + mask_offset[1]), 1)

class Zumbi(pygame.sprite.Sprite):
    def __init__(self, posicao):
        pygame.sprite.Sprite.__init__(self, inimigos_grupo,  todas_as_sprites, solidos)
        self.imagens_zumbi = []
        for i in range(3):
            img = sprites_personagem.subsurface((i*32,32), (32,32))
            img = pygame.transform.scale(img, (32*constantes.TAMANHO_ZUMBI, 32*constantes.TAMANHO_ZUMBI))
            self.imagens_zumbi.append(img)
        self.posicao = posicao
        self.vel = constantes.VELOCIDADE_ZUMBI
        self.index_lista = 0
        self.image = self.imagens_zumbi[self.index_lista]
        self.rect = self.image.get_rect()
        self.rect.center = self.posicao
        self.som = pygame.mixer.Sound('sons/Large Monster Death 01.wav')
        self.som.set_volume(0.5)
        self.wait_time = 0

        self.mask = pygame.mask.from_surface(self.image)

        self.direcao = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()

    def perseguir(self):
        vetor_personagem = pygame.math.Vector2(personagem.rect.center)
        vetor_zumbi = pygame.math.Vector2(self.rect.center)
        distancia = self.get_distancia_vetor(vetor_personagem, vetor_zumbi)

        if distancia > 0:
            self.direcao = (vetor_personagem - vetor_zumbi).normalize()
        else:
            self.direcao = pygame.math.Vector2()

        self.velocity = self.direcao * self.vel
        self.posicao += self.velocity

        self.rect.centerx = self.posicao.x
        self.rect.centery = self.posicao.y

    def get_distancia_vetor(self, vetor_personagem, vetor_zumbi):
        return (vetor_personagem - vetor_zumbi).magnitude()

    def draw_mask(self, surface):
        mask_offset = (self.rect.x, self.rect.y)
        for x, y in self.mask.outline():
            pygame.draw.circle(surface, (255,0,0), (x + mask_offset[0], y + mask_offset[1]), 1)

    def colidir_solidos(self):
        #personagem = personagem_grupo.sprites()
        solidos_list = solidos.sprites()
        # for p in personagem:
        #     solidos_list.append(p)
        for solido in solidos_list:
            if solido != self and pygame.sprite.collide_mask(self, solido):
                overlap = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(solido.rect.center)
                if overlap.length() > 0:
                    overlap = overlap.normalize() * self.vel
                    self.posicao += overlap
                    self.rect.center = self.posicao 
                return True   

    def update(self):
        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_zumbi[int(self.index_lista)]
        
        if self.wait_time > 0:
            self.wait_time -=1
        else:
            self.perseguir()

        if pygame.sprite.collide_mask(self, personagem):
            #direcao = pygame.math.Vector2(personagem.rect.center) - pygame.math.Vector2(self.rect.center)
            #personagem.empurrado(direcao, forca=50)
            self.wait_time = 30
            self.som.play()
        self.colidir_solidos()

# FUNÇÃO PARA CALCULAR A DIREÇÃO DO MOVIMENTO
def get_direction(source, target):
    dx = target[0] - source[0]
    dy = target[1] - source[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    if distance == 0:
        return 0, 0
    return dx / distance, dy / distance

class Fantasma(pygame.sprite.Sprite):
    def __init__(self, posicao, inimigos_grupo, todas_as_sprites):
        #super().__init__()
        pygame.sprite.Sprite.__init__(self, inimigos_grupo,  todas_as_sprites, solidos)
        image = pygame.image.load(os.path.join(diretorio_sprites, 'anim-nme-ghost.png')).convert_alpha()
        self.imagens_fantasma = []
        for i in range(6):
            img = image.subsurface((i*32,0), (32,32))
            img = pygame.transform.scale(img, (32*constantes.TAMANHO_FANTASMA, 32*constantes.TAMANHO_FANTASMA))
            self.imagens_fantasma.append(img)

        self.index_lista = 0

        self.image = self.imagens_fantasma[self.index_lista]
        self.posicao = posicao
        self.rect = self.image.get_rect()
        self.rect.center = self.posicao
        self.speed = constantes.VELOCIDADE_FANTASMA
        self.target = None
        self.attack_cooldown = constantes.COOLDOWN_FANTASMA  # Tempo de espera entre ataques
        self.last_attack_time = pygame.time.get_ticks()
        self.direction = (0, 0)
        self.attacking = False

        self.som = pygame.mixer.Sound('sons/ghost_voice.wav')
        self.som.set_volume(0.5)

        self.mask = pygame.mask.from_surface(self.image)


    def attack(self, personagem):
        current_time = pygame.time.get_ticks()
        solidos_list = solidos.sprites()

        # Se não está atacando e o cooldown passou, define um novo alvo
        if not self.attacking and current_time - self.last_attack_time > self.attack_cooldown:
            self.target = personagem.rect.center
            self.direction = get_direction(self.rect.center, self.target)
            self.attacking = True

        # Move-se em direção ao alvo, se atacando
        if self.attacking:
            self.rect.x += self.direction[0] * self.speed
            self.rect.y += self.direction[1] * self.speed
            self.som.play()

            # Verifica colisão com as paredes
            # for solido in solidos_list:
            #     if solido != self and pygame.sprite.collide_mask(self, solido):
            #         self.stop_attack()
            #         return
                
                
            if self.rect.left < 0 or self.rect.right > constantes.LARGURA or self.rect.top < 0 or self.rect.bottom > constantes.ALTURA:
                self.stop_attack()
                return

    def stop_attack(self):
        self.attacking = False
        self.target = None
        self.last_attack_time = pygame.time.get_ticks()

    def draw_mask(self, surface):
        mask_offset = (self.rect.x, self.rect.y)
        for x, y in self.mask.outline():
            pygame.draw.circle(surface, (255,0,0), (x + mask_offset[0], y + mask_offset[1]), 1)

    def update(self):
        if self.index_lista > 5:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_fantasma[int(self.index_lista)]
        self.attack(personagem)
    


class Chave(pygame.sprite.Sprite):
    def __init__(self, posicao):
        pygame.sprite.Sprite.__init__(self, todas_as_sprites, chaves_grupo)
        image = pygame.image.load(os.path.join(diretorio_sprites, 'chave.png')).convert_alpha()
        self.image = pygame.transform.scale(image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.posicao = posicao
        self.rect.center = self.posicao
        self.som = pygame.mixer.Sound('sons/key2_pickup.wav')

        self.mask = pygame.mask.from_surface(self.image)
        #self.radius = 15

    def update(self):
        self.rect.center = self.posicao
        self.image = pygame.transform.scale(self.image, (32*2, 32*2))

    def draw_mask(self, surface):
        mask_offset = (self.rect.x, self.rect.y)
        for x, y in self.mask.outline():
            pygame.draw.circle(surface, (255,0,0), (x + mask_offset[0], y + mask_offset[1]), 1)

class Cristal(pygame.sprite.Sprite):
    def __init__(self, posicao):
        pygame.sprite.Sprite.__init__(self, todas_as_sprites, cristais_grupo)
        image = pygame.image.load(os.path.join(diretorio_sprites, 'crystal-qubodup-ccby3-32-blue.png')).convert_alpha()
        self.imagens_cristal = []
        for i in range(8):
            img = image.subsurface((i*32,0), (32,32))
            img = pygame.transform.scale(img, (32*2, 32*2))
            self.imagens_cristal.append(img)

        self.index_lista = 0

        self.image = self.imagens_cristal[self.index_lista]
        self.posicao = posicao
        self.rect = self.image.get_rect()
        self.rect.center = self.posicao
        self.som = pygame.mixer.Sound('sons/Waterharpsound-drip04.wav')

        self.mask = pygame.mask.from_surface(self.image)
        #self.radius = 15

    def update(self):
        self.rect.center = self.posicao
        if self.index_lista > 7:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_cristal[int(self.index_lista)]

    def draw_mask(self, surface):
        mask_offset = (self.rect.x, self.rect.y)
        for x, y in self.mask.outline():
            pygame.draw.circle(surface, (255,0,0), (x + mask_offset[0], y + mask_offset[1]), 1)

class Vida(pygame.sprite.Sprite):
    def __init__(self, posicao):
        pygame.sprite.Sprite.__init__(self, todas_as_sprites, vidas_grupo)
        image = pygame.image.load(os.path.join(diretorio_sprites, 'heart.png')).convert_alpha()
        self.image = pygame.transform.scale(image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.posicao = posicao
        self.rect.center = self.posicao
        self.som = pygame.mixer.Sound('sons/life_pickup.flac')

        self.mask = pygame.mask.from_surface(self.image)
        #self.radius = 15

    def update(self):
        self.rect.center = self.posicao
        self.image = pygame.transform.scale(self.image, (32*2, 32*2))

    def draw_mask(self, surface):
        mask_offset = (self.rect.x, self.rect.y)
        for x, y in self.mask.outline():
            pygame.draw.circle(surface, (255,0,0), (x + mask_offset[0], y + mask_offset[1]), 1)

class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self,todas_as_sprites, solidos)
        self.image = pygame.Surface((constantes.TAMANHO_OBSTACULO, constantes.TAMANHO_OBSTACULO))
        self.image.fill(constantes.MARROM)
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def draw_mask(self, surface):
        mask_offset = (self.rect.x, self.rect.y)
        for x, y in self.mask.outline():
            pygame.draw.circle(surface, (255,0,0), (x + mask_offset[0], y + mask_offset[1]), 1)

class Porta(pygame.sprite.Sprite):
    def __init__(self, posicao, chaves_necessarias):
        super().__init__()
        pygame.sprite.Sprite.__init__(self,todas_as_sprites, solidos)
        self.image = pygame.Surface((constantes.TAMANHO_OBSTACULO*1.7, constantes.TAMANHO_OBSTACULO*1.7))
        self.image.fill(constantes.CINZA)
        self.posicao = posicao
        self.rect = self.image.get_rect(center=posicao)
        self.chaves_necessarias = chaves_necessarias
        self.visivel = True

    def visibilidade(self):
        if self.visivel:
            self.desenhar(tela)   
            if self.verificar_se_pode_atravessar(personagem.inventario['chaves']):
                self.desaparecer()
        else:
            self.kill()

    def update(self):
        self.visibilidade()

    def verificar_se_pode_atravessar(self, numero_chaves):
        return numero_chaves >= self.chaves_necessarias
    

    def desaparecer(self):
        self.visivel = False

    def desenhar(self, tela):
        if self.visivel:
            tela.blit(self.image, self.rect)
            if self.chaves_necessarias - personagem.inventario['chaves'] >= 0:
                # Mostrar o número de chaves necessárias dentro do obstáculo
                texto_esquerda = font.render(str(self.chaves_necessarias - personagem.inventario['chaves']), True, (255,255,255))
                texto_esquerda_rect = texto_esquerda.get_rect(center=(self.rect.centerx-55, self.rect.centery))
                tela.blit(texto_esquerda, texto_esquerda_rect)

                texto_baixo = font.render(str(self.chaves_necessarias - personagem.inventario['chaves']), True, (255,255,255))
                texto_baixo_rect = texto_baixo.get_rect(center=(self.rect.centerx, self.rect.centery+55))
                tela.blit(texto_baixo, texto_baixo_rect)

                texto_direita = font.render(str(self.chaves_necessarias - personagem.inventario['chaves']), True, (255,255,255))
                texto_direita_rect = texto_direita.get_rect(center=(self.rect.centerx+55, self.rect.centery))
                tela.blit(texto_direita, texto_direita_rect)

                texto_cima = font.render(str(self.chaves_necessarias - personagem.inventario['chaves']), True, (255,255,255))
                texto_cima_rect = texto_cima.get_rect(center=(self.rect.centerx, self.rect.centery-55))
                tela.blit(texto_cima, texto_cima_rect)

class Porta_principal(pygame.sprite.Sprite):
    def __init__(self, posicao, cristais_necessarios=4):
        super().__init__()
        pygame.sprite.Sprite.__init__(self,todas_as_sprites, solidos)
        self.image = pygame.Surface((constantes.TAMANHO_OBSTACULO*1.7, constantes.TAMANHO_OBSTACULO*1.7))
        self.image.fill(constantes.DOURADO)
        self.posicao = posicao
        self.rect = self.image.get_rect(center=posicao)
        self.cristais_necessarios = cristais_necessarios
        self.visivel = True

    def visibilidade(self):
        if self.visivel:
            self.desenhar(tela)   
            if self.verificar_se_pode_atravessar(personagem.inventario['cristais']):
                self.desaparecer()
        else:
            self.kill()

    def update(self):
        self.visibilidade()

    def verificar_se_pode_atravessar(self, numero_cristais):
        return numero_cristais >= self.cristais_necessarios
    

    def desaparecer(self):
        self.visivel = False

    def desenhar(self, tela):
        if self.visivel:
            tela.blit(self.image, self.rect)
            if self.cristais_necessarios - personagem.inventario['cristais'] >= 0:
                # Mostrar o número de chaves necessárias dentro do obstáculo
                texto_baixo = font.render(str(self.cristais_necessarios - personagem.inventario['cristais']), True, (255,255,255))
                texto_baixo_rect = texto_baixo.get_rect(center=(self.rect.centerx, self.rect.centery+55))
                tela.blit(texto_baixo, texto_baixo_rect)

#CRIANDO GRUPOS E INSANCIANDO OBJETOS
personagem_grupo = pygame.sprite.Group()
chaves_grupo = pygame.sprite.Group()
vidas_grupo = pygame.sprite.Group()
cristais_grupo = pygame.sprite.Group()
todas_as_sprites = pygame.sprite.Group()
solidos = pygame.sprite.Group()
inimigos_grupo = pygame.sprite.Group()
#chave = Chave((constantes.X_CHAVE,constantes.Y_CHAVE))
personagem = Personagem()
#zumbi = Zumbi((500,100))
#z2 = Zumbi((100,500))

# FUNÇÃO PARA DESENHAR A FASE COM BASE NO ARRAY
def desenhar_fase(fase, todas_as_sprites, player):
    for sprite in todas_as_sprites:
        sprite.kill()
    todas_as_sprites.empty()
    for row in range(len(fase.array)):
        for col in range(len(fase.array[row])):
            x = col * 50  # Posição x no cenário
            y = row * 50  # Posição y no cenário
            coordenada = (col,row)
            if fase.array[row][col] == 1:
                obstaculo = Obstaculo(x, y)
                #todas_as_sprites.add(obstaculo)
            elif fase.array[row][col] == 2:
                zumbi = Zumbi((x,y))
            elif fase.array[row][col] == 3 and not (coordenada in fase.objetos_coletados):
                chave = Chave((x,y))
                print(coordenada)
            elif fase.array[row][col] == 4 and not (coordenada in fase.objetos_coletados):
                vida = Vida((x,y))
                print(coordenada)
            elif fase.array[row][col] == 7 and not (coordenada in fase.objetos_coletados):
                cristal = Cristal((x,y))
                print(coordenada)
            elif fase.array[row][col] == 5:
                fantasma = Fantasma((x,y), inimigos_grupo=inimigos_grupo, todas_as_sprites=todas_as_sprites)
            elif type(fase.array[row][col]) == tuple and fase.array[row][col][0] == 2 and fase.array[row][col][1] >= personagem.inventario['chaves']:
                porta = Porta((x,y-20),fase.array[row][col][1])
            elif type(fase.array[row][col]) == tuple and fase.array[row][col][0] == 1 and fase.array[row][col][1] >= personagem.inventario['cristais']:
                porta_principal = Porta_principal((x,y-20),fase.array[row][col][1])

def coletar_objeto(fase, linha, coluna):
    fase.objetos_coletados.add((linha, coluna))


# Função para calcular posições automaticamente
def calcular_posicoes(raiz, inicio=(constantes.LARGURA // 2, constantes.ALTURA // 7), distancia=75):
    posicoes = {}
    visitados = set()

    def dfs(fase, x, y):
        if fase in visitados:
            return
        visitados.add(fase)

        # Define a posição da fase atual
        posicoes[fase] = (x, y)

        # Calcula as posições das conexões
        for direcao, proxima_fase in fase.conexoes.items():
            if proxima_fase not in visitados:
                if direcao == "cima":
                    dfs(proxima_fase, x, y - distancia)
                elif direcao == "baixo":
                    dfs(proxima_fase, x, y + distancia)
                elif direcao == "esquerda":
                    dfs(proxima_fase, x - distancia, y)
                elif direcao == "direita":
                    dfs(proxima_fase, x + distancia, y)

    # Começa pela fase inicial (raiz)
    dfs(raiz, inicio[0], inicio[1])
    return posicoes

# Calcular posições das fases (começando na fase1)
posicoes = calcular_posicoes(fases.fase1)

# Função para encontrar o caminho entre dois nós usando BFS
def encontrar_caminho(inicio, destino):
    visitados = set()
    fila = deque([(inicio, [])])

    while fila:
        fase_atual, caminho = fila.popleft()

        if fase_atual in visitados:
            continue

        visitados.add(fase_atual)
        novo_caminho = caminho + [fase_atual]

        if fase_atual == destino:
            return novo_caminho

        for proxima_fase in fase_atual.conexoes.values():
            if proxima_fase not in visitados:
                fila.append((proxima_fase, novo_caminho))

    return None 

# Função para desenhar o grafo
def desenhar_grafo(tela, posicoes, selecionados):
    # Cores e fontes
    cor_fase = (255, 255, 255)
    cor_dourado = (255, 215, 0)
    cor_vermelho = (255, 0, 0)
    cor_conexao = (255, 255, 255)
    cor_caminho = (255, 0, 0)
    fonte = pygame.font.Font(None, 24)

    # Desenhar conexões
    for fase in posicoes:
        x, y = posicoes[fase]
        for direcao, proxima_fase in fase.conexoes.items():
            if proxima_fase in posicoes:
                destino_x, destino_y = posicoes[proxima_fase]
                pygame.draw.line(tela, cor_conexao, (x, y), (destino_x, destino_y), 2)

    # Desenhar caminho se houver dourado e vermelho
    if selecionados["vermelho"]:
        caminho = encontrar_caminho(sala_atual, selecionados["vermelho"])
        if caminho:
            for i in range(len(caminho) - 1):
                x1, y1 = posicoes[caminho[i]]
                x2, y2 = posicoes[caminho[i + 1]]
                pygame.draw.line(tela, cor_caminho, (x1, y1), (x2, y2), 3)

    # Desenhar fases
    for fase, (x, y) in posicoes.items():
        # Determinar cor com base nos selecionados
        if fase == sala_atual:
            cor = cor_dourado
        elif fase == selecionados["vermelho"]:
            cor = cor_vermelho
        else:
            cor = cor_fase

        pygame.draw.circle(tela, cor, (x, y), 20)
        if fase.nome == 'Início' or fase.nome == 'Fim':
            texto = fonte.render(fase.nome, True, (0, 0, 0))
            texto_rect = texto.get_rect(center=(x, y))
            tela.blit(texto, texto_rect)

# Função para detectar clique em um nó
def detectar_clique(posicoes, mouse_pos):
    for fase, (x, y) in posicoes.items():
        if (x - mouse_pos[0]) ** 2 + (y - mouse_pos[1]) ** 2 <= 20 ** 2:
            return fase
    return None

# Dicionário para gerenciar seleções
selecionados = {"dourado": None, "vermelho": None}


sala_inicial = fases.fase1
sala_final = fases.fim
desenhar_fase(sala_inicial, todas_as_sprites, personagem)
sala_atual = sala_inicial

som_gameover = pygame.mixer.Sound('sons/game-over-2.wav')

font = pygame.font.Font(None, 36)
relogio = pygame.time.Clock()
rodando = True

#LOOP PRINCIPAL DO JOGO
while rodando:
    relogio.tick(30)
    tela.fill(constantes.PRETO)
    for event in pygame.event.get():
        if event.type == QUIT:
            rodando = False

        if estado_jogo == TELA_INICIAL:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter para iniciar
                    estado_jogo = JOGANDO
                    tocar_musica(musica_jogo)

        elif estado_jogo == JOGANDO:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # P para pausar
                    estado_jogo = PAUSADO
                    tocar_musica(musica_pause)

        elif estado_jogo == PAUSADO:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # P para despausar
                    tocar_musica(musica_jogo)
                    estado_jogo = JOGANDO
                if event.key == pygame.K_e:
                    desenhar_fase(sala_inicial,todas_as_sprites,personagem)
                    personagem.posicao = constantes.POSICAO_PERSONAGEM
                    personagem.rect.center = personagem.posicao
                    personagem.vidas = 5
                    personagem.inventario['chaves'] = 0
                    personagem.inventario['cristais'] = 0
                    sala_atual = sala_inicial
                    for fase in fases.Fase.todas_as_fases:
                        fase.objetos_coletados.clear()
                    tocar_musica(musica_tela_inicial)
                    estado_jogo = TELA_INICIAL
                elif event.key == pygame.K_q:  # Q para sair
                    rodando = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Detectar clique
                clicado = detectar_clique(posicoes, pygame.mouse.get_pos())
                if clicado:
                    # Regras de seleção
                    if clicado == selecionados["vermelho"]:
                        # Se clicar no vermelho, desmarca
                        selecionados["vermelho"] = None
                    elif selecionados["vermelho"] is None:
                        # Marca como vermelho se não houver vermelho
                        selecionados["vermelho"] = clicado

        elif estado_jogo == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter para reiniciar
                    desenhar_fase(sala_inicial,todas_as_sprites,personagem)
                    personagem.posicao = constantes.POSICAO_PERSONAGEM
                    personagem.rect.center = personagem.posicao
                    personagem.vidas = 5
                    personagem.inventario['chaves'] = 0
                    personagem.inventario['cristais'] = 0
                    sala_atual = sala_inicial
                    for fase in fases.Fase.todas_as_fases:
                        fase.objetos_coletados.clear()
                    estado_jogo = TELA_INICIAL
                    tocar_musica(musica_tela_inicial)
                if event.key == pygame.K_SPACE:
                    desenhar_fase(sala_inicial,todas_as_sprites,personagem)
                    personagem.posicao = constantes.POSICAO_PERSONAGEM
                    personagem.rect.center = personagem.posicao
                    personagem.vidas = 5
                    sala_atual = sala_inicial
                    estado_jogo = JOGANDO
                if event.key == pygame.K_q:  # Q para sair
                    rodando = False

        elif estado_jogo == ZERADO:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    desenhar_fase(sala_inicial,todas_as_sprites,personagem)
                    personagem.posicao = constantes.POSICAO_PERSONAGEM
                    personagem.vidas = 5
                    personagem.inventario['chaves'] = 0
                    personagem.inventario['cristais'] = 0
                    sala_atual = sala_inicial
                    for fase in fases.Fase.todas_as_fases:
                        fase.objetos_coletados.clear()
                    estado_jogo = TELA_INICIAL
                    tocar_musica(musica_tela_inicial)
                if event.key == pygame.K_q:  # Q para sair
                    rodando = False

    if estado_jogo == TELA_INICIAL:
        texto_tela_inicial = font.render("ZOMBIESCAPE", True, (255,255,255))
        texto_tela_inicial2 = font.render("Pressione Enter para começar", True, (255,255,255))
        creditos = font.render("Game by Carlos Marcelo Dowsley and Letícia Souza de Missena",True,(255,255,255))
        tela.blit(texto_tela_inicial, ((constantes.LARGURA/2)-100,(constantes.ALTURA/2)-100))
        tela.blit(texto_tela_inicial2, ((constantes.LARGURA/2.5)-100,constantes.ALTURA/2))
        tela.blit(creditos,(10,(constantes.ALTURA - 40)))

    elif estado_jogo == JOGANDO:

        #COLETANDO CHAVES
        coletou_chaves = pygame.sprite.spritecollide(personagem, chaves_grupo, True, pygame.sprite.collide_mask)
        if coletou_chaves:
            coletou_chaves[0].som.play()
            coletar_objeto(sala_atual,int((coletou_chaves[0].posicao[0])//50),int((coletou_chaves[0].posicao[1])//50))
            personagem.inventario['chaves'] += 1
            print (sala_atual.objetos_coletados)
            print(personagem.inventario['chaves'])
            #coletou_chaves[0].posicao = (randint(40, 600), randint(50, 430))

        #COLETANDO VIDAS
        coletou_vidas = pygame.sprite.spritecollide(personagem, vidas_grupo, False, pygame.sprite.collide_mask)
        if coletou_vidas:
            if personagem.vidas >= constantes.MAXIMO_VIDAS_PERSONAGEM:
                pass
            else:
                coletou_vidas[0].som.play()
                personagem.vidas += 1
                coletar_objeto(sala_atual,int((coletou_vidas[0].posicao[0])//50),int((coletou_vidas[0].posicao[1])//50))
                coletou_vidas[0].kill()
                print (sala_atual.objetos_coletados)
                print(personagem.vidas)
                #coletou_vidas[0].posicao = (randint(40, 600), randint(50, 430))

        #COLETANDO CRISTAIS
        coletou_cristais = pygame.sprite.spritecollide(personagem, cristais_grupo, True, pygame.sprite.collide_mask)
        if coletou_cristais:
            coletou_cristais[0].som.play()
            personagem.inventario['cristais'] += 1
            coletar_objeto(sala_atual,int((coletou_cristais[0].posicao[0])//50),int((coletou_cristais[0].posicao[1])//50))
            print (sala_atual.objetos_coletados)
            print(personagem.inventario['cristais'])
            #coletou_cristais[0].posicao = (randint(40, 600), randint(50, 430))

        # #COLIDINDO COM INIMIGOS
        if pygame.sprite.spritecollide(personagem, inimigos_grupo, False, pygame.sprite.collide_mask):
            personagem.vidas -= 1
            personagem.som.play()
            pygame.time.delay(100)
            if personagem.vidas <= 0:
                print("GAME OVER")
                som_gameover.play()
                estado_jogo = GAME_OVER

        if sala_atual == sala_inicial:
            instrucoes = font.render("Aperte W, A, S, D ou as setas para se movimentar",True,(255,255,255))
            instrucoes4 = font.render("Aperte espaço para empurrar um inimigo",True,(255,255,255))
            instrucoes2 = font.render("Aperte P para pausar",True,(255,255,255))
            instrucoes3 = font.render("Colete 4 cristais para escapar do labirinto",True,(255,255,255))
            tela.blit(instrucoes, (200,constantes.ALTURA//4))
            tela.blit(instrucoes4,(250,constantes.ALTURA//3))
            tela.blit(instrucoes2, (350,(constantes.ALTURA//2.5)))
            tela.blit(instrucoes3, (250,(constantes.ALTURA//2)))

        if sala_atual == sala_final and personagem.rect.centery > 20:
            estado_jogo = ZERADO

        if personagem.x > 960 and "direita" in sala_atual.conexoes:
            sala_atual = sala_atual.conexoes["direita"]
            personagem.x = 0
            desenhar_fase(sala_atual, todas_as_sprites, personagem)
            if sala_atual.som:
                sala_atual.som.play()
        elif personagem.x < 0 and "esquerda" in sala_atual.conexoes:
            sala_atual = sala_atual.conexoes["esquerda"]
            personagem.x = 960
            desenhar_fase(sala_atual, todas_as_sprites, personagem)
            if sala_atual.som:
                sala_atual.som.play()
        elif personagem.y < 0 and "cima" in sala_atual.conexoes:
            sala_atual = sala_atual.conexoes["cima"]
            personagem.y = 720
            desenhar_fase(sala_atual, todas_as_sprites, personagem)
            if sala_atual.som:
                sala_atual.som.play()
        elif personagem.y > 720 and "baixo" in sala_atual.conexoes:
            sala_atual = sala_atual.conexoes["baixo"]
            personagem.y = 0
            desenhar_fase(sala_atual, todas_as_sprites, personagem)
            if sala_atual.som:
                sala_atual.som.play()

        
        todas_as_sprites.draw(tela)
        personagem_grupo.draw(tela)
        #personagem.draw_mask(tela)
        # for obj in solidos.sprites():
        #     obj.draw_mask(tela)
        #pygame.draw.rect(tela, (255,0,0), chave, 2)
        # personagem.draw_mask(tela)
        # chave.draw_mask(tela)
        # zumbi.draw_mask(tela)
        # z2.draw_mask(tela)
        todas_as_sprites.update()
        personagem_grupo.update()

        mensagem = font.render(f"Chaves: {personagem.inventario['chaves']}  Cristais: {personagem.inventario['cristais']}   Vidas: {personagem.vidas}", True, (255,255,255))
        fase_texto = font.render(f"Fase: {sala_atual.nome}",True,(255,255,255))
        tela.blit(mensagem, (585,690))
        tela.blit(fase_texto,(100,690))

    elif estado_jogo == PAUSADO:
        desenhar_grafo(tela, posicoes, selecionados)
        texto_pause = font.render("Jogo Pausado", True, (255,255,255))
        texto_pause2 = font.render("Pressione P para continuar, E para a tela inicial ou Q para sair",True,(255,255,255))
        tela.blit(texto_pause, (constantes.LARGURA/2.5,(constantes.ALTURA/2)+200))
        tela.blit(texto_pause2,((constantes.LARGURA/7),(constantes.ALTURA/2)+300))

    elif estado_jogo == ZERADO:
        texto_zerado = font.render("Parabéns! Você conseguiu zerar o ZombiEscape!", True, (255,255,255))
        texto_zerado2 = font.render("Pressione Enter para voltar à tela inicial ou Q para sair",True,(255,255,255))
        creditos = font.render("Game by Carlos Marcelo Dowsley and Letícia Souza de Missena",True,(255,255,255))
        tela.blit(texto_zerado, (constantes.LARGURA/5,(constantes.ALTURA/4)))
        tela.blit(texto_zerado2,((constantes.LARGURA/6),(constantes.ALTURA/2)))
        tela.blit(creditos,(10,(constantes.ALTURA - 40)))

    elif estado_jogo == GAME_OVER:
        texto_gameover = font.render("GAME OVER", True, (255,255,255))
        texto_gameover2 = font.render("Pressione Enter para voltar ao início ou pressione espaço para continuar",True,(255,255,255))
        tela.blit(texto_gameover, (constantes.LARGURA/2.5,(constantes.ALTURA/2)-100))
        tela.blit(texto_gameover2,((constantes.LARGURA/10)-50,(constantes.ALTURA/2)))

    #pygame.display.update()
    pygame.display.flip()
