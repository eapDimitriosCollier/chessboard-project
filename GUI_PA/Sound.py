import sys
import os

sys.path.append('../CHESSBOARD-PROJECT')
from playsound import playsound
MoveWAV = os.getcwd()+u'/GUI_PA/sound/Move.wav'
CheckWAV = os.getcwd()+u'/GUI_PA/sound/Check.wav'
CaptureWAV = os.getcwd()+u'/GUI_PA/sound/Capture.wav'


def PlayWAV(wav_file:str)->None:
    
    playsound(wav_file)


#PlayWAV(wavFile)
print (playsound.__doc__)