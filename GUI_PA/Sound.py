import sys
import os
import threading

sys.path.append('../CHESSBOARD-PROJECT')
from playsound import playsound
MoveWAV = os.getcwd()+u'/GUI_PA/sound/Move.wav'
CheckWAV = os.getcwd()+u'/GUI_PA/sound/Check.wav'
CaptureWAV = os.getcwd()+u'/GUI_PA/sound/Cap.wav'


def PlayWAV(wav_file:str)->None:
    Thread=threading.Thread(target=playsound,args=(wav_file,))
    Thread.daemon=True
    Thread.start()        
    Thread.join()
    #playsound(wav_file)


if __name__ == '__main__':
    for _ in range(10):
        PlayWAV(MoveWAV)
        PlayWAV(CheckWAV)
        PlayWAV(CaptureWAV)