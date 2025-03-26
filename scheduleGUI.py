import sys
import ctypes

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget
from PyQt6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setWindowIcon(QIcon("Buildings/UA/0.png"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myapp.app.1")

        layout = QGridLayout()

        for i in range(5):
            for j in range(5):
                if (i+j)%2==0:
                    self.placeButton(layout,i,j,"Button number "+str(5*i+j+1))
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def buttonAction(self):
        print("button be got pushed")
        
    def placeButton(self,layout:QGridLayout,x,y,text):
        newbutton = QPushButton(text)
        newbutton.clicked.connect(lambda :print(text))
        layout.addWidget(newbutton,x,y)


def outerFunction():
    print("outer print")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
