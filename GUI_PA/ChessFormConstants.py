import os
ImagePath = os.getcwd()+"/GUI_PA/IMG"
MainWindowGeometryX=900
if sys.platform=='win32':
    MainWindowGeometryY=600
else:
    MainWindowGeometryY=650
ChessBoardX=600;ChessBoardY=600
ChessBoardSquareSize=64
ChessPieceSize=60
ChessBoardOffset=42+ChessBoardSquareSize-ChessPieceSize-1
BackGroundColor='#333333'
