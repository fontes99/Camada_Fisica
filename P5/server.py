#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enlace import *
import time

class Server():

    def __init__(self):
      self.rxBuffer = None
      self.locEOP = None
      self.img = None
      print("Waiting Instructions")

    def organizeFile(self,EOP,stuffed):
      ####################
      # Ajeitando Imagem #
      ####################
      pBuffer = True
      while pBuffer:
          s01 = self.img.find(stuffed)
          if s01 == "-1":
              pBuffer = False
          else:
              imgfinal = self.img.replace(stuffed,EOP)
              pBuffer = False
      return imgfinal, len(imgfinal)
      #*********************************#

    def achaEOP(self,rxBuffer,EOP):
      self.locEOP = rxBuffer.find(EOP)
      #############
      # EOP ERROR #
      #############
      if self.locEOP==-1:
        resposta = bytes({0x00})
        return resposta
      elif self.locEOP!=len(rxBuffer)-4:
        resposta = bytes({0x01})
        return resposta
      else:
        resposta = bytes({0x02})
        if self.img == None:
          self.img = rxBuffer[:self.locEOP]
        else:
          self.img = self.img + rxBuffer[:self.locEOP]
        return resposta
      #*********************************#

    
    def fileType(self,tipo):
      if tipo== 0:
        return "png"
      if tipo== 1:
        return "jpg"
      if tipo== 2:
        return "jpeg"

    def verifiError(self,Bytes):
      if Bytes==-1:
        return True
      return False

'''    
========================#=======================#=========================

NUMERO DE IDENTIFICAÇÃO: 21

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