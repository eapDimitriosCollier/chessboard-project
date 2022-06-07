from GUI.ChessController import ChessController
from GUI.ChessView import ChessView
from GUI.ChessModel import ChessModel

if __name__ == '__main__':
    ChessCtrl=ChessController(ChessView,ChessModel)
    ChessCtrl.Start()