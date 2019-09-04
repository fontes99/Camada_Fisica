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

    print('\n Comprimento real da lista: ', len(send_list))

    print('\n Quant de packs: ', qPck, '\n')

    a = 0

    t0 = time.time()

    while a < qPck:

        # Envio pack por pack
        com.sendData(send_list[a])
        print(send_list[a])

        # Atualiza dados da transmissão
        txSize = com.tx.getStatus()
        print ("Transmitido {}/{} packs".format(a+1, qPck))

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

        print("*********************************************")
        print('            PACOTE {} DE {}                '.format(a+1, qPck))
        print("*********************************************")

        if compTamanho == 0:
            print("---------------------------------------------")
            print("[ERRO] Tamanho recebido diferente do enviado")

        elif compTamanho == 1:
            print("---------------------------------------------")
            print("Nenhum erro encontrado no payload")


        if erroEoP == 0:
            print("---------------------------------------------")
            print("EOP não Encontrado...")
            print("---------------------------------------------")
        
        elif erroEoP == 1:
            print("---------------------------------------------")
            print("EOP encontrado em um local errado...")
            print("---------------------------------------------")
            
        elif erroEoP == 2:
            print("---------------------------------------------")
            print("Nenhum erro encontrado no EoP")
        

        if erroEoP == 2 and compTamanho == 1:
            a += 1
        
        print("\n ----- CONCLUIDO ----- \n")

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

    ####################
    #  Loop Ocioso #
    ####################
    while ocioso:
        while(com.tx.getIsBussy()):
            pass
        QPackTotal = com.rx.getNData(2)
        QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
        QPackAtual = com.rx.getNData(2)
        QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little') + 1
        tamanho = com.rx.getNData(4)
        tip = com.rx.getNData(1)
        stuffedQuant = com.rx.getNData(1)
        resposta_tamanho = com.rx.getNData(1)
        resposta_EOP = com.rx.getNData(1)
        m1 = com.rx.getNData(1)
        m1INT = int.from_bytes(m1, byteorder='little')
        EOP_recebido = com.rx.getNData(4)
        ######################################################
        #  Recebendo mensagem para deixar de ser ocioso--M1  #
        ######################################################
        if EOP_recebido == EOP:
            if m1INT == 1:
                ocioso = False
        time.sleep(0.1)

    print("-------------------------")
    print("PEGUEI AS INFORMAÇÕES DO HEAD")

    ##############################################
    #  Mandando mensagem de servidor pronto--M2  #
    ##############################################
    
    send = QPackTotal+QPackAtual+envio+tip+stuffedQuant+resposta_tamanho+resposta_EOP+m2+EOP
    com.sendData(send)

    print("START")

    while QPackAtualINT<=QPackTotalINT:
        while(com.tx.getIsBussy()):
            pass

        timer_1 = time.time()
        timer_2 = time.time()

        QPackTotal = com.rx.getNData(2)
        QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
        QPackAtual = com.rx.getNData(2)
        QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little') + 1
        tamanho = com.rx.getNData(4)
        tip = com.rx.getNData(1)
        stuffedQuant = com.rx.getNData(1)
        resposta_tamanho = com.rx.getNData(1)
        resposta_EOP = com.rx.getNData(1)
        m3 = com.rx.getNData(1)
        m3INT = int.from_bytes(m3, byteorder='little')
        tamanhoPack = int.from_bytes(tamanho,byteorder="little")
        rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))

        # ##############################################
        # #  Pega as informações conhecendo o tamanho! #
        # ##############################################
        # if QPackAtualINT==QPackTotalINT:
        #     tamanhoPack = int.from_bytes(tamanho,byteorder="little")%128
        #     rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))
        # else:
        #     tamanhoPack = 128
        #     rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))


        if m3INT!=3:
            if timer_2>20:
                ocioso = True
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m5+EOP
                com.sendData(send)
                com.disable()
                print(":-(")
            if timer_1>2:
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m4+EOP
                com.sendData(send)
                timer_1 = (time.time - timer_1)
        else:
            ###############################################################################
            # Pegando o Buffer e construindo as variaveis do Head apartir do segundo Pack #
            ###############################################################################
            print("Quant Total: ", int.from_bytes(QPackTotal,byteorder="little"))
            print("Quant Atual: ", int.from_bytes(QPackAtual,byteorder="little"))

            
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

            print(resposta_tamanho, "+", resposta_EOP)
            ##################
            #    RESPOSTA    #
            ##################
            if resposta_tamanho == bytes({0x01}) and resposta_EOP == bytes({0x02}):
                send = QPackTotal+QPackAtual+envio+tip+stuffedQuant+resposta_tamanho+resposta_EOP+m4+EOP
                com.sendData(send)
                QPackAtualINT += 1
            else:
                send = QPackTotal+QPackAtual+envio+tip+stuffedQuant+resposta_tamanho+resposta_EOP+m6+EOP
                com.sendData(send)
        


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
