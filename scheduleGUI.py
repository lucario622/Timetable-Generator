import sys
import ctypes

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setWindowIcon(QIcon("Buildings/UA/0.png"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('myapp.app.1')

        button = QPushButton("My Button")
        button.setCheckable(True)
        button.clicked.connect(outerFunction)

        self.setFixedSize(QSize(400,800))

        self.setCentralWidget(button)

    def buttonAction(self):
        print("button be got pushed")

def outerFunction():
    print("outer print")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()