#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enlace import *
from tkinter import filedialog,Tk
import time

class Server():

    def __init__(self):
      self.rxBuffer = None
      print("Waiting Instructions")

    def organizeFile(self,rxBuffer,EOP,stuffed):
      self.rxBuffer = rxBuffer
      locEOP = self.rxBuffer.find(EOP)
      ############
      if locEOP==-1:
        resposta = bytes({0x00})
        return rxBuffer,len(rxBuffer),resposta
      elif locEOP!=len(rxBuffer)-4:
        resposta = bytes({0x01})
        return rxBuffer,len(rxBuffer),resposta
      else:
        resposta = bytes({0x02})
        image = self.rxBuffer[:locEOP]
      #############
      pBuffer = True
      while pBuffer:
          s01 = image.find(stuffed)
          if s01 == "-1":
              pBuffer = False
          else:
              image = image.replace(stuffed,EOP)
              pBuffer = False
      return image, len(image),resposta
    
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

# 0xF1 = EOP não Encontrado
# 0xF2 = EOP encontrado em um local errado...
# 0xF3 = Sem erros

#========================#=======================#=========================