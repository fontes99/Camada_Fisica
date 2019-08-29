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
      print("LOC:",self.locEOP)
      print("BUFFER:",len(rxBuffer))
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
      if tipo== bytes({0x00}):
        return "png"
      if tipo==bytes({0x01}):
        return "jpg"
      if tipo==bytes({0x02}):
        return "jpeg"

    

#========================#=======================#=========================

# DICIONARIO DE EXTENÇÃO

# .png = bytes({0x00})
# .jpg = bytes({0x01})
# .jpeg = bytes({0x02})

#========================#=======================#=========================
      
#========================#=======================#=========================

# DICIONARIO DE RESPOSTAS

# 0x00 = EOP não Encontrado
# 0x01 = EOP encontrado em um local errado...
# 0x02 = Sem erros

#========================#=======================#=========================

      