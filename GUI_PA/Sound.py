import sys
import os

sys.path.append('../CHESSBOARD-PROJECT')
from playsound import playsound
MoveWAV = os.getcwd()+u'/GUI_PA/sound/Move.wav'
CheckWAV = os.getcwd()+u'/GUI_PA/sound/Check.wav'
CaptureWAV = os.getcwd()+u'/GUI_PA/sound/Cap.wav'


def PlayWAV(wav_file:str)->None:
    playsound(wav_file)


if __name__ == '__main__':
    PlayWAV(MoveWAV)
    PlayWAV(CheckWAV)
    PlayWAV(CaptureWAV)