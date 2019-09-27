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
        rxT2 = com.rx.getNData(16)

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
            rxHead = com.rx.getNData(16)

            if rxHead == -1:
                timeout += 2
                print('\nRemandando pacote {}...\n'.format(a+1))
                continue

            rxLen = int.from_bytes(rxHead[6:10], byteorder='little')

            tip = rxHead[0]
            pacAtual = int.from_bytes(rxHead[4:6], byteorder='little')

            if tip == 5:
                print("---------------------------------------------")
                print("         [ERRO] TIMEOUT DE EXECUÇÃO          ")
                print("---------------------------------------------")
                sys.exit()

            if tip == 6:
                print("\n [ERRO] Pacote {} mal enviado. Transferindo novamente...\n". format(a+1))  
                continue

            if tip == 7:
                print("\n [ERRO][CRC] Pacote {} com alteração de dados. Transferindo novamente...\n". format(a+1))  
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



###############################################################################################################################################################
###############################################################################################################################################################
###############################################################################################################################################################



elif typ == "1":

    A=bytes(bytearray())
    A = bytes("CRRT", 'utf-8')
    print ("Aguardando informações...")
    server = Server()
    ocioso = True

    #############################
    #  Definindo EOP + Stuffed  #
    #############################
    EOP = bytes({0xF0}) + bytes({0xF1}) + bytes({0xF2}) + bytes({0xF3})
    stuffed = bytes({0x00}) + bytes({0xF0}) + bytes({0x00}) + bytes({0xF1}) + bytes({0x00}) + bytes({0xF2}) + bytes({0x00}) + bytes({0xF3})


    ###############################
    #  Respostas dadas ao Client  #
    ###############################
    m2INT = 2
    m2 = m2INT.to_bytes(1,byteorder='little')
    m4INT = 4
    m4 = m4INT.to_bytes(1,byteorder='little')
    m5INT = 5
    m5 = m5INT.to_bytes(1,byteorder='little')
    m6INT = 6
    m6 = m6INT.to_bytes(1,byteorder='little')
    ItsYou = 123
    ItsYouBytes = ItsYou.to_bytes(1,byteorder='little')

    ####################
    #  Loop Ocioso #
    ####################
    while ocioso:
        BODY = com.rx.getNData(16)
        if server.verifiError(BODY):
            continue
        m1 = BODY[0]
        ItsMe = BODY[1]
        QPackTotal = BODY[2:4]
        QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
        QPackAtual = BODY[4:6]
        QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little')
        tamanho = BODY[6:10]
        tip = BODY[10]
        tipBT = tip.to_bytes(1,byteorder='little')
        stuffedQuant = BODY[11]
        stuffedQuantBT = stuffedQuant.to_bytes(1, byteorder='little')
        EOP_recebido = BODY[12:16]
        print(m1)
        if m1 == 1:
            if ItsMe == 21:
                ocioso = False
        time.sleep(0.1)
        # resposta_tamanho = com.rx.getNData(1)
        # resposta_EOP = com.rx.getNData(1)
        ######################################################
        #  Recebendo mensagem para deixar de ser ocioso--M1  #
        ######################################################
    print("-------------------------")
    print("PEGUEI AS INFORMAÇÕES DO HEAD")

    ##############################################
    #  Mandando mensagem de servidor pronto--M2  #
    ##############################################
    
    send = m2+ItsYouBytes+QPackTotal+QPackAtual+tamanho+tipBT+stuffedQuantBT+EOP
    com.sendData(send)

    print("START")

    timer_2 = time.time()

    num_do_pacote = [0]

    ErroCond = False

    printProgressBar(0, QPackTotalINT, prefix = 'Transferindo pacotes {}/{}:'.format(QPackAtualINT, QPackTotalINT), suffix = 'Completo', length = 30)

    while QPackAtualINT<=QPackTotalINT:

        printProgressBar(QPackAtualINT, QPackTotalINT, prefix = 'Transferindo pacotes {}/{}:'.format(QPackAtualINT, QPackTotalINT), suffix = 'Completo', length = 30)

        HEAD = com.rx.getNData(12)

        #############################
        #  Verifica se tirou o fio  #
        #############################
        if server.verifiError(HEAD):
            time_now = time.time()
            time_out = time_now - timer_2
            if time_out>=20:
                ocioso = True
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m5+EOP
                com.sendData(send)
                com.disable()
                print("\n:-(\n")
                ErroCond = True
                break
            else:

                send = m4+ItsYouBytes+QPackTotal+QPackAtual+tamanho+tipBT+stuffedQuantBT+EOP
                com.sendData(send)
                continue


        m3 = HEAD[0]
        m3BT = m3.to_bytes(1, byteorder='little')
        ItsYou = HEAD[1]
        QPackTotal = HEAD[2:4]
        QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
        QPackAtual = HEAD[4:6]
        QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little')+1
        tamanho = HEAD[6:10]
        tip = HEAD[10]
        tipBT = tip.to_bytes(1, byteorder='little')
        stuffedQuant = HEAD[11]
        stuffedQuantBT = stuffedQuant.to_bytes(1, byteorder='little')
        # resposta_tamanho = com.rx.getNData(1)
        # resposta_EOP = com.rx.getNData(1)
        
        # rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))

        ##############################################
        #  Pega as informações conhecendo o tamanho! #
        ##############################################
        if QPackAtualINT==QPackTotalINT:
            tamanhoPack = int.from_bytes(tamanho,byteorder="little")%128
            rxBuffer = com.rx.getNData(tamanhoPack+len(EOP))
            if server.verifiError(rxBuffer):
                continue
        else:
            tamanhoPack = 128
            rxBuffer = com.rx.getNData(tamanhoPack+len(EOP))
            if server.verifiError(rxBuffer):
                continue


        if server.verifiError(rxBuffer):
            print("Erro")
            if timer_2>=20:
                ocioso = True
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m5+EOP
                com.sendData(send)
                com.disable()
                print(":-(")
                ErroCond = True
                break
            else:

                send = m4+ItsYouBytes+QPackTotal+QPackAtual+tamanho+tipBT+stuffedQuantBT+EOP
                com.sendData(send)
                continue	

        if QPackAtualINT == num_do_pacote[-1]+1:
            num_do_pacote.append(QPackAtualINT)
            timer_2=time.time()
            ###############################################################################
            # Pegando o Buffer e construindo as variaveis do Head apartir do segundo Pack #
            ###############################################################################
            
            #####################################
            #  Quantidade que realmente chegou  #
            #####################################
            tamanhoRecebido = len(rxBuffer)-4
            envio = tamanhoRecebido.to_bytes(4, byteorder='little')

            ##################
            #  Verifica EOP  #
            ##################
            resposta_EOP = server.achaEOP(rxBuffer,EOP)

            #############################
            #  Verifica Tamanho Imagem  #
            #############################
            if tamanhoRecebido!=tamanhoPack:
                resposta_tamanho = bytes({0x00})
            else:
                resposta_tamanho = bytes({0x01})

            ##################
            #    RESPOSTA    #
            ##################
            if resposta_tamanho == bytes({0x01}) and resposta_EOP == bytes({0x02}):
                send = m4+ItsYouBytes+QPackTotal+QPackAtual+envio+tipBT+stuffedQuantBT+EOP
                com.sendData(send)
                QPackAtualINT += 1
            else:
                send = m6+ItsYouBytes+QPackTotal+QPackAtual+envio+tipBT+stuffedQuantBT+EOP
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


    

