#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enlace import *
import time

class Server():

    def __init__(self):
      self.rxBuffer = None
      self.locEOP = None
      self.img = None
      self.ItsYouBytes = (123).to_bytes(1, byteorder='little')
      self.ItsMe = 21

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

    def fatiaHeader(self, header):

        tipM = header[0]

        ItsMe = header[1]

        QPackTotal = header[2:4]

        QPackAtual = header[4:6]

        tamanho = header[6:10]

        tip = header[10]

        stuffedQuant = header[11]

        CRC = header[12:14]

        return tipM, ItsMe, QPackTotal, QPackAtual, tamanho, tip, stuffedQuant, CRC

    def convertINTheader(self, header):

      tipM, ItsMe, QPackTotal, QPackAtual, tamanho, tip, stuffedQuant, CRC = self.fatiaHeader(header)

      tipMINT = int.from_bytes(tipM, byteorder='little')

      ItsMeINT = int.from_bytes(ItsMe, byteorder='little')

      QPackTotalINT = int.from_bytes(QPackTotal, byteorder='little')

      QPackAtualINT = int.from_bytes(QPackAtual, byteorder='little')

      tamanhoINT = int.from_bytes(tamanho, byteorder='little')

      tipINT = int.from_bytes(tip, byteorder='little')

      stuffedQuantINT = int.from_bytes(stuffedQuant, byteorder='little')

      CRCINT = int.from_bytes(CRC, byteorder='little')

      return tipMINT, ItsMeINT, QPackTotalINT, QPackAtualINT, tamanhoINT, tipINT, stuffedQuantINT, CRCINT


    def makeM2(self, header):

      header[0:1] = (2).to_bytes(1, byteorder='little')

      return header

    def makeM4(self, header):

      header[0:1] = (4).to_bytes(1, byteorder='little')

      return header 

    def makeM5(self, header):

      header[0:1] = (5).to_bytes(1, byteorder='little')

      return header

    def makeM6(self, header):

      header[0:1] = (6).to_bytes(1, byteorder='little')

      return header      



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

PROTOCOLO HEADER (14 bytes): 0'0'00'00'0000'0'0'00
Tipo (1 byte) + 
Destinatário (1 byte) +
Num de Pacotes (2 bytes) + 
Pacote atual (2 bytes) + 
Tamanho da imagem (4 bytes) + 
extenção da imagem (1 byte) + 
Quantidade de stuffeds q foram feitos (1 byte) +
CRC (2 bytes)

DICIONARIO DE EXTENÇÃO:
.png = b'\0x00'
.jpg = b'\0x01'
.jpeg = b'\0x02'

========================#=======================#=========================
'''