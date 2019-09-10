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
        self.qPck = None
        self.txLenStuff = None
        self.destino = None

        self.identificador = (123).to_bytes(1, byteorder='little')

        self.byteEoP = bytes({0xF0}) + bytes({0xF1}) + bytes({0xF2}) + bytes({0xF3})

    def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
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

    def getLen(self):
        return self.txLen

    def setDestino(self, destino):
        self.destino = destino.to_bytes(1, byteorder='little')

    def getqPack(self):
        return int.from_bytes(self.qPck, byteorder='little')
    
    def getIdentificador(self):
        return self.identificador

    def GetFileAndSize(self):

        filename = filedialog.askopenfilename(initialdir = "/home/borg/Imagens/.",title="ESCOLHA UM ARQUIVO!", filetypes=(("imagens","*.jpg *.jpeg *.png"),("allfiles","*.*")))

        a = filename.split('.')

        fileType = a[-1]

        self.fileType = fileType

        with open(filename, 'rb') as foto:
            self.txBuffer = foto.read()
        
        self.txLen = len(self.txBuffer)

        return self.txBuffer, self.txLen, fileType

    def makeHeader(self, tipo, pckAtual=0):

        msg_size = self.txLen.to_bytes(4, byteorder='little')

        if  self.fileType.lower() == 'png':
            img_typ =  bytes({0x00})

        elif  self.fileType.lower() == 'jpg':
            img_typ =  bytes({0x01})

        elif  self.fileType.lower() == 'jpeg':
            img_typ =  bytes({0x02})
    
            
        quantStuff = self.quantStuff.to_bytes(1, byteorder='little')
        
        pacote_atual = pckAtual.to_bytes(2, byteorder='little')

        head = tipo.to_bytes(1, byteorder='little') + self.destino + self.qPck + pacote_atual + msg_size + img_typ + quantStuff

        return head

    def fatiamento(self):

        payload = bytearray(self.txBuffer)

        stuffedIdx = []

        a = 0
        
        while a <= (self.txLen - 3):

            if payload[a] == self.byteEoP[0] and payload[a+1] == self.byteEoP[1] and payload[a+2] == self.byteEoP[2] and payload[a+3] == self.byteEoP[3]:

                payload[a:a]     = bytes({0x00})
                payload[a+1:a+1] = bytes({0x00})
                payload[a+2:a+2] = bytes({0x00})
                payload[a+3:a+3] = bytes({0x00})
                
                stuffedIdx.append(a)

            a += 1
        
        self.quantStuff = len(stuffedIdx)
        
        self.txLenStuff = len(payload)
            
        qt = self.fatia()

        payload = payload + self.byteEoP

        b = 0
        p = qt 

        packs = []

        while b <= len(payload):

            payload[b:b] = self.makeHeader(3, (qt-p))
            p -= 1
            b += 140
                
            payload[b:b] = self.byteEoP
            b += 4

            packs.append(payload[b-144: b])
        
        packs.append(payload[b:])

        return packs

    def fatia(self):

        tamanho_do_payload = self.txLenStuff

        sobra = tamanho_do_payload%128

        a = tamanho_do_payload - sobra

        qPack = int(a/128) + 1

        self.qPck = (qPack).to_bytes(2, byteorder='little')

        return qPack


    def Organize(self):

        pack_list = self.fatiamento()

        # Transmite dado

        return pack_list


    def Time(self,pck,END,STR):

        dt = round(END-STR, 3)
        taxa = round(pck/dt, 3)

        print("Time: {} segundos".format(dt))
        print("Taxa: {} pacotes por segundo".format(taxa)) 
    
    def makeType1(self):
        
        head = self.makeHeader(1)

        send = head + self.byteEoP

        return send

        


'''    
========================#=======================#=========================

NUMERO DE IDENTIFICAÇÃO: 123

PROTOCOLO HEADER (12 bytes): 0'0'00'00'0000'0'0
Tipo (1 byte) + 
Destinatário (1 byte) +
Num de Pacotes (2 bytes) + 
Pacote atual (2 bytes) + 
Tamanho da imagem (4 bytes) + 
extenção da imagem (1 byte) + 
Quantidade de stuffeds q foram feitos (1 byte)

DICIONARIO DE EXTENÇÃO:
.png = bytes({0x00})
.jpg = bytes({0x01})
.jpeg = bytes({0x02})

========================#=======================#=========================
'''