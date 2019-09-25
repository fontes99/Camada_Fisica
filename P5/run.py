    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

from client import *
from enlace import *
from server import *
import time

import subprocess
import sys

'''
    Serial com Port
        para saber a sua porta, execute no terminal:
        python -m serial.tools.list_ports

'''

def getPortAuto():

    port = subprocess.getoutput('python -m serial.tools.list_ports')
    r = port.split('\n')
    a = r[-1]
    b = a.strip()
    return b

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

serialName = getPortAuto()                      # Ubuntu 
# serialName = "/dev/tty.usbmodem1411"          # Mac    
# serialName = "COM11"                          # Windows

# Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
# Ativa comunicacao

if serialName == 'no ports found':
    print('Nenhuma porta encontrada...')

try:
    com.enable()
except:
    print('-------Impossível conectar-------')
    sys.exit()
    
# Log
print("-------------------------")
print("Comunicacao inicializada")
print("  porta : {}".format(com.fisica.name))
print("-------------------------")

typ = input("Escolha Client(0) ou Server(1): ")

while typ != "0" and typ != "1":
    print('Resposta inválida...')
    typ = input("Escolha Client(0) ou Server(1): ")

if typ == "0":

    client = Client()

    # Pede destinatario
    destino = int(input('Qual o destinatario? (0-255): '))

    if destino < 0 or destino > 255:

        while destino < 0 or destino > 255:

            print('Destinatario invalido...')
            destino = int(input('Qual o destinatario? (0-255): '))

    client.setDestino(destino)

    # Pede o Arquivo
    txBuffer, txLen, fileType = client.GetFileAndSize()

    # Organiza o arquivo para envio
    send_list = client.Organize()

    qPck = client.getqPack()

    print('\nQuant de packs: ', qPck, '\n')

    # Manda tipo 1 e espera tipo 2

    com.sendData(client.makeType1())

    tam = client.getLen()
    print('Requisitando conexção. Envio de {} bytes.'.format(tam))

    time.sleep(0.5)

    print("Esperando resposta...")

    resp2 = 0
    while resp2 <= 10:
        # Chama Resposta  
        rxT2 = com.rx.getNData(18)

        if rxT2 == -1 and resp2 <= 10:   
            resp2 += 1
            print('tentando denovo... tentativa {}/10\r'.format(resp2), end='\r')
        else:
            break

    # checa se chegou tipo 2 e faz o envio
    try:
        resp = rxT2[0]
    except:
        print("---------------------------------------------")
        print("         [ERRO] TIMEOUT DE EXECUÇÃO          ")
        print("---------------------------------------------")
        sys.exit()

    ver = rxT2[1] == client.getIdentificador()

    if resp == 2:

        print('\nConexão estabelecida!\nEnviando...\n')

        a = 0
        timeout = 0

        t0 = time.time()

        printProgressBar(0, qPck, prefix = 'Transferindo pacotes {}/{}:'.format(a+1, qPck), suffix = 'Completo', length = 30)

        while a < qPck and timeout <= 20:

            printProgressBar(a+1, qPck, prefix = 'Transferindo pacotes {}/{}:'.format(a+1, qPck), suffix = 'Completo', length = 30)
            
            # Envio pack por pack
            com.sendData(send_list[a])

            #========================================#
            #                Resposta                #
            #========================================#
            
            # Chama a Resposta  
            rxHead = com.rx.getNData(18)

            if rxHead == -1:
                timeout += 2
                print('\nRemandando pacote {}...\n'.format(a+1))
                continue

            rxLen = int.from_bytes(rxHead[6:10], byteorder='little')

            tip = rxHead[0]
            pacAtual = int.from_bytes(rxHead[4:6], byteorder='little')

            if tip == 6:
                print("\n [ERRO] Pacote {} mal enviado. Transferindo novamente...\n". format(a+1))  
                continue                

            if tip == 4:
                timeout = 0
                a = pacAtual+1

        t1 = time.time()

        print('')

        if timeout <= 20:
            #Printa a Eficiencia
            print("---------------------------------------------")
            print('TAXA DE TRANSFERÊNCIA:')
            client.Time(qPck,t1,t0)
            
            # print("---------------------------------------------")
            # print('TRUEPUT:')
            # client.Time(rxLen-12, t1, t0)
        
        if timeout > 20:
            print("---------------------------------------------")
            print("         [ERRO] TIMEOUT DE EXECUÇÃO          ")

        # Encerra comunicação
        print("---------------------------------------------")
        print("            Comunicação encerrada            ")
        print("---------------------------------------------")
        com.disable()



#------------------------------------------------------------------------------------------------------------------------------------------------------------------



elif typ == "1":

    print ("Aguardando informações...")
    server = Server()
    ocioso = True

    #  Definindo EOP + Stuffed
    EOP = b'\0xF0\0xF1\0xF2\0xF3'
    stuffed = b'\0xF0\0x00\0xF1\0x00\0xF2\0x00\0xF3'


    #  Respostas dadas ao Client  
    
    m2 = (2).to_bytes(1,byteorder='little')
    m4 = (4).to_bytes(1,byteorder='little')
    m5 = (5).to_bytes(1,byteorder='little')
    m6 = (6).to_bytes(1,byteorder='little')

    ItsYou = 123
    ItsYouBytes = ItsYou.to_bytes(1,byteorder='little')

    ####################
    #    Loop Ocioso   #
    ####################

    ocioso = True

    while ocioso:

        BODY = com.rx.getNData(18)

        print(BODY)

        if server.verifiError(BODY):
            continue
        
        tipM, ItsMe, QPackTotal, QPackAtual, tamanho, tip, stuffedQuant, CRC = server.fatiaHeader(BODY)

        tipMINT, ItsMeINT, QPackTotalINT, QPackAtualINT, tamanhoINT, tipINT, stuffedQuantINT, CRCINT = server.convertINTheader(BODY)

        if tipMINT == 1 and ItsMeINT == 21:
            ocioso = False

        time.sleep(0.1)

    print("-------------------------")
    print("PEGUEI AS INFORMAÇÕES DO HEAD")

    ##############################################
    #  Mandando mensagem de servidor pronto--M2  #
    ##############################################
    
    tip2 = server.makeM2(BODY)

    com.sendData(tip2)

    print("START")

    timer_2 = time.time()

    num_do_pacote = [0]

    ErroCond = False

    printProgressBar(0, QPackTotalINT, prefix = 'Transferindo pacotes {}/{}:'.format(QPackAtualINT, QPackTotalINT), suffix = 'Completo', length = 30)

    while QPackAtualINT<=QPackTotalINT:

        printProgressBar(QPackAtualINT, QPackTotalINT, prefix = 'Transferindo pacotes {}/{}:'.format(QPackAtualINT, QPackTotalINT), suffix = 'Completo', length = 30)

        HEAD = com.rx.getNData(14)
        
        tipM, ItsMe, QPackTotal, QPackAtual, tamanho, tip, stuffedQuant, CRC = server.fatiaHeader(HEAD)

        tipMINT, ItsMeINT, QPackTotalINT, QPackAtualINT, tamanhoINT, tipINT, stuffedQuantINT, CRCINT = server.convertINTheader(HEAD)

        #############################
        #  Verifica se tirou o fio  #
        #############################

        if server.verifiError(HEAD):
            time_now = time.time()
            time_out = time_now - timer_2

            if time_out>=20:

                send = server.makeM5(HEAD)

                com.sendData(send)
                com.disable()
                print("\nTIMEOUT\n")
                ErroCond = True
                break

            else:
                send = server.makeM4(HEAD)
                com.sendData(send)
                continue

        ##############################################
        #  Pega as informações conhecendo o tamanho! #
        ##############################################

        if QPackAtualINT==QPackTotalINT:

            tamanhoPayload = tamanhoINT%128
            rxBuffer = com.rx.getNData(tamanhoPayload+len(EOP))

            if server.verifiError(rxBuffer):
                continue

        else:

            tamanhoPayload = 128
            rxBuffer = com.rx.getNData(tamanhoPayload+len(EOP))
            if server.verifiError(rxBuffer):
                continue

        if server.verifiError(rxBuffer):
            print("Erro")
            if timer_2>=20:

                send = server.makeM5(HEAD)

                com.sendData(send)
                com.disable()
                print("\nTIMEOUT\n")
                ErroCond = True
                break
    
            else:
                send = server.makeM4(HEAD)
                com.sendData(send)
                continue	

        if QPackAtualINT == num_do_pacote[-1]+1:

            num_do_pacote.append(QPackAtualINT)

            timer_2=time.time()

            # Pegando o Buffer e construindo as variaveis do Head apartir do segundo Pack
            
            #  Quantidade que realmente chegou

            tamanhoRecebido = len(rxBuffer)-4

            #  Verifica EOP  #
            resposta_EOP = server.achaEOP(rxBuffer,EOP)

            #  Verifica Tamanho Imagem  #
            if tamanhoRecebido != tamanhoPayload:
                resposta_tamanho = b'\0x00'
            else:
                resposta_tamanho = b'\0x01'

            ##################
            #    RESPOSTA    #
            ##################

            if resposta_tamanho == b'\0x01' and resposta_EOP == b'\0x02':

                send = server.makeM4(HEAD)
                com.sendData(send)
                QPackAtualINT += 1

            else:
                send = server.makeM6(HEAD)
                com.sendData(send)
        
    print('')
    if ErroCond:
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    else:
        print("-------------------------")
        print("CHECKPOINT")

        image, imageLen = server.organizeFile(EOP,stuffed)

        print("-------------------------")
        print("ORGANIZEI")

        tipo = server.fileType(tip)
        print(tipo)
        print(len(image))

	    #####################
	    #  Salva o Arquivo  #
	    #####################
        with open("SaveImage"+"."+tipo,'wb+') as saved:
             saved.write(image)

        print("-------------------------")
        print("SALVEI")

	    #########################
	    #  Encerra comunicação  #
	    #########################
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()


    

