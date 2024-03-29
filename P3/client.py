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
        self.head = None
        self.txLenStuff = None
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

    def getqPack(self):
        return int.from_bytes(self.qPck, byteorder='little')

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

        resposta_EoP = bytes({0x00})

        respPayload = bytes({0x00})
        
        head = img_size + img_typ + quantStuff + respPayload + resposta_EoP

        self.head = head

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

        self.makeHeader()
            
        qt = self.fatia()

        payload = payload + self.byteEoP

        b = 0
        p = qt 

        packs = []

        while b <= len(payload):

            payload[b:b] = self.qPck
            b+=2

            payload[b:b] = (qt-p).to_bytes(2, byteorder='little')
            p -= 1
            b += 2

            payload[b:b] = self.head
            b += 136

            # if b <= len(payload):
                
            payload[b:b] = self.byteEoP
            b += 4

            packs.append(payload[b-144: b])

            # else:
            #     break
        
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


    def Time(self,rxLen,END,STR):

        dt = END-STR
        taxa = int.from_bytes(self.qPck, byteorder='little')/dt

        print("Time: {}".format(dt))
        print("Taxa: {}".format(taxa)) 


    
#========================#=======================#=========================

# PROTOCOLO HEADER:
# Num de Pacotes (2 bytes) + Pacote atual + Tamanho da imagem (4 bytes) + extenção da imagem (1 byte) + Quantidade de stuffeds q forem feitos (1 byte) + checagem do tamanho (1 byte) + resposta (1 byte)

# RESPOSTA:
# 0x02 = tudo OK

# DICIONARIO DE EXTENÇÃO:
# .png = bytes({0x00})
# .jpg = bytes({0x01})
# .jpeg = bytes({0x02})

# DICIONARIO DE RESPOSTAS

# 0x00 = EOP não Encontrado
# 0x01 = EOP encontrado em um local errado...
# 0x02 = Sem erros

#========================#=======================#=========================