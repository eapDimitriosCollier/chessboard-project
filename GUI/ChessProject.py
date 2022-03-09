from fileinput import filename
import tkinter as tk
from reportlab.graphics import renderPDF, renderPM
from PIL import Image, ImageTk
import os
 
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def get_svg(fileName):
    drawing = svg2rlg(f'{fileName}.svg')
    renderPM.drawToFile(drawing, f'{fileName}.png', fmt="PNG")
 
class Root:
    def __init__(self):
        window = tk.Tk()
        get_svg(ROOT_PATH+"/chessboard")
        chessboardPNG = Image.open(ROOT_PATH+"/chessboard.png")
        pChessboard = ImageTk.PhotoImage(chessboardPNG)
        size = img.size
        frame = tk.Canvas(window, width=size[0], height=size[1])
        print(size)
        frame.pack()
        get_svg(ROOT_PATH+"/chesspieces/pawnblack")
        img = Image.open(ROOT_PATH+"/chesspieces/pawnblack.png")
        pimg = ImageTk.PhotoImage(img)
        frame.create_image(0,0,anchor='nw',image=pimg)
        
        size = img.size
        print(size)
        frame = tk.Canvas(window, width=size[0], height=size[1])
        frame.pack()
        window.mainloop()

    def chesspieces(self):
        pieces = ["pawnwhite","rookwhite","knightwhite","bishopwhite","queenwhite","kingwhite","pawnblack","rookblack","knightblack","bishopblack","queenblack","kingblack",]
        for piece in pieces:
            self.images[piece] = tk.PhotoImage(file="./chesspieces" + piece + ".png")    

# get_svg(ROOT_PATH+"/chessboard.svg")
# window = Root()


    

# get_svg(ROOT_PATH+"\pawnblack.svg")

