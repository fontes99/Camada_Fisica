

#importe as bibliotecas
import suaBibSignal as sig
import numpy as np
import   sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
import sys

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    signal = sig.signalMeu()
    freqDeAmostragem = 44100
    filename = 'oi-meu-chapa.wav'
    # Extract data and sampling rate from file
    data, fs = sf.read(filename, dtype='float32')  
    time = len(data)/freqDeAmostragem
    # sd.play(data, fs)
    # status = sd.wait()  # Wait until file is done playing
    #######
    data = np.array(data)
    dataLeft = []
    for i in range(len(data)):
        dataLeft.append(data[i][0])

    dataLeft = np.array(dataLeft)
    div = max(abs(dataLeft))
    norm = dataLeft/max(abs(dataLeft))

    low_pass_normalized = signal.butter_lowpass_filter(norm,4000,freqDeAmostragem)
    sin = signal.generateSin(7000,1,time,freqDeAmostragem)
    signalAM = low_pass_normalized*sin[1]
    print(sin[1])
    sd.play(signalAM,fs)
    status = sd.wait()
    print(status)


    # # Exibe gráficos
    # fig, axs = plt.subplots(2, 1)
    # axs[0].plot(f1[0][0:400], f1[1][0:400],f2[0][0:400], f2[1][0:400])
    # axs[0].set_xlabel('time')
    # axs[0].set_ylabel('f1 and f2')
    # axs[0].grid(True)

    # axs[1].plot(f1[0][0:400], tone[0:400])
    # axs[1].set_xlabel('time')
    # axs[1].set_ylabel('Tone')
    # axs[1].grid(True)

    # fig.tight_layout()
    # plt.show()
    # # aguarda fim do audio
    # sd.wait()

if __name__ == "__main__":
    main()
