#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from client import *
from enlace import *
from server import *

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

def getPort():

    print('Qual porta esta usando?')
    port = int(input("Numero da porta: "))
    portF = ''

    if port==0:
        portF = "/dev/ttyACM0"

    if port==1:
        portF = "/dev/ttyACM1"

    if port==2:
        portF = "/dev/ttyACM2"

    return portF

serialName = getPort()                      # Ubuntu (variacao de)
# serialName = "/dev/tty.usbmodem1411"      # Mac    (variacao de)
# serialName = "COM11"                      # Windows(variacao de)

# Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
# Ativa comunicacao
com.enable()

# Log
print("-------------------------")
print("Comunicacao inicializada")
print("  porta : {}".format(com.fisica.name))
print("-------------------------")

typ = input("Escolha Client(0) ou Server(1): ")

if typ == "0":

    client = Client()

    # Pede o Arquivo
    txBuffer, txLen, fileType = client.GetFileAndSize()

    # Organiza o arquivo para envio
    send_list = client.Organize()

    qPck = client.getqPack()

    print('\nQuant de packs: ', qPck, '\n')

    a = 0

    t0 = time.time()

    client.printProgressBar(0, qPck, prefix = 'Transferindo pacotes {}/{}:'.format(a+1, qPck), suffix = 'Completo', length = 70)

    while a < qPck:

        client.printProgressBar(a + 1, qPck, prefix = 'Transferindo pacotes {}/{}:'.format(a+1, qPck), suffix = 'Completo', length = 70)

        # Envio pack por pack
        com.sendData(send_list[a])

        # Atualiza dados da transmissão
        txSize = com.tx.getStatus()

        #========================================#
        #                Resposta                #
        #========================================#

        # Espera as infos
        while(com.tx.getIsBussy()):
            pass
        

        #Recebe Resposta  
        rxHead = com.rx.getNData(16)

        rxLen = int.from_bytes(rxHead[0:4], byteorder='little')

        compTamanho = rxHead[-6]

        erroEoP = rxHead[-5]

        if compTamanho == 0:
            print("\n[ERRO] Tamanho recebido diferente do enviado no pacote {}". format(a))

        if erroEoP == 0:
            print("\n[ERRO] EOP não Encontrado no pacote {}". format(a))
        
        elif erroEoP == 1:
            print("\n[ERRO] EOP encontrado em um local errado no pacote {}". format(a))                    

        if erroEoP == 2 and compTamanho == 1:
            a += 1

    t1 = time.time()

    #Printa a Eficiencia
    print("---------------------------------------------")
    print('TAXA DE TRANSFERÊNCIA:')
    client.Time(rxLen,t1,t0)
    
    print("---------------------------------------------")
    print('TRUEPUT:')
    client.Time(rxLen-12, t1, t0)

    # Encerra comunicação
    print("---------------------------------------------")
    print("            Comunicação encerrada              ")
    # print(clien)
    print("---------------------------------------------")
    com.disable()



#------------------------------------------------------------------------------------------------------------------------------------------------------------------


elif typ == "1":

    A=bytes(bytearray())
    A = bytes("CRRT", 'utf-8')
    print ("Aguardando informações...")
    server = Server()

    ####################
    #  Loop de espera  #
    ####################
    while(com.tx.getIsBussy()):
        pass

    
    QPackTotal = com.rx.getNData(2)
    QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
    QPackAtual = com.rx.getNData(2)
    QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little')
    tamanho = com.rx.getNData(4)
    tip = com.rx.getNData(1)
    stuffedQuant = com.rx.getNData(1)
    resposta_tamanho = com.rx.getNData(1)
    resposta_EOP = com.rx.getNData(1)
    print("START")
    EOP = bytes({0xF0}) + bytes({0xF1}) + bytes({0xF2}) + bytes({0xF3})
    stuffed = bytes({0x00}) + bytes({0xF0}) + bytes({0x00}) + bytes({0xF1}) + bytes({0x00}) + bytes({0xF2}) + bytes({0x00}) + bytes({0xF3})

    print("-------------------------")
    print("PEGUEI AS INFORMAÇÕES DO HEAD")

    ##################################### 
    #  Tamanho do arquivo + StuffedLen  #
    #####################################
    # rxLen = int.from_bytes(tamanho,byteorder='little') + int.from_bytes(stuffedQuant,byteorder='little')

    while QPackAtualINT<QPackTotalINT:
        

        ########################################################
        # Pegando o Buffer e construindo as variaveis do Head  #
        ########################################################
        if QPackAtualINT>0:
            QPackTotal = com.rx.getNData(2)
            QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
            QPackAtual = com.rx.getNData(2)
            QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little')
            tamanho = com.rx.getNData(4)
            tip = com.rx.getNData(1)
            stuffedQuant = com.rx.getNData(1)
            resposta_tamanho = com.rx.getNData(1)
            resposta_EOP = com.rx.getNData(1)

        print("Quant Total: ", int.from_bytes(QPackTotal,byteorder="little"))
        print("Quant Atual: ", int.from_bytes(QPackAtual,byteorder="little")+1)
    
        ##############################################
        #  Pega as informações conhecendo o tamanho! #
        ##############################################

        if QPackAtualINT==QPackTotalINT-1:
            tamanhoPack = int.from_bytes(tamanho,byteorder="little")%128
            rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))
        else:
            tamanhoPack = 128
            rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))
        
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
        print()
        head = QPackTotal+QPackAtual+envio+tip+stuffedQuant+resposta_tamanho+resposta_EOP+EOP

        ##################
        #    RESPOSTA    #
        ##################
        com.sendData(head)

        print(resposta_tamanho, "+", resposta_EOP)
        if resposta_tamanho == bytes({0x01}) and resposta_EOP == bytes({0x02}):
            QPackAtualINT += 1


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

    # #####################################
    # #  Quantidade que realmente chegou  #
    # #####################################
    # envio = imageLen.to_bytes(4, byteorder='little')

    # #############################
    # #  Verifica Tamanho Imagem  #
    # #############################
    # if imageLen!=rxLen:
    #     resposta_tamanho = bytes({0x00})
    # else:
    #     resposta_tamanho = bytes({0x01})
    # head = QPackTotal+QPackAtual+envio+tip+stuffedQuant+resposta_tamanho+resposta_EOP

    # ##################
    # #  Retorna Head  #
    # ##################
    # com.sendData(head)

    #########################
    #  Encerra comunicação  #
    #########################
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()