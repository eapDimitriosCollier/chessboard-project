from concurrent.futures import thread
from tkinter import *
from tkinter import messagebox
from time import time, sleep
#needs to install Pillow (pip install pillow)
from PIL import ImageTk,Image
import random
import threading

def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def quit():
    global root,thread
    print("terminating threads")
    for thread in threadList:
        print (thread)

    root.destroy()
    # root.quit()

def dosomething(x,y,z):   
    #root.after(4000, root.update())
    #obj=objList[z]
    i=random.randint(0, 7)
    r=random.randint(0, 7)
    obj=canvas.create_image(44+(i*64)+2, 44 + (0*64)+2, anchor=NW, image=piece_img) 
    c=0
    #btn["state"]=DISABLED
    for i in range (0,64*7):
        sleep(0.0005)
        #canvas.move(obj,0,1)
        canvas.moveto(obj,y=i+46)
       
    
    #btn["state"]=NORMAL
    
        
    # root.after(1000,canvas.move(objList[1],64,64))
    # root.after(1000,canvas.move(objList[1],64,64))
    # root.after(1000,canvas.move(objList[1],64,64))
    #return
def dosomethingElse():   
    canvas.move(obj,0,-64)


def startThread():
    
    x1=threading.Thread(target= dosomething,args=[1,1,random.randint(0, 7)])
    threadList.append(x1)
    #x2=threading.Thread(target= dosomething)
    #Setting the Daemon thread to True, makes it live in background when started and terminates when the main thread terminates
    x1.daemon=True
    x1.start()
    
    
    #x2.start()
    #x2.start()
    return x1
    
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        quit()
        #root.destroy()



root=Tk()
threadList=[]

root.geometry("800x600")
root.minsize(800, 600)
root.maxsize(800, 600)
#root.resizable(False,False)

canvas = Canvas(root, width = 800, height = 600)   
canvas['background']='#333333'
root.title("Chess PGN Viewer")
root.iconbitmap("./GUI_PA/img/ico/chess.ico")
chessBoard_img=ImageTk.PhotoImage(Image.open("./GUI_PA/img/chessboard_New.png"))
#chessLabel=Label(image=chessBoard_img)
piece_img=ImageTk.PhotoImage(Image.open("./GUI_PA/img/bKing.png"))
#pieceLabel=Label(image=piece_img)
canvas.create_image(0, 0, anchor=NW, image=chessBoard_img) 
#canvas.create_image(45, 45, anchor=NW, image=piece_img) 
objList=[]
for r in range(0,1):
    for i in range(0,8):
        pass
        #objList.append(canvas.create_image(44+(i*64)+2, 44 + (r*64)+2, anchor=NW, image=piece_img) )
canvas.pack()


#obj=objList[1]

#btn=Button(root,text="Going Down",command=dosomething)
btn=Button(root,text="Going Down",command=startThread)
btn2=Button(root,text="Going Up",command=dosomethingElse)


# quit_button = tk.Button(root, text = "Quit", command = root.quit, anchor = 'w',
#                     width = 10, activebackground = "#33B5E5")
# quit_button_window = canvas.create_window(10, 10, anchor='nw', window=quit_button)   

button1_window = canvas.create_window(640, 10, anchor='nw', window=btn) 
button2_window = canvas.create_window(730, 10, anchor='nw', window=btn2)
root.protocol("WM_DELETE_WINDOW", on_closing)
canvas.pack()
#chessLabel.pack()
#pieceLabel.pack()
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
# filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=donothing)
# filemenu.add_command(label="Save", command=donothing)
# filemenu.add_command(label="Save as...", command=donothing)
filemenu.add_command(label="Close", command=donothing)

filemenu.add_separator()

#filemenu.add_command(label="Exit", command=root.quit)
filemenu.add_command(label="Exit", command=quit)
menubar.add_cascade(label="File", menu=filemenu)
# editmenu = Menu(menubar, tearoff=0)
# editmenu.add_command(label="Undo", command=donothing)

# editmenu.add_separator()

# editmenu.add_command(label="Cut", command=donothing)
# editmenu.add_command(label="Copy", command=donothing)
# editmenu.add_command(label="Paste", command=donothing)
# editmenu.add_command(label="Delete", command=donothing)
# editmenu.add_command(label="Select All", command=donothing)

# menubar.add_cascade(label="Edit", menu=editmenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)

root.mainloop()




