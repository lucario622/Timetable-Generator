import sys
import ctypes

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsView,
    QPushButton,
    QGridLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QGraphicsItem,
    QListWidget,
    QListWidgetItem,
    QTabWidget
)
from PyQt6.QtGui import QIcon, QColor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setWindowIcon(QIcon("Buildings/UA/0.png"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myapp.app.1")

        layout = QGridLayout()

        self.scene = QGraphicsScene(0, 0, 400, 200, parent=self)
        self.scene.addLine(
            0, 0, self.scene.width(), self.scene.height(), QColor(255, 0, 0)
        )
        self.scene.addRect(0, 0, 40, 40, QColor(0, 255, 0))
        self.scene.addEllipse(0, 0, 100, 100, QColor(0, 0, 255))
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.textN = []
        for i in range(4):
            for j in range(2):
                self.textN.append(self.placeLE(layout, i, 2 * j))
                self.placeLinkedButton(
                    layout,
                    i,
                    2 * j + 1,
                    "Button number " + str(2 * i + j + 1),
                    2 * i + j,
                )
        newbutton = QPushButton("Rotate")
        newbutton.clicked.connect(self.rotate)
        layout.addWidget(newbutton, 6, 2)
        
        listcheck = QPushButton("Check List")
        listcheck.clicked.connect(self.listCheck)
        layout.addWidget(listcheck, 7, 2)
        
        self.myListW = QListWidget()
        layout.addWidget(self.myListW,0,5)
        for i in range(10):
            myListItem = QListWidgetItem()
            myListItem.setText(f'The number {i+1}')
            self.myListW.addItem(myListItem)

        # print(textN)
        view = QGraphicsView(self.scene)
        layout.addWidget(view, 7, 7)
        # widget = QWidget()
        widget = QTabWidget()
        widget.setTabPosition(QTabWidget.TabPosition.West)
        widget.setMovable(True)
        for i in range(5):
            widget.addTab(QLabel(f'The number {i}'),f'The number {i}')
        # widget.setLayout(layout)
        self.setCentralWidget(widget)
        # for i in range(100):
        #     print(layout.itemAt(i))

    def listCheck(self):
        curitem = self.myListW.currentItem()
        if (curitem!=None): print(curitem.text())

    def rotate(self):
        for item in self.scene.selectedItems():
            item.setRotation(item.rotation() + 1)

    def mousePressEvent(self, a0):
        print(f"Left click moment at {a0.globalPosition()} or maybe {a0.pos()}")

    def buttonAction(self):
        print("button be got pushed")

    def placeButton(self, layout: QGridLayout, x, y, text):
        newbutton = QPushButton(text)
        layout.addWidget(newbutton, x, y)
        return newbutton

    def placeLinkedButton(self, layout: QGridLayout, x, y, text, linkedIndex):
        newbutton = QPushButton(text)
        newbutton.clicked.connect(lambda: print(self.summonText(linkedIndex)))
        layout.addWidget(newbutton, x, y)
        return newbutton

    def placeLabel(self, layout: QGridLayout, x, y, text):
        newLabel = QLabel(text)
        layout.addWidget(newLabel, x, y)
        return newLabel

    def placeLE(self, layout: QGridLayout, x, y):
        newLineEdit = QLineEdit()
        layout.addWidget(newLineEdit, x, y)
        return newLineEdit

    def summonText(self, index):
        return self.textN[index].text()


def outerFunction():
    print("outer print")


def outerPrint(text):
    print(text)


app = QApplication(sys.argv)


window = MainWindow()
window.show()

app.exec()
