import sys
import ctypes

from PyQt6.QtCore import QSize
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

class ViewSchedules(QWidget):
    def __init__(self):
        super().__init__()
        
class InputCourses(QWidget):
    def __init__(self):
        super().__init__()
        
class InputPreferences(QWidget):
    def __init__(self):
        super().__init__()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setWindowIcon(QIcon("Buildings/UA/0.png"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myapp.app.1")
        
        # self.setFixedSize(QSize(1920,1061))

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(True)
            
        inputCourses = InputCourses()
        tabs.addTab(inputCourses,'Courses')
        
        inputPrefs = InputPreferences()
        tabs.addTab(inputPrefs,'Preferences')
        
        viewSchedules = ViewSchedules()
        tabs.addTab(viewSchedules,'Schedules')
        
        self.setCentralWidget(tabs)

    def keyPressEvent(self, a0):
        print(a0.key())
        print(a0.text())
        print(a0.modifiers())
        print("----------")
        return super().keyPressEvent(a0)

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

    def placeInputField(self, layout: QGridLayout, x, y):
        newLineEdit = QLineEdit()
        layout.addWidget(newLineEdit, x, y)
        return newLineEdit

    def summonText(self, index):
        return self.textN[index].text()

app = QApplication(sys.argv)

window = MainWindow()
window.showMaximized()

app.exec()
