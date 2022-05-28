from cProfile import label
import tkinter as tk
import os
from Event.Event import Event
from ImageLabel.ImageLabel import ImageLabel

class Loading:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.gifPath = f'{os.getcwd()}/loading.gif'
        self.gif = None
        Event('LoadingMessage', message="").subscribe(self)
        self.loadingMessage = tk.Label(self.window, text="",  font='Helvetica 10 bold')
        self.loadingMessage.pack(side=tk.BOTTOM)
        self.gif = ImageLabel(self.window)
        
        self.gif.pack()
        self.gif.load(self.gifPath)
        self.window.withdraw()

    def start(self) -> None:
        self.window.after(0,self.window.deiconify)
        
    def stop(self) -> None:
        self.window.withdraw()

    def onLoadingMessage(self, event) -> None:
        self.loadingMessage.config(text=event.message)

if __name__ == '__main__':
    root = tk.Tk()
    x=Loading()
    
    Event('LoadingMessage', message='hi :)').invoke()
    x.start()
    root.mainloop()