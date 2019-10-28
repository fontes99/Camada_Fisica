

#importe as bibliotecas
import suaBibSignal as sig
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import sys

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    print("Inicializando encoder")

    freqDeAmostragem = 44100
        
    signal = sig.signalMeu()

    print("Gerando Tons base")
    
    optList =['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'X', '#', 'A', 'B', 'C', 'D']
    NUM = None

    print("****** TABELA *******")
    print("*  1   2   3    A   *")
    print("*  4   5   6    B   *")
    print("*  7   8   9    C   *")
    print("*  X   0   #    D   *")
    print("*********************")

    
    while NUM not in optList:
        NUM = input('Selecione um valor da tabela: ')

    print("Gerando Tom referente ao símbolo : {}".format(NUM))
    
    tone,f1,f2 = signal.makeTone(NUM)

    #solta o som
    sd.play(tone, freqDeAmostragem)
  
    # Exibe gráficos
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(f1[0][0:400], f1[1][0:400],f2[0][0:400], f2[1][0:400])
    axs[0].set_xlabel('time')
    axs[0].set_ylabel('f1 and f2')
    axs[0].grid(True)

    axs[1].plot(f1[0][0:400], tone[0:400])
    axs[1].set_xlabel('time')
    axs[1].set_ylabel('Tone')
    axs[1].grid(True)

    fig.tight_layout()
    plt.show()
    # aguarda fim do audio
    sd.wait()

if __name__ == "__main__":
    main()
