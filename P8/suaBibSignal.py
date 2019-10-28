
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window
import suaBibSignal as sig



class signalMeu:

    def __init__(self):
        self.init = 0

    def generateSin(self, freq, amplitude, time, fs):
        n = time*fs
        x = np.linspace(0.0, time, n)
        s = amplitude*np.sin(freq*x*2*np.pi)
        return (x, s)

    def calcFFT(self, signal, fs):
        # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
        N  = len(signal)
        W = window.hamming(N)
        T  = 1/fs
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        yf = fft(signal*W)
        return(xf, np.abs(yf[0:N//2]))

    def plotFFT(self, signal, fs):
        x,y = self.calcFFT(signal, fs)
        plt.figure()
        plt.plot(x, np.abs(y))
        plt.title('Fourier')
    
    def makeTone(self, input):

        freqDeAmostragem = 44100

        duration = 5

        gainX  = 0.2
        gainY  = 0.2

        s1209 = self.generateSin(1209, gainY, duration,freqDeAmostragem)
        s1336 = self.generateSin(1336, gainY, duration,freqDeAmostragem)
        s1477 = self.generateSin(1477, gainY, duration,freqDeAmostragem)
        s1633 = self.generateSin(1633, gainY, duration,freqDeAmostragem)
        s697 = self.generateSin(697, gainY, duration,freqDeAmostragem)
        s770 = self.generateSin(770, gainY, duration,freqDeAmostragem)
        s852 = self.generateSin(852, gainY, duration,freqDeAmostragem)
        s941 = self.generateSin(941, gainY, duration,freqDeAmostragem)

        if input == '1':
            return s1209[1]+s697[1],s1209,s697

        elif input == '2':
            return s1336[1]+s697[1],s1336,s697

        elif input == '3':
            return s1477[1]+s697[1],s1477,s697

        elif input == '4':
            return s1209[1]+s770[1],s1209,s770

        elif input == '5':
            return s1336[1]+s770[1],s1336,s770

        elif input == '6':
            return s1477[1]+s770[1],s1477,s770

        elif input == '7':
            return s1209[1]+s852[1],s1209,s852

        elif input == '8':
            return s1336[1]+s852[1],s1336,s852

        elif input == '9':
            return s1477[1]+s852[1],s1477,s852

        elif input == '0':
            return s1336[1]+s941[1],s1336,s941

        elif input == 'X':
            return s1209[1]+s941[1],s1209,s941

        elif input == '#':
            return s1477[1]+s941[1],s1477,s941

        elif input == 'A':
            return s1633[1]+s697[1],s1633,s697

        elif input == 'B':
            return s1633[1]+s770[1],s1633,s770

        elif input == 'C':
            return s1633[1]+s852[1],s1633,s852

        elif input == 'D':
            return s1633[1]+s941[1],s1633,s941


