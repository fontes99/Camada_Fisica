#!/usr/bin/python3
"""Show a text-mode spectrogram using live microphone data."""

# Importe todas as bibliotecas

import suaBibSignal as sig
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from peakutils.plot import plot as pplot
import time  # This is required to include time module.
import peakutils

# funcao para transformas intensidade acustica em dB


def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():

    # declare um objeto da classe da sua biblioteca de apoio (cedida)
    signal = sig.signalMeu()
  
    # declare uma variavel com a frequencia de amostragem, sendo 44100
    freqDeAmostragem = 44100

    # freq de porte
    ch = 7000
  
    # voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:

    sd.default.samplerate = freqDeAmostragem  # taxa de amostragem
   
    sd.default.channels = 2  # voce pode ter que alterar isso dependendo da sua placa
   
    duration = 5  # tempo em segundos que ira aquisitar o sinal acustico captado pelo mic

    # faca um printo na tela dizendo que a captacao comecará em n segundos. e entao
    # use um time.sleep para a espera
    for i in range(6):
        print('A captação começará em ', 5-i, ' segundos.         \r', end = "\r")
        time.sleep(1)
    
    print('')
    
    # faca um print informando que a gravacao foi inicializada
    print("A gravação foi inicializada.")

    start = time.time()
   
    # calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes)
    numAmostras = duration*freqDeAmostragem
    audio = sd.rec(int(numAmostras), freqDeAmostragem, channels=1)
   
    sd.wait()
    end = time.time()
    print("...     FIM")
    
    dt= end - start
    
    print("Durou: ",dt," segundos")

    portadora = signal.generateSin(ch,  1, duration, freqDeAmostragem)



    # analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ..
    # print("Audio recebido: ",audio)

    audio_graf = []
    for i in range(len(audio)):
        audio_graf.append(audio[i][0])

    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    t = np.linspace(0.0, dt, len(audio_graf))

    recebido = portadora[1] * np.array(audio_graf)
    recebidoFiltradao = signal.butter_lowpass_filter(recebido, ch/10, freqDeAmostragem)
    
    sd.play(recebidoFiltradao)

    xf,yf = signal.calcFFT(audio_graf,freqDeAmostragem)

    fig, axs = plt.subplots(2, 1)
    
    axs[0].plot(t, recebidoFiltradao)
    axs[0].set_xlabel('time')
    axs[0].set_ylabel('Tone Recived')
    axs[0].grid(True)

    index = peakutils.indexes(yf, thres=0.2, min_dist=30)
    pplot(xf, yf,index)
    axs[1].set_ylabel('Fourier/Peaks')
    axs[1].grid(True)

    fig.tight_layout()
    plt.show()

    # value = xf[index]
    # print(value)

    # printe os picos encontrados!

    # encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    # print a tecla.

    # Exibe gráficos
    

if __name__ == "__main__":
    main()
