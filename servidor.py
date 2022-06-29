# Alessandra // Hacjesse // Matheus

import socket
from _thread import *
import random
clientsAtivo = 0
words = [
    'sockey', 'javascript', 'ifpb', 'sistemas para internet', 'redes',
    'onibus', 'bicicleta', 'sistemas operacionais', 'mesa', 'teclado',
    'cleopatra', 'melao', 'caneca', 'uva', 'abacaxi'
]
games = []

class Game:
    word = ""
    gameString = ""
    incorrectGuesses = 0
    incorrectLetters = 0
    turn = 1
    lock = 0
    completou = False

    def __init__(self, word, num_players_requested): #metodo que vai incializar o jogo
        self.incorrectLetters = []
        self.lock = allocate_lock()
        self.word = word
        for i in range(len(word)):# vai ler o tamanho da palavra para determinar as 'dicas'
            self.gameString += "_"
        if num_players_requested == 1:
            self.completou = True

    def getStatus(self):  # metodo que vai retornar os status do jogador, caso erras 6 letras perderá, caso acerte a palavra vai ganhar
        if self.incorrectGuesses >= 6:
            return 'Você perdeu :('
        elif not '_' in self.gameString:
            return 'Você ganhou!!'
        else:
            return ''

    def guess(self, letter):
        if letter not in self.word or letter in self.gameString:  #vai adicionar as letras que foram erradas em uma pequena lista
            self.incorrectGuesses += 1
            self.incorrectLetters.append(letter)
            return 'Errado!'
        else:
            gameString = list(self.gameString)  #caso o jogador acerte a letra ele vai inserir a letra correta na posição correta na frase, utilizando o JOIN
            for i in range(len(self.word)):
                if self.word[i] == letter:
                    gameString[i] = letter
            self.gameString = ''.join(gameString)
            return 'Certo!'

    def changeTurn(self):  # metodo que vai retornar a vez do jogador
        if self.turn == 1:
            self.turn = 2
        else:
            self.turn = 1


def Main():
    global clientsAtivo
    global words

    ip = '127.0.0.1'
    port = 40000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #AF_INET é a família de endereços da Internet para IPv4. SOCK_STREAM é o tipo de socket para TCP, o protocolo que será usado para transportar mensagens na rede
    print('Servidor iniciando no ' + ip + '| Porta ' + str(port))

  
    try:
        s.bind((ip, port)) 
    except socket.error as e:
        print(str(e))
    s.listen(6)  



    while True:
        c, addr = s.accept()
        clientsAtivo += 1
        print("Uma conexão " + str(clientsAtivo) + " ativa de: " + str(addr))
        start_new_thread(clientThread, (c,))

def getGame(num_players_requested): #metodo que vai retornar a quantidade de jogadores na partida
    if num_players_requested == 2: #retornar 2 jogadores
        for game in games:
            if not game.completou:
                game.completou = True
                return (game, 2)
    if len(games) < 3: # vai deixar aleatório as palavras que estão em minha lista 
        word = words[random.randint(0, 14)]
        game = Game(word, num_players_requested)
        games.append(game)
        return (game, 1)
    else:
        return -1

def clientThread(c):  # metodo que vai permitir a entrada dos clientes ao jogo
    global clientsAtivo
                                                          
    twoPlayerSignal = c.recv(1024).decode('utf-8')

    if twoPlayerSignal == '2':
        x = getGame(2)
        if x == -1:
            send(c, 'Servidor está cheio')
        else:
            game, player = x
            send(c, 'Espere os outros jogadores...')

            while not game.completou:
                continue
            send(c, 'Jogo está iniciando')
            twoPlayerGame(c, player, game)

    else:
        x = getGame(1)   #retornar quando o servidor esta com 2 jogadores e um 3 quer entrar
        if x == -1:
            send(c, 'Servidor está cheio')
        else:
            game, player = x
            onePlayerGame(c, game)

def send(c, msg):
    packet = bytes([len(msg)]) + bytes(msg, 'utf8')
    c.send(packet)

def dados_do_game(c, game): #metodo que vai retornar os dados do jogo, letras já escolhidas , situação da palavra
    msgFlag = bytes([0])
    data = bytes(game.gameString + ''.join(game.incorrectLetters), 'utf8')
    gamePacket = msgFlag + bytes([len(game.word)]) + bytes([game.incorrectGuesses]) + data
    c.send(gamePacket)

def twoPlayerGame(c, jogador, game): # metodo que vai retornar o multiplayer
    global clientsAtivo                                                  

    while True:
        while game.turn != jogador:
            continue
        game.lock.acquire()

        status = game.getStatus() #informar os status do jogo, letras, situação...
        if status != '':
            dados_do_game(c, game)
            send(c, status)
            send(c, "Fim de jogo!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, 'Sua vez!')

        dados_do_game(c, game)

        rcvd = c.recv(1024) # indica a quantidade máxima de bytes recebidos por pacotes.
        letterGuessed = bytes([rcvd[1]]).decode('utf-8')

        send(c, game.guess(letterGuessed))

        status = game.getStatus() #informar os status do jogo, letras, situação...
        if len(status) > 0:
            dados_do_game(c, game)
            send(c, status)
            send(c, "Fim de jogo!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, "Aguarde a sua vez...")
        game.changeTurn()
        game.lock.release()

    if game in games:
        games.remove(game)
    c.close()
    clientsAtivo -= 1


def onePlayerGame(c, game): #metodo que retorna o jogo de apenas 1 participante
    global clientsAtivo

    while True:
        dados_do_game(c, game)

        rcvd = c.recv(1024)
        letterGuessed = bytes([rcvd[1]]).decode('utf-8')

        send(c, game.guess(letterGuessed))

        status = game.getStatus() #informar os status do jogo, letras, situação...
        if len(status) > 0:
            dados_do_game(c, game)
            send(c, status)
            send(c, "Fim de jogo!")
            break
    games.remove(game)
    c.close()
    clientsAtivo -= 1



if __name__ == '__main__':
    Main()
