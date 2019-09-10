    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

from client import *
from enlace import *
from server import *
import time

'''
    Serial Com Port
        para saber a sua porta, execute no terminal :
        python -m serial.tools.list_ports

'''

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

    # Pede destinatario
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
    
    # Recebe Resposta  
    rxT2 = com.rx.getNData(16)

    # checa se chegou tipo 2 e faz o envio
    resp = rxT2[0]

    ver = rxT2[1] == client.getIdentificador()

    if resp == 2:

        t0 = time.time()
        a = 0
        timeout = 0

        client.printProgressBar(0, qPck, prefix = 'Transferindo pacotes {}/{}:'.format(a+1, qPck), suffix = 'Completo', length = 30)

        while a < qPck and timeout <= 20:

            client.printProgressBar(a+1, qPck, prefix = 'Transferindo pacotes {}/{}:'.format(a+1, qPck), suffix = 'Completo', length = 30)
            
            # Envio pack por pack
            com.sendData(send_list[a])

            # Atualiza dados da transmissão
            txSize = com.tx.getStatus()

            #========================================#
            #                Resposta                #
            #========================================#
            
            # Chama a Resposta  
            rxHead = com.rx.getNData(16)

            if rxHead == -1:
                timeout += 2
                continue

            rxLen = int.from_bytes(rxHead[6:10], byteorder='little')

            tip = rxHead[0]

            if tip == 6:
                print("\n [ERRO] Pacote {} mal enviado". format(a))                  

            if tip == 4:
                timeout = 0
                a += 1

        t1 = time.time()

        if timeout <= 20:
            #Printa a Eficiencia
            print("---------------------------------------------")
            print('TAXA DE TRANSFERÊNCIA:')
            client.Time(rxLen,t1,t0)
            
            print("---------------------------------------------")
            print('TRUEPUT:')
            client.Time(rxLen-12, t1, t0)
        
        if timeout > 20:

            print("---------------------------------------------")
            print("         [ERRO] TIMEOUT DE CONEXÃO           ")
            print("---------------------------------------------")

        # Encerra comunicação
        print("---------------------------------------------")
        print("            Comunicação encerrada            ")
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
    ItsYou = 123
    ItsYouBytes = ItsYou.to_bytes(1,byteorder='little')

    ####################
    #  Loop Ocioso #
    ####################
    while ocioso:
        while(com.tx.getIsBussy()):
            pass
        BODY = com.rx.getNData(16)
        if server.verifiError(BODY):
            continue
        m1 = BODY[0]
        m1INT = int.from_bytes(m1, byteorder='little')
        ItsMe = BODY[1]
        ItsMeInt = int.from_bytes(ItsMe, byteorder='little')
        QPackTotal = BODY[2:3]
        QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
        QPackAtual = BODY[4:5]
        QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little') + 1
        tamanho = BODY[6:9]
        tip = BODY[10]
        stuffedQuant = BODY[11]
        EOP_recebido = BODY[12:15]
        print(m1INT)
        if m1INT == 1:
            if ItsMeInt == 21:
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
    
    send = m2+ItsYouBytes+QPackTotal+QPackAtual+tamanho+tip+stuffedQuant+EOP
    com.sendData(send)

    print("START")

    timer_2 = time.time()

    while QPackAtualINT<=QPackTotalINT:
        while(com.tx.getIsBussy()):
            pass
        
        HEAD = com.rx.getNData(16)
        if server.verifiError(HEAD):
            if timer_2>20:
                ocioso = True
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m5+EOP
                com.sendData(send)
                com.disable()
                print(":-(")
            else:
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m4+EOP
                com.sendData(send)
        m3 = HEAD[0]
        m3INT = int.from_bytes(m1, byteorder='little')
        ItsYou = HEAD[1]
        QPackTotal = HEAD[2:3]
        QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')
        QPackAtual = HEAD[4:5]
        QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little') + 1
        tamanho = HEAD[6:9]
        tip = HEAD[10]
        stuffedQuant = HEAD[11]
        # resposta_tamanho = com.rx.getNData(1)
        # resposta_EOP = com.rx.getNData(1)
        
        # rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))

        ##############################################
        #  Pega as informações conhecendo o tamanho! #
        ##############################################
        if QPackAtualINT==QPackTotalINT:
            tamanhoPack = int.from_bytes(tamanho,byteorder="little")%128
            rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))
        else:
            tamanhoPack = 128
            rxBuffer, nRx = com.getData(tamanhoPack+len(EOP))

        if server.verifiError(rxBuffer):
            if timer_2>20:
                ocioso = True
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m5+EOP
                com.sendData(send)
                com.disable()
                print(":-(")
            else:
                cont = 0
                
                stuff = cont.to_bytes(12,byteorder='little')

                send = stuff+m4+EOP
                com.sendData(send)

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
                send = m4+ItsYouBytes+QPackTotal+QPackAtual+envio+tip+stuffedQuant+EOP
                com.sendData(send)
                QPackAtualINT += 1
            else:
                send = m6+ItsYouBytes+QPackTotal+QPackAtual+envio+tip+stuffedQuant+EOP
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


    

