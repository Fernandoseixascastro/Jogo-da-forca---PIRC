import socket


def Main(): #comunicação cliente-servidor
    ip = '127.0.0.1'
    port = 40000
    print('Client ativo no ' + ip + '| Porta ' + str(port))

    s = socket.socket()
    s.connect((ip, port))
    print("*****------------------*****")
    print("****B E M  - V I N D O  ****")
    print("******      ao       *******")
    print("*******Jogo da Forca********")
    print("*****------------------*****")
    print("Modo multiplayer? (s/n)")
    print(">>", end='')
    msg = input().lower()

    while 1:
        if msg == 's' or msg == 'n':
            break
        msg = input('Escolha uma opção s (Sim) ou n (Não)')

    if msg == 's':
        twoPlayerSignal = '2'.encode('utf-8')
        s.send(twoPlayerSignal)
        Start(s)

    else:
        twoPlayerSignal = '0'.encode('utf-8')
        s.send(twoPlayerSignal)

        print("Um jogador iniciou uma partida")
        Start(s)

def recebe(socket):
    byte_value = int(socket.recv(1)[0])
    if byte_value == 0:
        x, y = socket.recv(2)
        return 0, socket.recv(int(x)), socket.recv(int(y))
    else:
        return 1, socket.recv(byte_value)

def Start(s):# metodo que vai iniciar o jogo
    while True:
        pkt = recebe(s)
        msgFlag = pkt[0]
        if msgFlag != 0:
            msg = pkt[1].decode('utf8')
            print(msg)
            if msg == 'Servidor lotado' or 'Game Over!' in msg:
                break
        else:
            gameString = pkt[1].decode('utf8')
            incorrectGuesses = pkt[2].decode('utf8')
            print(" ".join(list(gameString)))  #juntar as palavras ja utilizadas em uma lista
            print("Palpites incorreto: " + " ".join(incorrectGuesses) + "\n")#juntar as palavras ja erradas
            if "_" not in gameString or len(incorrectGuesses) >= 6:
                continue
            else:
                letraEscolhida = ''
                valid = False
                while not valid:
                    letraEscolhida = input('Letra escolhida: ').lower()
                    if letraEscolhida in incorrectGuesses or letraEscolhida in gameString:
                        print("Erro! A letra " + letraEscolhida.upper() + " Já foi escolhida antes, pense em outra opção.") #mostra se a letra ja foi escolhida antes
                    elif len(letraEscolhida) > 1 or not letraEscolhida.isalpha(): #impede que escolhe mais de uma letra ao mesmo tempo, ou uma frase também
                        print("Erro! Escolha apenas uma letra")
                    else:
                        valid = True
                msg = bytes([len(letraEscolhida)]) + bytes(letraEscolhida, 'utf8')
                s.send(msg)

    s.shutdown(socket.SHUT_RDWR) # chamar o descritor (shut_rdwr) que vai desabilitar as recepções e transmissões de dados
    s.close()


if __name__ == '__main__':
    Main()
