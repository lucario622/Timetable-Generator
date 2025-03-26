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
    QTabWidget,
)
from PyQt6.QtGui import QIcon, QColor, QFont


class ViewSchedules(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()

        self.setLayout(self.layout)

        # for i in range(5):
        #     newbutton = QPushButton(f'The number {i+1}')
        #     self.layout.addWidget(newbutton,i,i)

        print(self.width(), self.height())
        self.scene = QGraphicsScene(0, 0, self.width(), self.height(), parent=self)
        self.view = QGraphicsView(self.scene)
        self.scene.addLine(
            0, 0, self.view.width(), self.view.height(), QColor(255, 0, 0)
        )
        self.scene.addLine(
            self.view.width(), 0, 0, self.view.height() * 2, QColor(255, 0, 0)
        )
        self.layout.addWidget(self.view, 0, 0)
        CourseList = QListWidget()
        for i in range(100):
            CourseList.addItem(f"{i}")
        myFont = QFont()
        myFont.setPixelSize(50)
        CourseList.setFont(myFont)
        self.layout.addWidget(CourseList, 0, 1)


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
        self.setBaseSize(QSize(1920,1061))
        self.setL
        print(self.baseSize().width())
        print(self.width(), self.height())

        tabs = QTabWidget()
        # tabs.setTabPosition(QTabWidget.TabPosition.North)

        inputCourses = InputCourses()
        tabs.addTab(inputCourses, "Courses")

        inputPrefs = InputPreferences()
        tabs.addTab(inputPrefs, "Preferences")

        print(self.width(), self.height())
        viewSchedules = ViewSchedules()
        tabs.addTab(viewSchedules, "Schedules")

        # tabs.setTabEnabled(2,False)
        tabs.setCurrentIndex(2)

        self.setCentralWidget(tabs)

    def keyPressEvent(self, a0):
        # print(a0.key())
        # print(a0.text())
        # print(a0.modifiers())
        # print("----------")
        if a0.key() == 16777216:
            sys.exit()
        return super().keyPressEvent(a0)

    def listCheck(self):
        curitem = self.myListW.currentItem()
        if curitem != None:
            print(curitem.text())

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
# window.showMaximized()
window.show()

app.exec()
