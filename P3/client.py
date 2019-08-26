#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enlace import *
from tkinter import filedialog,Tk
import time

class Client():

    def __init__(self):
        self.txLen = None
        self.txBuffer = None
        self.type = None
        self.quantStuff = None
        self.sobra = None
        self.qPck = None
        self.head = None

        
    def GetFileAndSize(self):

        filename = filedialog.askopenfilename(initialdir = "/home/borg/Imagens/.",title="ESCOLHA UM ARQUIVO!", filetypes=(("imagens","*.jpg *.jpeg *.png"),("allfiles","*.*")))

        a = filename.split('.')

        fileType = a[-1]

        self.fileType = fileType

        with open(filename, 'rb') as foto:
            self.txBuffer = foto.read()
        
        self.txLen = len(self.txBuffer)

        return self.txBuffer, self.txLen, fileType


    def makeHeader(self):

        img_size = self.txLen.to_bytes(4, byteorder='little')


        if  self.fileType.lower() == 'png':
            img_typ =  bytes({0x00})

        elif  self.fileType.lower() == 'jpg':
            img_typ =  bytes({0x01})

        elif  self.fileType.lower() == 'jpeg':
            img_typ =  bytes({0x02})
    
            
        quantStuff = self.quantStuff.to_bytes(1, byteorder='little')

        resposta = bytes({0x00})

        resp1 = bytes({0x00})
        
        head = img_size + img_typ + quantStuff + bytes({0x00}) + resp1 + resposta

        self.head = head

        return head
    

    def fatiamento(self):

        byteEoP = bytes({0xF0}) + bytes({0xF1}) + bytes({0xF2}) + bytes({0xF3})

        payload = self.txBuffer

        stuffedIdx = []

        a = 0
        
        while a < self.txLen:

            if payload[a] == byteEoP[0] and payload[a+1] == byteEoP[1] and payload[a+2] == byteEoP[2] and payload[a+3] == byteEoP[3]:

                payload[a:a]     = bytes({0x00})
                payload[a+1:a+1] = bytes({0x00})
                payload[a+2:a+2] = bytes({0x00})
                payload[a+3:a+3] = bytes({0x00})
                
                stuffedIdx.append(a)

            a += 1
            
        s, qt = self.fatia()

        b = 0
        p = qt

        while b < payload:

            payload[b:b] = qt.to_bytes(2, byteorder='little') + (qt-p).to_bytes(2, byteorder='little')
            p -= 1
            b += 4

            payload[b:b] = self.head
            b += 136

            payload[b:b] = bytes({0xF0}) + bytes({0xF1}) + bytes({0xF2}) + bytes({0xF3})
            b += 4
        
        payload = payload + bytes({0xF0}) + bytes({0xF1}) + bytes({0xF2}) + bytes({0xF3})

        self.quantStuff = len(stuffedIdx)

        send = payload + byteEoP

        return send

    def fatia(self):

        tamanho_do_payload = self.txLen

        sobra = tamanho_do_payload%128

        qPack = (tamanho_do_payload - sobra)/128

        self.sobra = sobra.to_bytes(2, byteorder='little')

        self.qPck = (qPack + 1).to_bytes(2, byteorder='little')

        return sobra, qPack


    def Organize(self):

        head = self.makeHeader()

        send = self.fatiamento()

        # Transmite dado
        print("tentado transmitir .... {} bytes".format(self.txLen))

        return send


    def Time(self,rxLen,END,STR):

        dt = END-STR
        taxa = rxLen/dt

        print("Time: {}".format(dt))
        print("Taxa: {}".format(taxa)) 


    
#========================#=======================#=========================

# PROTOCOLO HEADER:
# Num de Pacotes (2 bytes) + Pacote atual + Tamanho da imagem (4 bytes) + extenção da imagem (1 byte) + Quantidade de stuffeds q forem feitos (1 byte) + checagem do tamanho (1 byte) + resposta (1 byte)

# RESPOSTA:
# 0XFF = tudo OK

# DICIONARIO DE EXTENÇÃO:
# .png = bytes({0x00})
# .jpg = bytes({0x01})
# .jpeg = bytes({0x02})

# DICIONARIO DE RESPOSTAS

# 0x00 = EOP não Encontrado
# 0x01 = EOP encontrado em um local errado...
# 0x02 = Sem erros

#========================#=======================#=========================