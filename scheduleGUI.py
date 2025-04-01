import json
import math
import random
import sys
import ctypes

from ScheduleGenerator import makedatas, betteroptionstoschedules, allCourses

from PyQt6.QtCore import QSize, Qt, QRectF
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
    QComboBox,
)
from PyQt6.QtGui import QIcon, QColor, QFont, QCursor

WIDTH = 1920
HEIGHT = 1060

resolution:QSize = QSize()

weights:list[int] = []

uniqueCodes:list[str] = []

currentCodes:list[str] = []

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
        times:CourseTime,
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

uniqueCourses:dict[str,Course] = dict()

class timeAmount:
    def __init__(self, value):
        self.totalMs = value
        self.totalSeconds = value // 1000
        self.totalMinutes = value // 1000 // 60
        self.totalHours = value // 1000 // 60 // 60
        self.totalDays = value // 1000 // 60 // 60 // 24
        self.totalYears = value // 1000 // 60 // 60 // 24 // 365
        self.remMs = value % 1000
        self.remSeconds = value // 1000 % 60
        self.remMinutes = value // 1000 // 60 % 60
        self.remHours = value // 1000 // 60 // 60 % 24
        self.remDays = value // 1000 // 60 // 60 // 24 % 365

    def __str__(self):
        result = ""
        if self.totalYears != 0:
            result += f"{int(self.totalYears)} Years, "
        if self.totalDays != 0:
            result += f"{int(self.remDays)} Days, "
        if self.totalHours != 0:
            result += f"{int(self.remHours)} Hours, "
        if self.totalMinutes != 0:
            result += f"{int(self.remMinutes)} Minutes, "
        if self.totalSeconds != 0:
            result += f"{int(self.remSeconds)} Seconds, "
        if self.totalMs != 0:
            result += f"{round(self.remMs,4)} ms"
        return result

class GeneralCourse:
    def __init__(
        self,
        title: str,
        code: str,
        sections:list[Course]
    ):
        self.title = title
        self.code = code
        self.sections = sections
    
    def __str__(self):
        return f"{self.code}|{self.title} {len(self.sections)} sections"
    
    def get(self, query: str):
        match query.lower():
            case "title":
                return self.title
            case "code":
                return self.code
            case "sections":
                return self.sections
            case _:
                return ""

class Schedule:
    def __init__(self, courses: list[Course], name: str = "Untitled Schedule"):
        if type(courses)==list[int]:
            self.crns = courses
            self.courses = []
            for crn in self.crns:
                self.courses.append(allCourses[crn]) # type: ignore
        else:
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
                myQGRI = scene.addRect(myRect,brush=myColor)
                myQGRI.setData(69420,course.crn)
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
        for sceneitem in scene.items():
            if sceneitem.type() == 3:
                sceneitem.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

def getscore(x: Schedule):
    """
    Used to sort scored_list in optionstoschedules()
    """
    return x.calcscore()

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

undoStack = []

class ViewOneSchedule(QWidget):
    def __init__(self):
        super().__init__()

        self.tabLayout = QGridLayout()

        self.setLayout(self.tabLayout)

        self.scene = QGraphicsScene(0, 0, int(resolution.width()*0.7), int(resolution.height()*0.8), parent=self)
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
        self.rightPanel.setFixedWidth(int(resolution.width()*0.25))
        myFont = QFont()
        myFont.setPixelSize(20)
        self.courseList.setFont(myFont)
        
        self.tabLayout.addWidget(self.view, 0, 0)
        self.rlayout.addWidget(self.courseList)
        self.rlayout.addWidget(self.courseListButtons)
        
        self.tabLayout.addWidget(self.rightPanel, 0, 1)

    def omitcourse(self):
        for QGitem in self.scene.selectedItems():
            self.omitcrn(QGitem.data(69420))
        curitem = self.courseList.currentItem()
        currow = self.courseList.currentRow()
        if curitem != None:
            curcrn = self.schedule.courses[currow].crn
            if (len(undoStack)>0 and int(undoStack[-1][1:]) == curcrn):
                self.parent().parent().parent().undoOmission()
            else:
                self.parent().parent().parent().undobutton.setEnabled(True)
                if not (curcrn in removedCRNS):
                    removedCRNS.append(curcrn)
                    curdatas = makedatas(currentCodes,allCourses,removedCRNS)
                    curtotal = calctotal(curdatas)
                    print(str(curtotal) + " Courses to be processed after having removed " + str(curcrn))
                    thebutton:QPushButton = self.parent().parent().parent().regeneratebutton
                    esttime = timeAmount(self.parent().parent().parent().avgtime*curtotal*1000)
                    thebutton.setText(f"Re-Generate Schedules (est. {esttime})")
                    undoStack.append("+"+str(curcrn))
                    curitem.setBackground(QColor('black'))
                    curitem.setForeground(QColor('white'))
                else:
                    removedCRNS.remove(curcrn)
                    curdatas = makedatas(currentCodes,allCourses,removedCRNS)
                    curtotal = calctotal(curdatas)
                    thebutton:QPushButton = self.parent().parent().parent().regeneratebutton
                    esttime = timeAmount(self.parent().parent().parent().avgtime*curtotal*1000)
                    thebutton.setText(f"Re-Generate Schedules (est. {esttime})")
                    undoStack.append("-"+str(curcrn))
                    random.seed(curcrn)
                    minC = 100
                    maxC = 255
                    myColor = QColor(random.randrange(minC,maxC),random.randrange(minC,maxC),random.randrange(minC,maxC))
                    curitem.setForeground(QColor('black'))
                    curitem.setBackground(myColor)
                self.schedule.redrawSchedule(self.scene)
                self.parent().parent().parent().undobutton.setText(f"Undo Course Omission ({len(undoStack)})")
        # self.courseList.setFocus()
        
    def omitcrn(self,curcrn:int):
        if curcrn in self.schedule.crns:
            curitem = self.courseList.item(self.schedule.crns.index(curcrn))
            if (len(undoStack)>0 and int(undoStack[-1][1:]) == curcrn):
                self.parent().parent().parent().undoOmission()
            else:
                self.parent().parent().parent().undobutton.setEnabled(True)
                if not (curcrn in removedCRNS):
                    removedCRNS.append(curcrn)
                    curdatas = makedatas(currentCodes,allCourses,removedCRNS)
                    curtotal = calctotal(curdatas)
                    thebutton:QPushButton = self.parent().parent().parent().regeneratebutton
                    esttime = timeAmount(self.parent().parent().parent().avgtime*curtotal*1000)
                    thebutton.setText(f"Re-Generate Schedules (est.{str(esttime)})")
                    undoStack.append("+"+str(curcrn))
                    curitem.setBackground(QColor('black'))
                    curitem.setForeground(QColor('white'))
                else:
                    removedCRNS.remove(curcrn)
                    curdatas = makedatas(currentCodes,allCourses,removedCRNS)
                    curtotal = calctotal(curdatas)
                    thebutton:QPushButton = self.parent().parent().parent().regeneratebutton
                    esttime = timeAmount(self.parent().parent().parent().avgtime*curtotal*1000)
                    thebutton.setText(f"Re-Generate Schedules (est.{esttime})")
                    undoStack.append("-"+str(curcrn))
                    random.seed(curcrn)
                    minC = 100
                    maxC = 255
                    myColor = QColor(random.randrange(minC,maxC),random.randrange(minC,maxC),random.randrange(minC,maxC))
                    curitem.setForeground(QColor('black'))
                    curitem.setBackground(myColor)
                self.schedule.redrawSchedule(self.scene)
                self.parent().parent().parent().undobutton.setText(f"Undo Course Omission ({len(undoStack)})")
    
    def listUpdate(self,curitem:QListWidgetItem,previtem:QListWidgetItem):
        if curitem != None:
            curitem.setForeground(QColor('white'))
            self.schedule.redrawSchedule(self.scene)
        if previtem != None and (not self.schedule.courses[self.courseList.indexFromItem(previtem).row()].crn in removedCRNS):
            previtem.setForeground(QColor('black'))

    def setSchedule(self, schedule: Schedule):
        self.schedule = schedule
        schedule.drawScheduleBG(self.scene)
        schedule.redrawSchedule(self.scene)
        for course in self.schedule.courses:
            myitem = QListWidgetItem(course.code + " " + course.title + " " + course.type)
            random.seed(course.crn)
            minC = 100
            maxC = 255
            myColor = QColor(random.randrange(minC,maxC),random.randrange(minC,maxC),random.randrange(minC,maxC))
            myitem.setForeground(QColor('black'))
            myitem.setBackground(myColor)
            self.courseList.addItem(myitem)
        self.rlayout.addWidget(QLabel(f"{schedule.fullClasses}/{len(schedule.crns)} classes full"))

class SchedulePanel(QWidget):
    def __init__(self):
        super().__init__()
        
        self.panelLayout = QVBoxLayout()
        self.panelLayout.setContentsMargins(0,0,0,0)
        
        self.regeneratebutton = QPushButton("Re-Generate Schedules")
        self.regeneratebutton.clicked.connect(self.regenerateSchedules)
        
        self.undobutton = QPushButton("Undo Course Omission")
        self.undobutton.clicked.connect(self.undoOmission)
        self.undobutton.setEnabled(False)
        self.undobutton.setToolTip("Undo last course removal (Ctrl+Z)")
        
        self.tabs = ViewSchedules()
        
        self.panelLayout.addWidget(self.regeneratebutton)
        self.panelLayout.addWidget(self.undobutton)
        self.panelLayout.addWidget(self.tabs)
        
        self.setLayout(self.panelLayout)
        self.avgtime = 1/4000
    
    def keyPressEvent(self, a0):
        if a0.key() == 90 and a0.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if len(undoStack)>0:
                self.undoOmission()
        return super().keyPressEvent(a0)
    
    def undoOmission(self):
        actiontoundo = undoStack.pop()
        self.undobutton.setText(f"Undo Course Omission ({len(undoStack)})")
        if len(undoStack) == 0:
            self.undobutton.setEnabled(False)
        actiontype = actiontoundo[0]
        crntoundo = int(actiontoundo[1:])
        if self.tabs.currentIndex() != -1: 
            ind:int = self.tabs.tabs[self.tabs.currentIndex()].schedule.crns.index(crntoundo)
            curitem:QListWidgetItem = self.tabs.tabs[self.tabs.currentIndex()].courseList.item(ind)
        if actiontype == "+":
            removedCRNS.remove(crntoundo)
            if self.tabs.currentIndex() != -1:
                random.seed(crntoundo)
                minC = 100
                maxC = 255
                myColor = QColor(random.randrange(minC,maxC),random.randrange(minC,maxC),random.randrange(minC,maxC))
                curitem.setForeground(QColor('black'))
                curitem.setBackground(myColor)
        else:
            removedCRNS.append(crntoundo)
            if self.tabs.currentIndex() != -1:
                curitem.setBackground(QColor('black'))
                curitem.setForeground(QColor('white'))
        if self.tabs.currentIndex() != -1: self.tabs.tabs[self.tabs.currentIndex()].schedule.redrawSchedule(self.tabs.tabs[self.tabs.currentIndex()].scene)
        if self.tabs.count() == 0:
            self.regenerateSchedules(codes=currentCodes)
    
    def regenerateSchedules(self,a0=False,codes:list[str]=None):
        window.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        if codes == None: codes = currentCodes
        im_cs = ["CSCI2072U","CSCI2040U","CSCI2020U","MATH2055U","MATH2060U","SCCO0999U"]
        cs_01 = ["MATH1010U","CSCI1030U","PHY1010U","CSCI1060U","COMM1050U"]
        datas:list[list[int]] = makedatas(codes,allCourses,removedCRNS)
        datotal = calctotal(datas)
        scheds, ttltime = betteroptionstoschedules(datas)
        if datotal != 0: self.avgtime = ttltime/datotal 
        else: self.avgtime = 1/4000
        print(str(ttltime) + " Time taken in seconds")
        print(str(self.avgtime) + " Time taken per item")
        print(f"{self.avgtime}*{datotal} = {self.avgtime*datotal} = {ttltime}")

        print(str(len(scheds)) + " valid schedules found")
        scored_list:list[Schedule] = []
        for i in range(
            len(scheds)
        ):  # score all schedules (might be time consuming if calcscore has O(n^2+) efficiency)
            scheds[i] = Schedule(scheds[i].crns)
            scheds[i].calcscore()
            scored_list.append(scheds[i])
        scored_list = sorted(scored_list, key=getscore, reverse=True)  # Sort by score
        
        shortscheds = []
        for e in scored_list[:6]:
            shortscheds.append(e.crns)
        self.tabs.clearSchedules()
        self.tabs.loadCrns(shortscheds)
        self.tabs.setFocus()
        window.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        esttime = timeAmount(ttltime*1000)
        self.regeneratebutton.setText(f"Re-Generate Schedules (est.{esttime})")
        # tabwidg.removeTab(3)
        # tabwidg.setCurrentIndex(2)

def calctotal(arr):
    total = 1
    for eachentry in arr:
        minitotal = 0
        for eacheachentry in eachentry:
            if not (eacheachentry in removedCRNS): minitotal += 1
        total *= minitotal
    return total

class ViewSchedules(QTabWidget):
    def __init__(self):
        super().__init__()

        self.tabs = []

        # myCrns = [72869, 72870, 73778, 75797, 75043, 74365, 75425, 74892, 75153, 70175]
        # myCrns = [
        #     40290,
        #     40299,
        #     42684,
        #     43913,
        #     43914,
        #     42944,
        #     42751,
        #     42757,
        #     40364,
        #     42978,
        #     41929
        # ]
        # self.addCrns(myCrns)
        # self.addCrns(
        #     [72870, 72869, 74366, 73777, 70175, 75043, 74364, 72850, 74363, 70120]
        # )
        self.currentChanged.connect(self.tabChanged)
        
    def clearSchedules(self):
        self.tabs = []
        self.clear()
    
    def tabChanged(self,ind:int):
        if ind != -1 and len(self.tabs) > 0:
            self.tabs[ind].schedule.redrawSchedule(self.tabs[ind].scene)

    def loadSchedules(self, schedulelist: list[Schedule]):
        for i in range(min(len(schedulelist), 10 - len(self.tabs))):
            self.addSchedule(schedulelist[i])

    def loadCrns(self, crnlist: list[list[int]]):
        for i in range(min(len(crnlist), 10 - len(self.tabs))):
            mySchedule = Schedule(crnlist[i])
            self.addSchedule(mySchedule)

    def addSchedule(self, schedule:Schedule):
        myTab = ViewOneSchedule()
        self.addTab(
            myTab, f"Schedule #{len(self.tabs)+1} - Score:{schedule.calcscore()}"
        )
        myTab.setSchedule(schedule)
        self.tabs.append(myTab)

    def addCrns(self, crns: list[int]):
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
        
        self.selectedCourses:list[str] = [] #List of course codes
        
        self.mainLayout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.centerLayout = QVBoxLayout()
        
        #left side
        termtype = int(str(list(allCourses)[0])[0])
        termstr = "Fall" if (termtype == 4) else "Winter"
        with open("Programs.json",'r') as f:
            filecontents:dict[str,list[list[str]]] = json.load(f)
        self.presetsmenu = QHBoxLayout()
        self.presetsDD = QComboBox()
        self.firsttime = True
        self.presetslabel = QLabel("Programs:")
        self.presetslabel.setBuddy(self.presetsDD)
        self.presetsPush = QPushButton("Add all")
        self.presetsPush.clicked.connect(self.addAllInPreset)
        self.presetsPush.setEnabled(False)
        self.presetsDD.currentIndexChanged.connect(self.presetselected)
        self.presetsDD.addItem(f"- Select -")
        print(filecontents.keys())
        for csname in filecontents:
            for i in range(4):
                if (i+termtype)%2==0: #correct term
                    self.presetsDD.addItem(f"{csname} Year {math.ceil(i/2.0)} {termstr}",filecontents[csname][i])
        
        self.codeinputlayout = QHBoxLayout()
        self.codeLabel = QLabel("Course Code:")
        self.codeInput = QLineEdit()
        self.codeInput.textEdited.connect(self.searchforcourses)
        self.codeLabel.setBuddy(self.codeInput)
        
        self.titleinputlayout = QHBoxLayout()
        self.nameLabel = QLabel("Course Title:")
        self.nameInput = QLineEdit()
        self.nameInput.textEdited.connect(self.searchforcourses)
        self.nameLabel.setBuddy(self.nameInput)
        
        self.codeinputlayout.addWidget(self.codeLabel)
        self.codeinputlayout.addWidget(self.codeInput)
        self.input1 = QWidget()
        self.input1.setLayout(self.codeinputlayout)
        self.titleinputlayout.addWidget(self.nameLabel)
        self.titleinputlayout.addWidget(self.nameInput)
        self.input2 = QWidget()
        self.input2.setLayout(self.titleinputlayout)
        self.presetsmenu.addWidget(self.presetslabel)
        self.presetsmenu.addWidget(self.presetsDD)
        self.presetsmenu.addWidget(self.presetsPush)
        self.DDbox = QWidget()
        self.DDbox.setLayout(self.presetsmenu)
        
        self.searchresults = QListWidget()
        self.searchresults.itemSelectionChanged.connect(self.updateAddButton)
        
        self.leftLayout.addWidget(self.DDbox)
        self.leftLayout.addWidget(self.input1)
        self.leftLayout.addWidget(self.input2)
        self.leftLayout.addWidget(self.searchresults)
        self.leftbox = QWidget()
        self.leftbox.setLayout(self.leftLayout)
        self.mainLayout.addWidget(self.leftbox)
        
        #center
        self.addCourseButton = QPushButton("Add")
        self.addCourseButton.clicked.connect(self.addSelected)
        self.addCourseButton.setEnabled(False)
        self.centerLayout.addWidget(self.addCourseButton)
        
        self.removeCourseButton = QPushButton("Remove")
        self.removeCourseButton.clicked.connect(self.removeSelected)
        self.centerLayout.addWidget(self.removeCourseButton)
        self.removeCourseButton.setEnabled(False)
        
        self.removeAllCourseButton = QPushButton("Remove All")
        self.removeAllCourseButton.clicked.connect(self.removeAll)
        self.centerLayout.addWidget(self.removeAllCourseButton)
        self.removeAllCourseButton.setEnabled(False)
        
        self.centerBox = QWidget()
        self.centerBox.setLayout(self.centerLayout)
        self.centerBox.setMaximumHeight(150)
        self.mainLayout.addWidget(self.centerBox)

        #right side
        self.rightLayout = QVBoxLayout()
        self.rightBox = QWidget()
        self.rightBox.setLayout(self.rightLayout)
        self.proceedButton = QPushButton("Proceed")
        self.proceedButton.clicked.connect(self.proceed)
        self.proceedButton.setEnabled(False)
        self.proceedButton.setMinimumHeight(100)
        self.selectionList = QListWidget()
        self.rightLayout.addWidget(self.selectionList)
        self.rightLayout.addWidget(self.proceedButton)
        self.mainLayout.addWidget(self.rightBox)
        
        self.setLayout(self.mainLayout)
        
    def proceed(self):
        global currentCodes
        currentCodes = self.selectedCourses
        print(currentCodes)
        mainwind:QTabWidget = self.parent().parent()
        mainwind.setTabVisible(2,True)
        mainwind.setCurrentIndex(2)
        schedview:SchedulePanel = mainwind.parent().viewSchedules
        schedview.regenerateSchedules(codes=currentCodes)

    def updateAddButton(self):
        if self.searchresults.currentItem() != None:
            self.addCourseButton.setEnabled(True)
        else:
            self.addCourseButton.setEnabled(False)
        
    def addAllInPreset(self):
        if self.presetsDD.currentIndex() != 0:
            self.removeAllCourseButton.setEnabled(True)
            self.removeCourseButton.setEnabled(True)
            self.proceedButton.setEnabled(True)
            for eachcode in self.presetsDD.itemData(self.presetsDD.currentIndex()):
                if not eachcode in self.selectedCourses:
                    self.selectionList.addItem(f"{eachcode} {uniqueCourses[eachcode].title}")
                    self.selectedCourses.append(eachcode)
            avgtime = self.parent().parent().parent().viewSchedules.avgtime
            if avgtime != 1:
                curdatas = makedatas(self.selectedCourses,allCourses,removedCRNS)
                curtotal = calctotal(curdatas)
                esttime = timeAmount(avgtime*curtotal*1000)
                self.proceedButton.setText(f"Proceed (est.{esttime})")
        
    def presetselected(self,ind):
        if self.firsttime:
            self.firsttime = False
            return
        if self.presetsDD.currentIndex() != 0:
            self.presetsPush.setEnabled(True)
            self.searchresults.clear()
            for eachcode in self.presetsDD.itemData(ind):
                self.searchresults.addItem(f"{eachcode} {uniqueCourses[eachcode].title}")
        else:
            self.searchresults.clear()
            self.presetsPush.setEnabled(False)

    
    def searchforcourses(self):
        self.searchresults.clear()
        count = 0
        if self.codeInput.text() == "" and self.nameInput.text() == "":
            self.addCourseButton.setEnabled(False)
            return
        for eachcode in uniquesorted:
            eachtitle = uniqueCourses[eachcode].title
            titlehit = (self.nameInput.text() != "" and self.nameInput.text().lower() in eachtitle.lower())
            codehit = (self.codeInput.text() != "" and self.codeInput.text().lower() in eachcode.lower())
            if (codehit and self.nameInput.text() == "") or (titlehit and self.codeInput.text() == "") or (titlehit and codehit):
                self.searchresults.addItem(f"{eachcode} {eachtitle}")
                count+=1
        if count == 0:
            self.addCourseButton.setEnabled(False)
        if count == 1:
            self.searchresults.setCurrentRow(0)
    
    def addSelected(self):
        curitem = self.searchresults.currentItem()
        if curitem != None:
            if curitem.text().split(" ")[0] in self.selectedCourses:
                print("Already Added")
            else:
                print(f"Add course {curitem.text()}")
                self.removeCourseButton.setEnabled(True)
                self.removeAllCourseButton.setEnabled(True)
                self.proceedButton.setEnabled(True)
                self.selectionList.addItem(curitem.text())
                self.selectedCourses.append(curitem.text().split(" ")[0])
                avgtime = self.parent().parent().parent().viewSchedules.avgtime
                if avgtime != 1:
                    curdatas = makedatas(self.selectedCourses,allCourses,removedCRNS)
                    curtotal = calctotal(curdatas)
                    esttime = timeAmount(avgtime*curtotal*1000)
                    self.proceedButton.setText(f"Proceed (est.{esttime})")
        else:
            print("No Course selected")
        
    def removeAll(self):
        self.removeAllCourseButton.setEnabled(False)
        self.selectionList.clear()
        self.selectedCourses = []
        self.proceedButton.setText("Proceed")
        self.removeCourseButton.setEnabled(False)
        self.proceedButton.setEnabled(False)
        
    def removeSelected(self):
        curitem = self.selectionList.currentItem()
        if curitem != None:
            print(f"Remove course {curitem.text()}")
            ccode = curitem.text().split(" ")[0]
            removedrow = self.selectionList.takeItem(self.selectionList.currentRow())
            del removedrow
            self.selectedCourses.remove(ccode)
            if self.selectionList.count() == 0:
                self.proceedButton.setText("Proceed")
                self.removeCourseButton.setEnabled(False)
                self.removeAllCourseButton.setEnabled(False)
                self.proceedButton.setEnabled(False)
            else:
                avgtime = self.parent().parent().parent().viewSchedules.avgtime
                if avgtime != 1:
                    curdatas = makedatas(self.selectedCourses,allCourses,removedCRNS)
                    curtotal = calctotal(curdatas)
                    esttime = timeAmount(avgtime*curtotal*1000)
                    self.proceedButton.setText(f"Proceed (est.{esttime})")
        else:
            print("No Course selected")

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

        self.inputCourses = InputCourses()
        tabs.addTab(self.inputCourses, "Courses")

        self.inputPrefs = InputPreferences()
        tabs.addTab(self.inputPrefs, "Preferences")

        self.viewSchedules = SchedulePanel()
        tabs.addTab(self.viewSchedules, "Schedules")

        # tabs.setTabEnabled(2,False)
        tabs.setTabVisible(2,False)
        tabs.setTabVisible(1,False)
        # tabs.setCurrentIndex(2)

        self.setCentralWidget(tabs)

    def keyPressEvent(self, a0):
        # print(a0.key())
        # print(a0.text())
        # print(a0.modifiers())
        # print("----------")
        if a0.key() == 16777216 and a0.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            sys.exit()
        return super().keyPressEvent(a0)

allCoursesJSON = []
removedCRNS = []
allCourses:dict[int,Course] = dict()

def firstNumIndex(str: str):
    for i in range(len(str)):
        if str[i].isnumeric():
            return i

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
    allCourses[crn] = temp
allCourses = dict(sorted(allCourses.items()))


for course in allCourses.values():
    if course.code in uniqueCodes:
        uniqueCourses[course.code].get("sections").append(course)
    else:
        newGenCourse:GeneralCourse = GeneralCourse(course.title,course.code,[course])
        uniqueCodes.append(course.code)
        uniqueCourses[course.code] = newGenCourse

uniquesorted = sorted(uniqueCourses,key=lambda a:a[firstNumIndex(a):-1])

app = QApplication(sys.argv)
resolution = app.primaryScreen().size()
window = MainWindow()
window.showFullScreen()
# window.showMaximized()
# window.show()

app.exec()
