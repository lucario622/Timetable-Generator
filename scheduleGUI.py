import json
import math
import random
import sys
import ctypes

from PyQt6.QtCore import QSize, Qt, QRectF
# from PyQt6.QtCore.Qt import 
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
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtGui import QIcon, QColor, QFont

allCourses = dict()

WIDTH = 1920
HEIGHT = 1060


class CourseTime:
    def __init__(self, days: list, time: int, length: int, biweekly: int):
        self.days = days
        self.time = time
        self.length = length
        self.biweekly = biweekly

    def overlap(self, otherTime):
        for day in self.days:
            for otherday in otherTime.days:
                if day == otherday:
                    selfstarttime = miltohrspointmins(self.time)
                    selfendtime = selfstarttime+minstohrspointmins(self.length)
                    otherstarttime = miltohrspointmins(otherTime.time)
                    otherendtime = otherstarttime+minstohrspointmins(otherTime.length)
                    return (selfstarttime <= otherstarttime and selfendtime >= otherstarttime) or (selfstarttime <= otherendtime and selfendtime >= otherendtime)
        return False


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
            starttime:float = miltohrspointmins(self.times.time)
            endtime:float = starttime+minstohrspointmins(self.times.length)
            targettime:float = miltohrspointmins(time)
            return (starttime <= targettime and endtime >= targettime)
        else:
            return False

    def isattimegen(self, time: int):
        starttime:float = miltohrspointmins(self.times.time)
        endtime:float = starttime+minstohrspointmins(self.times.length)
        targettime:float = miltohrspointmins(time)
        return (starttime <= targettime and endtime >= targettime)

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
    def __init__(self, courses: list[Course], name: str = "Untitled Schedule"):
        self.courses = courses
        crns = []
        for course in self.courses:
            crns.append(course.crn)
        self.crns = crns
        self.name = name
        self.fullClasses = 0
        self.score = 0

    def __init__(self, crns: list[int], name: str = "Untitled Schedule"):
        self.crns = crns
        self.courses = []
        for crn in self.crns:
            self.courses.append(allCourses[crn])
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

    def drawScheduleBG(self, scene: QGraphicsScene):
        days = [
            ["Monday", "Tuedsay", "Wednesday", "Thursday", "Friday"],
            ["M", "T", "W", "R", "F"],
            [1, 2, 3, 4, 5],
        ]
        WIDTH = scene.width()
        HEIGHT = scene.height()
        scene.addRect(0, 0, WIDTH, HEIGHT, brush=QColor(250, 250, 250))

        # Draw Time numbers on left edge
        k = 0
        for i in range(700, 2200):
            j = i
            if i % 100 == 30:
                j += 20
            if i % 100 == 0 or (i - 30) % 100 == 0:
                suffix = "am"
                if i>=1200: suffix = "pm"
                y = 40 + (j - 700) * ((HEIGHT - 55) / 1500)
                makeText(scene,miltoreadable(i)+suffix,"black",5,y)
                if k%2==0: scene.addLine(0,y,WIDTH,y,QColor(200,200,200)) # Line to ease time recognition
                else: drawDashedLine(scene,0,y,WIDTH,y,3,QColor(200,200,200))
                k+=1

        # Draw days of week on top edge
        for j in range(len(days[0])):
            x = (0.1 + 0.18 * j) * WIDTH
            makeText(scene, days[0][j], "black", x, 0,30)
            scene.addLine(x,0,x,HEIGHT,QColor(200,200,200))
                    
    def redrawSchedule(self,scene:QGraphicsScene):
        selectedcrn = self.courses[scene.parent().courseList.currentRow()].crn
        if scene.parent().courseList.currentRow() == -1:
            selectedcrn = -1
        days = [
            ["Monday", "Tuedsay", "Wednesday", "Thursday", "Friday"],
            ["M", "T", "W", "R", "F"],
            [1, 2, 3, 4, 5],
        ]
        WIDTH = scene.width()
        HEIGHT = scene.height()

        # Draw courses
        for course in self.courses:
            fontcolor = 'black'
            if course.crn in removedCRNS:
                fontcolor = 'white'
                myColor = QColor(0,0,0)
            elif course.crn == selectedcrn:
                myColor = QColor(255, 15, 15)
            else :
                random.seed(course.crn)
                minC = 100
                maxC = 255
                myColor = QColor(random.randrange(minC,maxC),random.randrange(minC,maxC),random.randrange(minC,maxC))
            for day in course.times.days:
                x = (0.1 + 0.18 * (days[1].index(day))) * WIDTH  # works
                y = 40 + (miltohrspointmins(course.times.time)-7)/15 * (HEIGHT-55)  # not so much
                h = minstohrspointmins(course.times.length)/15 * (HEIGHT-55)

                myRect = QRectF(x,y,WIDTH * 0.17,h)
                scene.addRect(myRect,brush=myColor)
                # scene.addRect(x,y,WIDTH * 0.17,h,brush=myColor)
                content = f"{course.title} {course.type} {course.room} crn:{course.crn}"
                space = int(WIDTH * 0.03)
                index = lastIndexOf(content[:space]," ")
                makeText(scene, content[:index], fontcolor, x, y)
                content = content[index+1:]
                if len(content) >= 0:
                    makeText(scene, content[:space], fontcolor, x, y + 15)
                    content = content[index+1:]
                if len(content) >= 0:
                    makeText(scene, content[:space], fontcolor, x, y + 30)

def drawDashedLine(scene:QGraphicsScene,x,y,x1,y1,dashLength:int,color:QColor):
    dx = abs(x1-x)
    dy = abs(y1-y)
    length = math.sqrt(dx**2+dy**2)
    dashes = length/dashLength/2
    xlength = dx/dashes/2
    ylength = dy/dashes/2
    for i in range(int(dashes)):
        j = 2*i
        scene.addLine(x+j*xlength,y+j*ylength,x+(j+1)*xlength,y1+(j+1)*ylength,color)

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


def minstohrspointmins(mins: int):
    """
    e.g. 384 (minutes) -> 6.4 (hours)
    """
    return mins/60


def minstopercent(mins: int):
    """
    e.g. 384 (minutes) -> 0.2666...
    """
    return minstohrspointmins(mins) / 24


def miltohrspointmins(time: int):
    """
    e.g. 1230 -> 12.5
    """
    return math.floor(time / 100) + ((time % 100) / 60)


def miltopercent(time: int):
    """
    e.g. 1230 -> 0.5208333...
    """
    return miltohrspointmins(time) / 24


def makeText(
    scene: QGraphicsScene,
    text: str,
    color: str,
    x: int,
    y: int,
    size: int = 12,
    rot: int = 0,
):
    thisFont = QFont()
    thisFont.setPixelSize(size)
    thisText = scene.addText(text)
    thisText.setFont(thisFont)
    thisText.setPos(x, y)
    thisText.setRotation(rot)
    thisText.setDefaultTextColor(QColor(color))

def lastIndexOf(str: str, target: str):
    return len(str) - str[::-1].index(target[::-1]) - len(target)

def minutes2hours(minutes: int):
    """
    Takes number of minutes and returns int with last 2 digits as minutes and all other digits as hours (e.g. 150->230 (2 hours 30 minutes))
    """
    return ((minutes // 60) * 100) + (minutes % 60)


class ViewOneSchedule(QWidget):
    def __init__(self):
        super().__init__()

        self.tabLayout = QGridLayout()

        self.setLayout(self.tabLayout)

        self.scene = QGraphicsScene(0, 0, 1300, 800, parent=self)
        self.view = QGraphicsView(self.scene)
        
        self.rightPanel = QWidget()
        self.rlayout = QVBoxLayout()
        self.rlayout.setContentsMargins(0,0,0,0)
        self.rightPanel.setLayout(self.rlayout)
        
        self.courseListButtons = QWidget()
        self.rhlayout = QHBoxLayout()
        self.courseListButtons.setLayout(self.rhlayout)
        
        self.omitbutton = QPushButton("Omit Course")
        self.omitbutton.clicked.connect(self.omitcourse)
        
        self.rhlayout.addWidget(self.omitbutton)
        
        self.courseList = QListWidget()
        self.courseList.currentItemChanged.connect(self.listUpdate)
        self.rightPanel.setFixedWidth(500)
        myFont = QFont()
        myFont.setPixelSize(20)
        self.courseList.setFont(myFont)
        
        self.tabLayout.addWidget(self.view, 0, 0)
        self.rlayout.addWidget(self.courseList)
        self.rlayout.addWidget(self.courseListButtons)
        
        self.tabLayout.addWidget(self.rightPanel, 0, 1)

    def omitcourse(self):
        curitem = self.courseList.currentItem()
        currow = self.courseList.currentRow()
        if curitem != None:
            if not (self.schedule.courses[currow].crn in removedCRNS):
                removedCRNS.append(self.schedule.courses[currow].crn)
            else:
                removedCRNS.remove(self.schedule.courses[currow].crn)
            self.schedule.redrawSchedule(self.scene)
            print(removedCRNS)
    
    def listUpdate(self):
        curitem = self.courseList.currentItem()
        if curitem != None:
            self.schedule.redrawSchedule(self.scene)

    def setSchedule(self, schedule: Schedule):
        self.schedule = schedule
        schedule.drawScheduleBG(self.scene)
        schedule.redrawSchedule(self.scene)
        for course in self.schedule.courses:
            self.courseList.addItem(
                course.code + " " + course.title + " " + course.type
            )
        self.rlayout.addWidget(QLabel(f"{schedule.fullClasses}/{len(schedule.crns)} classes full"))

class SchedulePanel(QWidget):
    def __init__(self):
        super().__init__()
        
        self.panelLayout = QVBoxLayout()
        self.panelLayout.setContentsMargins(0,0,0,0)
        
        self.regeneratebutton = QPushButton("Re-Generatate Schedules")
        self.regeneratebutton.clicked.connect(regenerateSchedules)
        
        self.tabs = ViewSchedules()
        
        self.panelLayout.addWidget(self.regeneratebutton)
        self.panelLayout.addWidget(self.tabs)
        
        self.setLayout(self.panelLayout)

class ViewSchedules(QTabWidget):
    def __init__(self):
        super().__init__()

        self.tabs = []

        myCrns = [72869, 72870, 73778, 75797, 75043, 74365, 75425, 74892, 75153, 70175]
        self.addSchedule(myCrns)
        self.addSchedule(
            [72870, 72869, 74366, 73777, 70175, 75043, 74364, 72850, 74363, 70120]
        )
        self.currentChanged.connect(self.tabChanged)
        
    def tabChanged(self,ind:int):
        self.tabs[ind].schedule.redrawSchedule(self.tabs[ind].scene)

    def loadSchedules(self, schedulelist: list[Schedule]):
        for i in range(min(len(schedulelist), 10 - len(self.tabs))):
            self.addSchedule(schedulelist[i])

    def loadSchedules(self, crnlist: list[list[int]]):
        for i in range(min(len(crnlist), 10 - len(self.tabs))):
            mySchedule = Schedule(crnlist[i])
            self.addSchedule(mySchedule)

    def addSchedule(self, schedule: Schedule):
        myTab = ViewOneSchedule()
        self.addTab(
            myTab, f"Schedule #{len(self.tabs)+1} - Score:{schedule.calcscore()}"
        )
        myTab.setSchedule(schedule)
        self.tabs.append(myTab)

    def addSchedule(self, crns: list[int]):
        myTab = ViewOneSchedule()
        mySchedule = Schedule(crns)
        self.addTab(
            myTab, f"Schedule #{len(self.tabs)+1} - Score:{mySchedule.calcscore()}"
        )
        myTab.setSchedule(mySchedule)
        self.tabs.append(myTab)


class InputCourses(QWidget):
    def __init__(self):
        super().__init__()


class InputPreferences(QWidget):
    def __init__(self):
        super().__init__()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Schedule Generator")
        self.setWindowIcon(QIcon("Buildings/UA/0.png"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myapp.app.1")

        tabs = QTabWidget()
        tabFont = QFont()
        tabFont.setPixelSize(20)
        tabs.setFont(tabFont)

        inputCourses = InputCourses()
        tabs.addTab(inputCourses, "Courses")

        inputPrefs = InputPreferences()
        tabs.addTab(inputPrefs, "Preferences")

        viewSchedules = SchedulePanel()
        tabs.addTab(viewSchedules, "Schedules")

        # tabs.setTabEnabled(2,False)
        tabs.setCurrentIndex(2)

        self.setCentralWidget(tabs)

    def keyPressEvent(self, a0):
        # print(a0.key())
        # print(a0.text())
        # print(a0.modifiers())
        # print("----------")
        if a0.key() == 16777216 and a0.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            sys.exit()
        return super().keyPressEvent(a0)

    def listCheck(self):
        curitem = self.myListW.currentItem()
        if curitem != None:
            print(curitem.text())

    def rotate(self):
        for item in self.scene.selectedItems():
            item.setRotation(item.rotation() + 1)

    # def mousePressEvent(self, a0):
    #     print(f"Left click moment at {a0.globalPosition()} or maybe {a0.pos()}")

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


def regenerateSchedules():
    pass

allCoursesJSON = []
removedCRNS = []

coursefile = "CourseFiles/Winter2025.json"

with open(coursefile, "r") as f:
    allCoursesJSON = json.load(f)
for course in allCoursesJSON:
    crn = course["crn"]
    temptimes = CourseTime(
        course["times"]["days"],
        course["times"]["time"],
        course["times"]["length"],
        course["times"]["biweekly"],
    )
    temp = Course(
        course["title"],
        course["room"],
        course["crn"],
        course["type"],
        course["code"],
        temptimes,
        course["section"],
        course["instructor"],
        course["maxpop"],
        course["curpop"],
    )
    # if not (crn in allCourses):
    allCourses[crn] = temp
allCourses = dict(sorted(allCourses.items()))

app = QApplication(sys.argv)
window = MainWindow()
window.showFullScreen()
# window.showMaximized()
# window.show()

app.exec()
