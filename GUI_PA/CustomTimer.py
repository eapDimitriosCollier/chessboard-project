import threading
class RepeativeTimer(threading.Timer):  
    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__(interval, function, args, kwargs)
        self.__isActive=True
        self.daemon=True
        
    def run(self):
        while not self.finished.wait(self.interval):  
            self.function(*self.args,**self.kwargs)  

    def stop(self):
        self.cancel()
        self.__isActive=False

    @property
    def isActive(self)->bool:
        return self.__isActive



def PrintMsg(str):
    print (str,"\n")

if __name__ == '__main__':
    RT=RepeativeTimer(1,PrintMsg,("this is a message",))
    RT.start()
    
    for _ in range(10):
        print (RT.IsActive)
    
    RT.stop()
    print (RT.IsActive)