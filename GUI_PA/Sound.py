import os
import threading
import winsound
import sys
sys.path.append('../CHESSBOARD-PROJECT')
from Event.Event import Event, invoke
MoveWAV = os.getcwd()+u'/GUI_PA/sound/Move.wav'
CheckWAV = os.getcwd()+u'/GUI_PA/sound/CheckII.wav'
CaptureWAV = os.getcwd()+u'/GUI_PA/sound/Cap.wav'

class Sound:
    PlayQueue=[]
    ThreadLock=threading.Lock()
    isInit=False

    @classmethod
    def onWavInQueue(cls,event):
        cls.__Play()

    @classmethod
    def __Play(cls):
        Event('WavisPlaying').invoke()
        cls.ThreadLock.acquire()
        wav=cls.PlayQueue.pop(0)
        cls.ThreadLock.release()
        thread=threading.Thread(target=winsound.PlaySound,args=(wav, winsound.SND_FILENAME,))
        thread.isDaemon=True
        thread.start()
        #thread.join()
        
    @classmethod
    def PlayWAV(cls,wav_file:str)->None:
        cls.ThreadLock.acquire()
        if not getattr(cls,"isInit"):
            Event('WavInQueue').subscribe(cls)
            setattr(cls,"isInit",True)
        cls.PlayQueue.append(wav_file)
        cls.ThreadLock.release()
        Event('WavInQueue').invoke()        
        

if __name__ == '__main__':
    for _ in range(10):
        thread=threading.Thread(target=Sound.PlayWAV,args=(MoveWAV,))
        thread.start()
        thread=threading.Thread(target=Sound.PlayWAV,args=(CheckWAV,))
        thread.start()
        thread=threading.Thread(target=Sound.PlayWAV,args=(CaptureWAV,))
        thread.start()
    

