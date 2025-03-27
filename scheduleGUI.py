import math
import sys
import ctypes
from typing import Iterable

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

allCourses = []

WIDTH = 1920
HEIGHT = 1060


class Course:
    def __init__(
        self,
        title: str,
        room: str,
        crn: int,
        type: str,
        code: str,
        times,
        section: int,
        instructor: list,
        maxpop: int,
        curpop: int,
    ):
        self.title = title
        self.room = room
        self.crn = crn
        self.type = type
        self.code = code
        self.times = times
        self.section = section
        self.instructor = instructor
        self.maxpop = maxpop
        self.curpop = curpop

    def isattime(self, day: str, time: int):
        if day in self.times.days:
            if time >= self.times.time and time <= (
                self.times.time + minutes2hours(self.times.length)
            ):
                return True
            else:
                return False
        else:
            return False

    def isattimegen(self, time: int):
        if time >= self.times.time and time <= (
            self.times.time + minutes2hours(self.times.length)
        ):
            return True
        else:
            return False

    def __str__(self):
        return f"{self.crn}: {self.code}|{self.title} {self.type} Section {self.section}. Meets at {self.times.time} on {self.times.days} for {self.times.length} minutes in room {self.room}"

    def overlap(self, otherCourse):
        return self.times.overlap(otherCourse.times)

    def fullDetail(self):
        return f"{self.crn}: {self.code}|{self.title} {self.type} Section {self.section} by {', '.join(self.instructor) }. Meets at {self.times.time} on {self.times.days} for {self.times.length} minutes in room {self.room} with {self.curpop}/{self.maxpop} students. Biweekly: {self.times.biweekly}"

    def get(self, query: str):
        match query.lower():
            case "title":
                return self.title
            case "room":
                return self.room
            case "crn":
                return self.crn
            case "type":
                return self.type
            case "code":
                return self.code
            case "times":
                return self.times
            case "days":
                return self.times.days
            case "time":
                return self.times.time
            case "length":
                return self.times.length
            case "biweekly":
                return self.times.biweekly
            case "section":
                return self.section
            case "instructor":
                return self.instructor
            case "maxpop":
                return self.maxpop
            case "curpop":
                return self.curpop
            case _:
                return ""


class Schedule:
    def __init__(self, courses: list, name: str = "Untitled Schedule"):
        self.courses = courses
        crns = []
        for course in self.courses:
            crns.append(course.crn)
        self.crns = crns
        self.name = name
        self.fullClasses = 0
        self.score = 0

    def checkValid(self):
        for course in self.courses:
            for course_ in self.courses:
                if course == course_:
                    continue
                if course.overlap(course_):
                    return False
        return True

    def checkFull(self):
        self.fullClasses = 0
        for course in self.courses:
            if course.curpop >= course.maxpop:
                self.fullClasses += 1
        return self.fullClasses > 0

    def calcscore(self):
        self.checkFull()

        # Check which days have classes and which don't
        self.daycount = 0
        counteddays = [0, 0, 0, 0, 0]
        days = ["M", "T", "W", "R", "F"]
        for course in self.courses:
            for day in days:
                if day in course.times.days:
                    counteddays[days.index(day)] = 1
        self.daycount = sum(counteddays)

        # add up time spent in class, in school, and in breaks
        classtime = 0
        schooltime = 0
        timeranges = []
        for day in days:
            starttime = 0
            endtime = 0
            for course in sorted(self.courses, key=lambda a: a.times.time):
                if day in course.times.days:
                    starttime = course.times.time
                    break
            for course in sorted(
                self.courses, key=lambda a: a.times.time, reverse=True
            ):
                if day in course.times.days:
                    endtime = course.times.time + minutes2hours(course.times.length)
                    if endtime % 100 >= 60:
                        endtime += 40
                    break
            timeranges.append([starttime, endtime])
        for each in timeranges:
            strt = (each[0] // 100) * 60 + (each[0] % 100)
            end = (each[1] // 100) * 60 + (each[1] % 100)
            schooltime += end - strt
        for course in self.courses:
            classtime += course.times.length
        breaktime = schooltime - classtime

        self.score = (5 - self.daycount) * 400
        self.score += 3900 - schooltime
        return self.score

    def __str__(self):
        return (
            self.name
            + ", "
            + str(len(self.courses))
            + " courses, Score: "
            + str(self.score)
        )

    def addCourse(self, crn):
        if crn not in allCourses:
            return False
        self.courses.append(allCourses[crn])
        self.crns.append(crn)
        if self.checkValid():
            return True
        self.crns.pop()
        self.courses.pop()
        return False

    def __eq__(self, other):
        for selfcrn in self.crns:
            if not selfcrn in other.crns:
                return False
        for othercrn in other.crns:
            if not othercrn in other.crns:
                return False
        return True

    def lunchBreaks(self):
        count = 0
        for day in ["M", "T", "W", "R", "F"]:
            if (
                self.courseatdaytime(day, 1200) == 0
                or self.courseatdaytime(day, 1240) == 0
            ):
                count += 1
        return count

    def courseatdaytime(self, day, time):
        for course in self.courses:
            if course.isattime(day, time):
                return course
        # return 0

    def drawSchedule(self, scene: QGraphicsScene):
        days = [
            ["Monday", "Tuedsay", "Wednesday", "Thursday", "Friday"],
            ["M", "T", "W", "R", "F"],
            [1, 2, 3, 4, 5],
        ]
        scene.addRect(0, 0, scene.width(), scene.height(), brush=QColor(0, 255, 0))
        for i in range(700, 2200):
            j = i
            if i % 100 == 30:
                j += 20
            if i % 100 == 0 or (i - 30) % 100 == 0:
                makeText(
                    scene,
                    miltoreadable(i),
                    "black",
                    5,
                    40 + (j - 700) * ((HEIGHT - 55) / 1500),
                )

        for j in range(len(days[0])):
            makeText(
                scene,
                days[0][j],
                "black",
                (0.1 + 0.18 * j) * WIDTH,
                10,
            )
        for course in self.courses:
            for day in course.times.days:
                x = (0.1 + 0.18 * (days[1].index(day))) * WIDTH
                y = 40 + (course.times.time - 700) * ((HEIGHT - 55) / 1500)
                scene.addRect(
                    x,
                    y,
                    WIDTH * 0.18,
                    minutes2hours(course.times.length) * ((HEIGHT - 55) / 1500),
                    brush=QColor(200, 255, 200),
                )
                content = f"{course.title} {course.type}"
                space = int(WIDTH * 0.03)
                makeText(scene, content[:space], "black", x, y)
                if len(content) >= space:
                    makeText(
                        scene,
                        content[space : 2 * space],
                        "black",
                        x,
                        y + 10,
                    )
                if len(content) >= 2 * space:
                    makeText(
                        scene,
                        content[2 * space : 3 * space],
                        "black",
                        x,
                        y + 20,
                    )


def miltoreadable(time: int):
    """
    Takes 24h time as integer and returns 12h time with colon (e.g. 1540->3:40)
    """
    if time % 100 == 60:
        time += 40
    if time >= 1300:
        time -= 1200
    result = str(math.floor(time / 100)) + ":" + str(time)[-2:]
    return result


def makeText(
    scene: QGraphicsScene,
    text: str,
    color: str,
    x: int,
    y: int,
    size: int = 15,
    rot: int = 0,
):
    thisFont = QFont()
    thisFont.setPixelSize(size)
    thisText = scene.addText(text)
    thisText.setPos(x, y)
    thisText.setRotation(rot)
    thisText.setDefaultTextColor(QColor(color))


def minutes2hours(minutes: int):
    """
    Takes number of minutes and returns int with last 2 digits as minutes and all other digits as hours (e.g. 150->230 (2 hours 30 minutes))
    """
    return ((minutes // 60) * 100) + (minutes % 60)


class ViewOneSchedule(QWidget):
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

    def setSchedule(self, schedule:Schedule):
        self.schedule = schedule
        schedule.drawSchedule(self.scene)
        print(schedule)


class ViewSchedules(QTabWidget):
    def __init__(self):
        super().__init__()

        self.tabs = []
        for i in range(6):
            myTab = ViewOneSchedule()
            self.addTab(myTab, f"Schedule #{i+1}")
            self.tabs.append(myTab)
            ",".join

    def loadSchedules(self, schedules:Iterable[Schedule]):
        for i in range(len(self.tabs)):
            self.tabs[i].setSchedule(schedules[i])


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
        self.setBaseSize(QSize(1920, 1061))
        # self.setL
        print(self.baseSize().width())
        print(self.width(), self.height())

        tabs = QTabWidget()
        tabFont = QFont()
        tabFont.setPixelSize(20)
        tabs.setFont(tabFont)
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
