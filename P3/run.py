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
    send = client.Organize()

    t0 = time.time()
    # Envio
    com.sendData(send)

    # Atualiza dados da transmissão
    txSize = com.tx.getStatus()
    print ("Transmitido       {} bytes ".format(txSize))

    #========================================#
    #                Resposta                #
    #========================================#

    # Espera as infos
    while(com.tx.getIsBussy()):
        pass

    t1 = time.time()

    #Recebe Resposta  
    rxHead = com.rx.getNData(8)

    rxLen = int.from_bytes(rxHead[0:4], byteorder='little')

    compTamanho = rxHead[-2]

    erroEoP = rxHead[-1]


    if compTamanho == 0:
        print("---------------------------------------------")
        print("[ERRO] Tamanho recebido diferente do enviado")

    elif compTamanho == 1:
        print("---------------------------------------------")
        print("Nenhum erro encontrado no tamanho da IMG")


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
    print("---------------------------------------------")
    com.disable()



#------------------------------------------------------------------------------------------------------------------------------------------------------------------



elif typ == "1":

    A=bytes(bytearray())
    A = bytes("CRRT", 'utf-8')
    print ("Aguardando informações...")
    print (A)
    server = Server()

    while(com.tx.getIsBussy()):
        pass

    tamanho = com.rx.getNData(4)
    tip = com.rx.getNData(1)
    stuffedQuant = com.rx.getNData(1)
    resposta_tamanho = com.rx.getNData(1)
    resposta_EOP = com.rx.getNData(1)
    EOP = bytes({0xF0}) + bytes({0xF1}) + bytes({0xF2}) + bytes({0xF3})
    stuffed = bytes({0x00}) + bytes({0xF0}) + bytes({0x00}) + bytes({0xF1}) + bytes({0x00}) + bytes({0xF2}) + bytes({0x00}) + bytes({0xF3})

    print("-------------------------")
    print("PEGUEI AS INFORMAÇÕES")

    #Tamanho do arquivo + StuffedLen
    rxLen = int.from_bytes(tamanho,byteorder='little') + int.from_bytes(stuffedQuant,byteorder='little')

    #Pega as informações conhecendo o tamanho!  rxBuffer = rxBuffer[0: s01:] + rxBuffer[s01 + 1::]   
    rxBuffer, nRx = com.getData(rxLen+len(EOP))

    print("-------------------------")
    print("CHECKPOINT")

    image, imageLen, resposta_EOP = server.organizeFile(rxBuffer,EOP,stuffed)

    print("-------------------------")
    print("ORGANIZEI")

    tipo = server.fileType(tip)

    #Salva o Arquivo
    with open("SaveImage"+"."+tipo,'wb+') as saved:
        saved.write(image)

    print("-------------------------")
    print("SALVEI")

    #Quantidade que realmente chegou
    envio = imageLen.to_bytes(4, byteorder='little')

    #Verifica Tamanho Imagem
    if imageLen!=rxLen:
        resposta_tamanho = bytes({0x00})
    else:
        resposta_tamanho = bytes({0x01})
    head = envio+tip+stuffedQuant+resposta_tamanho+resposta_EOP

    #Retorna Head
    com.sendData(head)

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

