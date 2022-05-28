import tkinter as tk
import os
from PIL import ImageTk,Image

class ErrorMessage:
    def __init__(self, root, errorMessage):
        self.window = tk.Toplevel(root)
        self.pngPath = f'{os.getcwd()}/ErrorMessage/error.png'
        self.errorImage = ImageTk.PhotoImage(Image.open(self.pngPath).resize(size=(25, 25)))
        self.errorLabel = tk.Label(self.window, image=self.errorImage)
        self.errorLabel.image = self.errorImage
        self.errorLabel.pack()

        self.errorMessage = tk.Label(self.window, text=errorMessage)
        self.errorMessage.pack()

if __name__ == '__main__':
    root = tk.Tk()
    ErrorMessage(root, "I failed bacause i suck")
    root.mainloop()
    

    