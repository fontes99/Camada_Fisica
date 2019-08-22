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
        
        head = img_size + img_typ + quantStuff + bytes({0x00}) + resposta

        return head
    

    def attEoP(self):

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
        
        self.quantStuff = len(stuffedIdx)

        send = payload + byteEoP

        return send


    def Organize(self):

        EoP = self.attEoP()

        send = self.makeHeader() + EoP

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
# Tamanho da imagem (4 bytes) + extenção da imagem (1 byte) + Quantidade de stuffeds q forem feitos (1 byte) + checagem do tamanho (1 byte) + resposta (1 byte)

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