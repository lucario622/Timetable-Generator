import json
import math
import pygame
import os
from pygame.locals import *
from datetime import datetime
import time

# pygame.init()

WIDTH = 1920
HEIGHT = 1080

# coursefile = ""
# files = []
# for f in os.listdir("CourseFiles"):
#     files.append(f)
#     print(f, end=" ")
# print()


def firstNumIndex(str: str):
    for i in range(len(str)):
        if str[i].isnumeric():
            return i


# while True:
#     inp = input("Course File Name: ")
#     if inp in files:
#         coursefile = inp
#         break
#     if inp == "":
#         coursefile = "Winter2025.json"
#         break
#     if inp[-5:] != ".json":
#         inp += ".json"
#     if inp[1].isnumeric():
#         match inp[0]:
#             case "S":
#                 inp = "Summer" + inp[1:]
#             case "F":
#                 inp = "Fall" + inp[1:]
#             case "W":
#                 inp = "Winter" + inp[1:]
#             case _:
#                 continue
#         if inp.count("20") == 0:
#             x = firstNumIndex(inp)
#             inp = inp[:x] + "20" + inp[x:]
#     if inp in files:
#         coursefile = inp
#         break

# coursefile = "CourseFiles/" + coursefile

# WIDTH = 860
# HEIGHT = 540

# title_font = pygame.font.SysFont("Lucida Console", 15)
# text_font = pygame.font.SysFont("Lucida Console", 10)
# big_font = pygame.font.SysFont("Lucida Console", 30)

text_font = title_font = big_font = coursefile = None


class CampusMap:
    def __init__(self, rooms: dict):
        self.rooms = rooms

    def display(self, crn: int):
        if not crn in allCourses:
            return 0
        fullroom = str(allCourses[crn].room)
        notrooms = ["None", "OFFSITE", "SYN", "GEORGI_1", "GEORGI_2", "GEORGI_3"]
        if fullroom in notrooms:
            return 0
        if not fullroom[-1].isnumeric():
            return 0
        building = ""
        floor = 1
        roomid = 0
        for i in range(len(fullroom)):
            if fullroom[i:].isnumeric() or (
                fullroom[i + 1 :].isnumeric()
                and fullroom[i] == "B"
                and len(fullroom) - i == 4
                and (not fullroom[0] == "D")
            ):
                floor = fullroom[i]
                if floor == "B":
                    floor = 0
                floor = int(floor)
                building = fullroom[:i]
                break
        map_window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Map")
        while True:
            map_window.fill("white")
            filename = findfile(building, floor)
            chosen_map_image = pygame.image.load(filename)
            map_window.blit(chosen_map_image, (0, 0))
            pygame.draw.circle(
                map_window,
                "green",
                (self.rooms[fullroom][0], self.rooms[fullroom][1]),
                10,
                0,
            )
            pygame.display.flip()
            pygame.time.delay(100)
            events = pygame.event.get()
            for event in events:
                if event.type == KEYDOWN:
                    pygame.display.quit()
                    return 0

    def displaylist(self, crns):
        separated = []
        for j in range(len(crns)):
            crn = crns[j]
            if not crn in allCourses:
                continue
            fullroom = str(allCourses[crn].room)
            notrooms = ["None", "OFFSITE", "SYN", "GEORGI_1", "GEORGI_2", "GEORGI_3"]
            if fullroom in notrooms:
                continue
            if not fullroom[-1].isnumeric():
                continue
            building = ""
            floor = 1
            for i in range(len(fullroom)):
                if fullroom[i:].isnumeric() or (
                    fullroom[i + 1 :].isnumeric()
                    and fullroom[i] == "B"
                    and len(fullroom) - i == 4
                    and (not fullroom[0] == "D")
                ):
                    floor = fullroom[i]
                    if floor == "B":
                        floor = 0
                    floor = int(floor)
                    building = fullroom[:i]
                    separated.append([fullroom, building, floor])
                    break
        buildingfloors = dict()
        for each in separated:
            buildingfloor = each[1] + str(each[2])
            if buildingfloor in buildingfloors:
                buildingfloors[buildingfloor].append(each)
            else:
                buildingfloors[buildingfloor] = []
                buildingfloors[buildingfloor].append(each)
        buildingfloors = dict(sorted(buildingfloors.items()))
        map_window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Map")
        for key in buildingfloors:
            nextslide = False
            rms = buildingfloors[key]
            while nextslide == False:
                map_window.fill("white")
                filename = findfile(key[:-1], int(key[-1]))
                chosen_map_image = pygame.image.load(filename)
                map_window.blit(chosen_map_image, (0, 0))
                makeText(map_window, key, "black", 10, 10, 30)

                for room in rms:
                    fullroom = room[0]
                    pygame.draw.circle(
                        map_window,
                        "green",
                        (self.rooms[fullroom][0], self.rooms[fullroom][1]),
                        10,
                        0,
                    )
                pygame.display.flip()
                pygame.time.delay(100)
                events = pygame.event.get()
                for event in events:
                    if event.type == KEYDOWN:
                        nextslide = True
                        pygame.time.delay(250)
        pygame.display.quit()


def findfile(building: str, floor: int):
    result = "Buildings/"
    result += building
    result += "/"
    result += str(floor)
    result += ".png"
    return result


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
                self.fullClasses+=1
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
            for course in sorted(self.courses, key=getTime):
                if day in course.times.days:
                    starttime = course.times.time
                    break
            for course in sorted(self.courses, key=getTime, reverse=True):
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

    def combineWith(self, otherSchedule):
        self.courses = self.courses + otherSchedule.courses

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
        return 0

    def display(self, type):
        print(self.name, ": score = ", self.score, sep="")
        days = [
            ["Monday", "Tuedsay", "Wednesday", "Thursday", "Friday"],
            ["M", "T", "W", "R", "F"],
            [1, 2, 3, 4, 5],
        ]
        match type:
            case "map":
                campusmap.displaylist(self.crns)
            case "clock":
                width = 500
                height = 500
                clock_window = pygame.display.set_mode((width, height))
                pygame.display.set_caption("Timetable")
                while True:
                    clock_window.fill("white")
                    for i in range(6):
                        pygame.draw.ellipse(
                            clock_window,
                            "black",
                            (20 * i, 20 * i, width - 40 * i, height - 40 * i),
                            1,
                        )
                    radius = (height - 240) / 2
                    for i in range(30, 390, 30):
                        num = str(i // 30)
                        xpos = (width / 2) + (radius * math.sin(i / 180 * math.pi))
                        ypos = (height / 2) - (radius * math.cos(i / 180 * math.pi))
                        makeTextCent(clock_window, num, "black", xpos, ypos, 45, 0)
                    for i in range(5):
                        day = days[1][i]
                        radius = (height - (40 * i)) / 2
                        radius = radius - 15
                        for j in range(0, 360, 30):
                            xpos = (width / 2) + (radius * math.sin(j / 180 * math.pi))
                            ypos = (height / 2) - (radius * math.cos(j / 180 * math.pi))
                            makeTextCent(clock_window, day, "green", xpos, ypos, 30, j)
                    for course in self.courses:
                        for i in range(5):
                            # if i > 0:
                            #     continue
                            day = days[1][i]
                            if day in course.times.days:
                                rect = (i * 20, i * 20, width - i * 40, height - i * 40)
                                stime = course.times.time
                                if stime > 1200:
                                    stime -= 1200
                                etime = course.times.time + minutes2hours(
                                    course.times.length
                                )
                                if etime > 1200:
                                    etime -= 1200
                                # startangle = (stime/1200)*2*math.pi
                                startangle = (((stime // 100) / 12) * 2 * math.pi) + (
                                    (stime % 100) / 60 / 12
                                ) * 2 * math.pi
                                startangle = math.pi / 2 - startangle
                                endangle = (((etime // 100) / 12) * 2 * math.pi) + (
                                    (etime % 100) / 60 / 12
                                ) * 2 * math.pi
                                endangle = math.pi / 2 - endangle
                                pygame.draw.arc(
                                    clock_window, "red", rect, endangle, startangle, 20
                                )
                                makeArcText(
                                    clock_window,
                                    course.title + " " + course.type,
                                    "black",
                                    width / 2,
                                    height / 2,
                                    (height - i * 40) / 2,
                                    startangle,
                                    endangle,
                                )
                                # pygame.draw.arc(clock_window,"red",rect,startangle,endangle)
                    pygame.display.flip()
                    pygame.time.delay(100)
                    events = pygame.event.get()
                    for event in events:
                        if event.type == KEYDOWN and event.key == 32:
                            pygame.display.quit()
                            return
            case "window":
                calendar_window = pygame.display.set_mode((WIDTH, HEIGHT))
                pygame.display.set_caption("Timetable")
                while True:
                    calendar_window.fill("white")
                    for i in range(700, 2200):
                        j = i
                        if i % 100 == 30:
                            j += 20
                        if i % 100 == 0 or (i - 30) % 100 == 0:
                            makeText(
                                calendar_window,
                                miltoreadable(i),
                                "black",
                                5,
                                40 + (j - 700) * ((HEIGHT - 55) / 1500),
                            )
                    for j in range(len(days[0])):
                        makeText(
                            calendar_window,
                            days[0][j],
                            "black",
                            (0.1 + 0.18 * j) * WIDTH,
                            10,
                        )
                    for course in self.courses:
                        for day in course.times.days:
                            x = (0.1 + 0.18 * (days[1].index(day))) * WIDTH
                            y = 40 + (course.times.time - 700) * ((HEIGHT - 55) / 1500)
                            pygame.draw.rect(
                                calendar_window,
                                (200, 255, 200),
                                (
                                    x,
                                    y,
                                    WIDTH * 0.18,
                                    minutes2hours(course.times.length)
                                    * ((HEIGHT - 55) / 1500),
                                ),
                                0,
                            )
                            content = f"{course.title} {course.type} crn:{course.crn}"
                            space = int(WIDTH * 0.03)
                            makeText(calendar_window, content[:space], "black", x, y)
                            if len(content) >= space:
                                makeText(
                                    calendar_window,
                                    content[space : 2 * space],
                                    "black",
                                    x,
                                    y + 10,
                                )
                            if len(content) >= 2 * space:
                                makeText(
                                    calendar_window,
                                    content[2 * space : 3 * space],
                                    "black",
                                    x,
                                    y + 20,
                                )
                    pygame.display.flip()
                    pygame.time.delay(100)
                    events = pygame.event.get()
                    for event in events:
                        if event.type == KEYDOWN and event.key == 32:
                            pygame.display.quit()
                            return
            case "timetable":
                print(
                    "_____|    Monday     |    Tuesday    |   Wednesday   |   Thursday    |    Friday     |"
                )
                for i in range(700, 2200):
                    line = ""

                    if i % 100 == 0 or (i - 30) % 100 == 0:
                        line += miltoreadable(i)
                        if not (1000 <= i <= 1230):
                            line += " "
                        line += "|"
                        for j in range(len(days[0])):
                            found = False
                            for course in self.courses:
                                content = course.title + " " + course.type
                                if (
                                    days[1][j] in course.times.days
                                    and course.times.time == i + 10
                                ):
                                    found = True
                                    if len(content) < 15:
                                        line += content + "_" * (15 - len(content))
                                    else:
                                        line += content[:15]
                                    line += "|"
                                elif (
                                    days[1][j] in course.times.days
                                    and (
                                        course.times.time == i - 20
                                        or course.times.time == i - 60
                                    )
                                    and len(content) > 15
                                    and course.isattime(days[1][j], i - 1)
                                ):
                                    found = True
                                    if len(content) < 30:
                                        line += content[15:] + " " * (30 - len(content))
                                    else:
                                        line += content[15:30]
                                    line += "|"
                                elif (
                                    days[1][j] in course.times.days
                                    and (
                                        course.times.time == i - 50
                                        or course.times.time == i - 90
                                    )
                                    and len(content) > 30
                                    and course.isattime(days[1][j], i - 1)
                                ):
                                    found = True
                                    if len(content) < 45:
                                        if course.times.length < 80:
                                            line += content[30:] + " " * (
                                                45 - len(content)
                                            )
                                        if course.times.length == 80:
                                            line += content[30:] + "_" * (
                                                45 - len(content)
                                            )
                                        elif course.times.length > 80:
                                            line += content[30:] + " " * (
                                                45 - len(content)
                                            )
                                    else:
                                        line += content[30:45]
                                    line += "|"
                                elif (
                                    days[1][j] in course.times.days
                                    and (
                                        course.times.time == i - 50
                                        or course.times.time == i - 90
                                    )
                                    and course.isattime(days[1][j], i - 1)
                                ):
                                    found = True
                                    line += ("_" * 15) + "|"
                                elif course.isattime(days[1][j], i + 1):
                                    found = True
                                    line += (" " * 15) + "|"
                            if not found:
                                line += "_______________|"
                    if line != "":
                        print(line)
            case "notes":
                print("Schedule:")
                for i in range(len(days[0])):
                    print("\n" + days[0][i] + ":")
                    for course in sorted(self.courses, key=getTime):
                        if days[1][i] in course.times.days:
                            args = [
                                "- ",
                                miltoreadable(course.times.time),
                                "-",
                                miltoreadable(
                                    course.times.time
                                    + minutes2hours(course.times.length)
                                ),
                                " ",
                                course.title,
                                " ",
                                course.type,
                                " ",
                                course.room,
                            ]
                            text = "".join(args)
                            if course.times.biweekly == 1:
                                text += " (odd weeks)"
                            elif course.times.biweekly == 2:
                                text += " (even weeks)"
                            print(text)
            case _:
                for course in self.courses:
                    print("\t", course)

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

def minutes2hours(minutes:int):
    """
    Takes number of minutes and returns int with last 2 digits as minutes and all other digits as hours (e.g. 150->230 (2 hours 30 minutes))
    """
    return ((minutes // 60) * 100) + (minutes % 60)


def getTime(course):
    """
    extract time from course, used to sort by time
    """
    return course.times.time


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
    window: pygame.Surface,
    text: str,
    color: str,
    x: int,
    y: int,
    size: int = 15,
    rot: int = 0,
):
    if size == 15:
        txt = text_font.render(text, True, color)
    elif size == 30:
        txt = title_font.render(text, True, color)
    else:
        txt = big_font.render(text, True, color)
    txt = pygame.transform.rotate(txt, 360 - rot)
    txt_rect = txt.get_rect()
    txt_rect.topleft = (x, y)
    window.blit(txt, txt_rect)


def makeTextCent(
    window: pygame.Surface,
    text: str,
    color: str,
    x: int,
    y: int,
    size: int = 15,
    rot: int = 0,
):
    if size == 15:
        txt = text_font.render(text, True, color)
    elif size == 30:
        txt = title_font.render(text, True, color)
    else:
        txt = big_font.render(text, True, color)
    txt = pygame.transform.rotate(txt, 360 - rot)
    txt_rect = txt.get_rect()
    txt_rect.center = (x, y)
    window.blit(txt, txt_rect)


def makeArcText(
    window: pygame.Surface,
    text: str,
    color: str,
    x: int,
    y: int,
    radius: int,
    startrad: int,
    endrad: int,
):
    startrad = math.pi / 2 - startrad
    endrad = math.pi / 2 - endrad
    arclength = (endrad - startrad) * radius
    if arclength < 0:
        arclength = ((endrad + 2 * math.pi) - startrad) * radius
    charactersfit = int(arclength / 10)
    if len(text) > charactersfit:
        text = text[:charactersfit]
    radinc = 10 / radius
    currad = startrad
    radius = radius - 12
    for i in range(len(text)):
        # print(text[i],end="")
        xpos = x + (radius * math.sin((currad + radinc / 2)))
        ypos = y - (radius * math.cos((currad + radinc / 2)))
        makeTextCent(
            window,
            text[i],
            color,
            xpos,
            ypos,
            30,
            (currad + radinc / 2) / math.pi * 180,
        )
        # print(f'{xpos = },{ypos = }')
        currad += radinc
    # print()


rooms = dict()
roomsJSON = []
campusmap = CampusMap(rooms)


def readRooms():
    """
    Reads dictionary of rooms and coordinates from "rooms.json"
    """
    global campusmap
    global roomsJSON
    filename = "rooms.json"
    with open(filename, "r") as f:
        roomsJSON = json.load(f)
        campusmap.rooms = roomsJSON[0]


allCourses = dict()
allCoursesJSON = []


def readCourses():
    """
    Reads list of courses from course file into dictionary of courses
    """
    global allCoursesJSON
    global allCourses
    allCoursesJSON = []
    allCourses = dict()
    # try:
    #     coursefile = coursefile
    # except:
    #     coursefile = "CourseFiles/Winter2025.json"
    print(coursefile)
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


def removeDupes():
    """
    Removes duplicate crns from allCourses list
    """
    global allCoursesJSON
    global allCourses
    allCoursesJSON = []
    for key in allCourses:
        course = allCourses[key]
        cJSON = {
            "crn": course.crn,
            "type": course.type,
            "section": course.section,
            "instructor": course.instructor,
            "maxpop": course.maxpop,
            "curpop": course.curpop,
            "code": course.code,
            "title": course.title,
            "room": course.room,
            "times": {
                "days": course.times.days,
                "time": course.times.time,
                "length": course.times.length,
                "biweekly": course.times.biweekly,
            },
        }
        allCoursesJSON.append(cJSON)
    with open(coursefile, "w") as f:
        json.dump(allCoursesJSON, f)


def longtoshortday(longday: str):
    """
    Takes full name of day of week and returns the letter code (first letter of day except thursday is R)
    """
    days = [
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        ["M", "T", "W", "R", "F"],
    ]
    result = days[1][days[0].index(longday)]
    return result


def lastIndexOf(str: str, target: str):
    # "randomStringingString"
    # "lastIndexOf(str)"
    # print(str[::-1].index(target[::-1]))
    # print(len(str)-str[::-1].index(target[::-1])-len(target))
    return len(str) - str[::-1].index(target[::-1]) - len(target)


def timerangetotimeandlength(timerange: str):
    """
    Takes a string of format '03:40 PM - 05:00 PM' and returns the start time and minute length (1540,80)
    """
    time = 0
    length = 0
    if len(timerange) < 10:
        return time, length
    timerange = timerange.replace(":", "")
    time = int(timerange[:4])
    if timerange[5] == "P" and time < 1200:
        time += 1200
    timerange = timerange[10:]
    time2 = int(timerange[:4])
    if timerange[5] == "P" and time2 < 1200:
        time2 += 1200
    hr1 = time // 100
    mn1 = time % 100
    hr2 = time2 // 100
    mn2 = time2 % 100
    hr = hr2 - hr1
    mn = mn2 - mn1
    if mn < 0:
        hr -= 1
        mn += 60
    length = mn + (60 * hr)
    return time, length


def fastestAddCourses(skip=False):
    """
    Allows you to continuously paste pages into the console without waiting for the previous to finish
    """
    line = " "
    content = []
    if skip:
        content.append("Ontario Tech University")
    while line != "":
        try:
            # if line[:4] == "BIOL":
            #     print(line.count("\t"))
            if line[-8:] == "Per Page":
                input(":")
                # input(":")
                break
            line = input(":")
            if line.count("\t") == 6 or line.count("\t") == 7:
                line = "?" + line
            content.append(line)
        except:
            print(line)
            exit()
    # for lein in content:
    #     if (lein.count("\t") > 0 and (lein.count("\t") != 6 and lein.count("\t") != 7)):
    #         print(lein)
    #         print(lein.count("\t"))
    content = "\n".join(content)
    index = content.index("Status")
    content = content[index + 8 :]
    totals = content.split("?")
    for total in totals:
        if len(total) > 20:
            hasIntructor = False
            if total.count("(Primary)") > 0:
                hasIntructor = True
            biweekly = 0
            if total.count("Building:") > 3:
                biweekly = 1
            try:
                index = total.index("\t")
            except:
                continue
            code = total[:index]
            # ex. "BIOL"
            total = total[index + 1 :]
            index = total.index("\t")
            code += total[:index]
            # "BIOL"+"1020U"
            total = total[index + 1 :]

            index = total.index("\t")
            title = total[:index]
            # "Biology II"
            total = total[index + 1 :]

            index = total.index("\t")
            coursetype = total[:index]
            # "Lecture"
            total = total[index + 1 :]

            index = total.index("\t")
            section = total[:index]
            # 1
            # Section sometimes has an "A" or similar at the start
            if section.isnumeric():
                section = int(section)
            elif section[1:].isnumeric():
                section = int(section[1:])
            else:
                section = int(section[2:])
            total = total[index + 1 :]

            index = total.index("\t")
            crn = int(total[:index])
            # 70001
            total = total[index + 1 :]

            myArr = []
            if hasIntructor:
                while total.split("\n")[0].count(", ") > 0:
                    index = total.index("\n")
                    temp = total[:index]
                    if temp.count("Primary") != 0:
                        temp = temp[: temp.index(" (Primary)")]
                    myArr.append(temp)
                    total = total[index + 1 :]
            else:
                total = total[2:]

            days = []
            if len(total) <= 30:
                time, length = 0, 0
                room = "None"
            else:
                sidetotal = total
                i = 0
                while biweekly != 1:
                    i += 1
                    try:
                        index = sidetotal.index("\nS")
                    except:
                        break
                    try:
                        days.append(longtoshortday(sidetotal[:index]))
                    except:
                        break
                    try:
                        index = sidetotal.index("Start Date:")
                    except:
                        break
                    sidetotal = sidetotal[index + 44 :]
                if biweekly == 1:
                    index = total.index("\n")
                    days = [longtoshortday(total[:index])]
                index = total.index("F\nS\n")
                total = total[index + 4 :]

                index = total.index("Type:")
                time, length = timerangetotimeandlength(total[: index - 1])
                # 1710, 80
                index = total.index("g:")
                total = total[index + 3 :]

                index = total.index("Room:")
                stuff = total[: index - 1]
                room = ""
                # match stuff:
                #     case "Software and Informatics Resea":
                #         room += "SIR"
                #     case "Shawenjigewining Hall":
                #         room += "SHA"
                #     case _:
                #         pass
                total = total[index + 6 :]

                # index = lastIndexOf(total,"Start")
                index = total.index("Start")
                if biweekly == 0:
                    index = total.index("Start")
                room += total[: index - 1]
                # "SIR"+"2060" || ""+"SCI1350"
                index = lastIndexOf(total, "Start")
                total = total[index + 44 :]
            if total.count("FULL:") != 0:
                total = total[6:]
            index = total.index(" of ")
            index1 = total.index(" seats remain")
            curpop = int(total[:index])
            maxpop = int(total[index + 4 : index1])
            curpop = maxpop - curpop
            courseJSON = {
                "crn": crn,
                "type": coursetype,
                "section": section,
                "instructor": myArr,
                "maxpop": maxpop,
                "curpop": curpop,
                "code": code,
                "title": title,
                "room": room,
                "times": {
                    "days": days,
                    "time": time,
                    "length": length,
                    "biweekly": biweekly,
                },
            }
            course_time = CourseTime(days, time, length, biweekly)
            course = Course(
                title,
                room,
                crn,
                coursetype,
                code,
                course_time,
                section,
                myArr,
                maxpop,
                curpop,
            )
            allCoursesJSON.append(courseJSON)
            allCourses[crn] = course
            # print(course.fullDetail())
            # print("-" * 100)

            with open(coursefile, "w") as f:
                json.dump(allCoursesJSON, f)
            # exit()


def fastAddCourses():
    """
    Takes a page of courses into the saved courses
    (No longer used)
    """
    while True:
        line = " "
        content = []
        while line != "":
            line = input(":")
            content.append(line)
        biweekly = 0
        if len(content) > 25:
            biweekly = 1
        total = "\n".join(content)
        index = total.index("	")
        code = total[:index]
        total = total[index + 1 :]
        index = total.index("	")
        code += total[:index]
        total = total[index + 1 :]

        index = total.index("\n")
        title = total[:index]
        total = total[index + 1 :]

        index = total.index("	")
        coursetype = total[:index]
        total = total[index + 1 :]

        index = total.index("	")
        section = int(total[:index])
        total = total[index + 1 :]

        index = total.index("\n")
        crn = int(total[:index])
        total = total[index + 1 :]

        days = []
        sidetotal = total
        i = 0
        while biweekly != 1:
            i += 1
            try:
                index = sidetotal.index("\nS")
            except:
                break
            days.append(longtoshortday(sidetotal[:index]))
            try:
                index = sidetotal.index("End Date:")
            except:
                break
            sidetotal = sidetotal[index + 21 :]
        if biweekly == 1:
            days = index = total.index("\n")
            days = [longtoshortday(total[:index])]
        index = total.index("F\nS\n")
        total = total[index + 4 :]

        index = total.index("Type:")
        time, length = timerangetotimeandlength(total[: index - 1])
        index = total.index("g:")
        total = total[index + 3 :]

        index = total.index("Room:")
        stuff = total[: index - 1]
        room = ""
        # match stuff:
        #     case "Software and Informatics Resea":
        #         room += "SIR"
        #     case "Shawenjigewining Hall":
        #         room += "SHA"
        #     case _:
        #         pass
        total = total[index + 6 :]

        index = total.index("Start")
        room += total[: index - 1]
        courseJSON = {
            "crn": crn,
            "type": coursetype,
            "section": section,
            "code": code,
            "title": title,
            "room": room,
            "times": {
                "days": days,
                "time": time,
                "length": length,
                "biweekly": biweekly,
            },
        }
        course_time = CourseTime(days, time, length, biweekly)
        course = Course(title, room, crn, coursetype, code, course_time, section)
        allCoursesJSON.append(courseJSON)
        allCourses[crn] = course

        with open(coursefile, "w") as f:
            json.dump(allCoursesJSON, f)

        inp = input("Continue? Y/N: ")
        if inp != "":
            break


def addCourses():
    """
    Adds new courses to file and to allCourses dictionary of objects
    """
    while True:
        crn = input("CRN (Ex: 41929)('stop' to stop): ")
        if crn == "stop" or crn == "":
            break
        crn = int(crn)
        if crn in allCourses:
            print(f"Course {allCourses[crn]} already in list")
            continue
        coursetype = input("Type (Lecture Lab Tutorial): ")
        if coursetype.lower() == "l":
            coursetype = "Lecture"
        elif coursetype.lower() == "b":
            coursetype = "Lab"
        elif coursetype.lower() == "t":
            coursetype = "Tutorial"
        section = int(input("Section (1-999): "))
        code = input("Course code (Ex: CSCI1030U): ")
        title = input("Course title (Ex: Intro to Computer Science): ")
        inp = input("Days (M T W R F) ('stop' to stop): ")
        days = []
        while inp != "stop" and inp != "":
            days.append(inp)
            inp = input("Days (M T W R F) ('stop' to stop): ")
        time = int(input("Time (0000-2400): "))
        length = int(input("Length in minutes (80 170): "))
        room = input("Room (Ex: SCI1350): ")
        biweekly = int(input("Biweekly? (0 1 2)"))
        instructor = []
        while inp != "stop" and inp != "":
            instructor.append(inp)
            inp = input("Instructor(s): ")
        maxpop = input("Max capacity")
        curpop = input("Current capacity")
        courseJSON = {
            "crn": crn,
            "type": coursetype,
            "section": section,
            "code": code,
            "title": title,
            "room": room,
            "times": {
                "days": days,
                "time": time,
                "length": length,
                "biweekly": biweekly,
            },
            "instructor": instructor,
            "maxpop":maxpop,
            "curpop":curpop,
        }
        course_time = CourseTime(days, time, length, biweekly)
        course = Course(title, room, crn, coursetype, code, course_time, section, instructor, maxpop, curpop)
        allCoursesJSON.append(courseJSON)
        allCourses[crn] = course

    with open(coursefile, "w") as f:
        json.dump(allCoursesJSON, f)


savedschedules = dict()
savedschedulesJSON = []


def readSchedules():
    """
    Fills savedschedulesJSON and savedschedules with content from Schedules.json
    """
    global savedschedulesJSON
    with open("Schedules.json", "r") as f:
        savedschedulesJSON = json.load(f)
        for schedule in savedschedulesJSON:
            name = schedule["name"]
            courses = []
            for crn in schedule["crns"]:
                if crn in allCourses:
                    courses.append(allCourses[crn])
            temp = Schedule(courses, name)
            if len(temp.crns) == 0:
                continue
            temp.calcscore()
            savedschedules[name] = temp

if __name__=="__main__":
    if coursefile == "Winter2024.json":
        datas = [
            [70154, 70155, 70167, 70851, 75638],
            [
                70156,
                70157,
                70158,
                70159,
                70160,
                70161,
                70162,
                70163,
                70164,
                70165,
                70166,
                70168,
                70169,
                70170,
                70171,
                70172,
                70852,
                71950,
                71951,
                72278,
                72660,
                72676,
                72865,
                72866,
                72867,
                72868,
                73689,
                75640,
                75641,
                75642,
                75643,
                75644,
            ],
            [72642, 75155, 75156, 75510],
            [
                72670,
                72671,
                72672,
                73009,
                73776,
                73922,
                74534,
                74868,
                74894,
                74895,
                75459,
                75511,
                75512,
            ],
            [71974, 75332],
            [70197, 70198, 72883, 73014],
            [
                70199,
                70200,
                70201,
                70202,
                70203,
                70204,
                70205,
                70206,
                70207,
                71906,
                71907,
                71908,
                71909,
                71910,
                71911,
                71912,
                71913,
                71914,
                71915,
                71916,
                71941,
                71966,
                72277,
                72876,
                72877,
                72878,
                72879,
                72880,
                72881,
                72882,
                73015,
                73016,
                73017,
                73018,
                73019,
                73020,
                75575,
                75576,
                75646,
                75647,
                75648,
                75649,
                75651,
                75653,
                75654,
                75655,
                75656,
            ],
            [
                70208,
                70209,
                70210,
                70211,
                70212,
                70213,
                70214,
                70215,
                70855,
                70856,
                72393,
                72394,
                72395,
                72396,
                72397,
                72884,
                72885,
                72886,
                72887,
                72888,
                73021,
                73022,
                73023,
                73024,
                75574,
                75577,
                75578,
                75657,
                75658,
                75659,
                75660,
            ],
            [73772, 74360, 75188],
            [73773, 73774, 73775, 73921, 74361, 74439, 74606, 74888, 75218, 75219, 75449],
        ]
    elif coursefile == "Fall2023.json":
        datas = [
            [40288, 40289, 40290, 40291, 45633],
            [
                40292,
                40293,
                40294,
                40295,
                40296,
                40297,
                40298,
                40299,
                40300,
                40301,
                40302,
                40303,
                40304,
                40305,
                40306,
                40308,
                40309,
                40310,
                41560,
                41576,
                41964,
                42002,
                42003,
                42958,
                42959,
                42960,
                42961,
                45708,
                45709,
                45710,
                45711,
            ],
            [42684, 42942, 44933],
            [
                42685,
                42686,
                42687,
                42688,
                42943,
                42944,
                42945,
                42946,
                42947,
                42948,
                45100,
                45101,
            ],
            [40363, 40364, 40365, 40366, 42035],
            [
                40367,
                40368,
                40369,
                40370,
                40371,
                40372,
                40373,
                40374,
                40375,
                40376,
                40377,
                40378,
                40379,
                40914,
                40915,
                41155,
                41156,
                41918,
                41920,
                41921,
                41922,
                41923,
                41924,
                41925,
                41926,
                41927,
                41928,
                41929,
                41930,
                41931,
                41970,
                41972,
                41973,
                41974,
                41976,
                42084,
                42334,
                42336,
                42337,
                42693,
                42695,
                45753,
                45754,
                45755,
                45756,
                45757,
                45758,
                45764,
            ],
            [
                40380,
                40381,
                40382,
                40383,
                41919,
                41975,
                41977,
                42335,
                42338,
                42339,
                42340,
                42702,
                42703,
                42704,
                42705,
                42969,
                42970,
                42971,
                42972,
                42973,
                42974,
                42975,
                42976,
                42977,
                42978,
                42979,
                43715,
                43879,
                43880,
                45759,
                45760,
                45761,
                45765,
            ],
            [43913, 44487, 45388],
            [
                43914,
                43915,
                43916,
                44108,
                44488,
                44572,
                44984,
                45102,
                45249,
                45250,
                45389,
                45390,
                45391,
                45628,
            ],
            [
                42752,
                42753,
                42754,
                42755,
                42756,
                42757,
                42758,
                42759,
                42760,
                42761,
                42762,
                42763,
                42764,
                42765,
                42766,
                42767,
                42768,
                43976,
                45630,
                45773,
            ],
        ]
    elif coursefile == "Fall2024_old.json" or coursefile == "Fall2024.json":
        datas = [
            [42730],
            [42731],
            [40241, 44934],
            [44758, 44759, 45823, 45824],
            [40245, 45941],
            [40246, 40250, 45822, 45944],
            [40311, 40313, 43713],
            [
                40316,
                40317,
                40320,
                40321,
                40322,
                40912,
                42962,
                42963,
                42964,
                42965,
                43142,
                43714,
                43786,
                43878,
            ],
            [40410],
            [45203],
        ]  # [45969]]#
    elif coursefile == "Winter2025.json":
        datas = [
            [75153],
            [74892],
            [75425],
            [74365],
            [75797],
            [73778, 75704, 75799],
            [72869],
            [72870],
            [70175],
            [75043],
        ]
        # datas = [
        #     [70120, 75153],
        #     [70121, 72305, 74362, 74363, 74529, 74530, 74531, 74892],
        #     [72850, 75425],
        #     [72851, 72852, 74364, 74365, 74532, 74533, 74893, 75186],
        #     [73777, 75797],
        #     [73778, 73779, 74366, 74535, 74536, 74869, 75704, 75798, 75799],
        #     [72869],
        #     [72870],
        #     [70175],
        #     [75043],
        # ]
        # datas = [
        #     [75153],
        #     [70121, 74362, 74531, 74892],
        #     [72850],
        #     [72852, 74364, 74365, 74532, 74533, 74893, 75186],
        #     [75797],
        #     [73778, 75704, 75798, 75799],
        #     [72869],
        #     [72870],
        #     [70175],
        #     [75043],
        # ]

    # , 43135, 45103, 45595, 45940


def LTLListfromCourse(code):
    """
    Takes a course code (e.g. CSCI2020U), and returns which section types it has as a list.

    e.g. [Lecture, Tutorial] or [Lecture] or [Lecture, Laboratory] etc...
    """
    # No clue what LTL stands for (love that list? left to left?) oh its probably lecture tutorial lab oh wait that means this function doesn't do what I thought.
    # I guess narrowSearch(functionalSearch("code",code)) does that other thing
    found = []
    for key in allCourses:
        c = allCourses[key]
        if c.code == code and not (c.type in found):
            found.append(c.type)
    return found


def generateSchedules():
    """
    Starts the process of generating schedules, first asking for course codes
    """
    inp = input("Number of Individual classes (usually ~10): ")
    set_of_all_options = []
    if inp != "":
        for i in range(int(inp)):
            code = input("Course code (Ex: CSCI2050U): ")
            for typ in LTLListfromCourse(code):
                # classType = input(
                #     "Course Type: (Should be one of: Lecture Tutorial Laboratory): "
                # )
                set_of_all_options.append(
                    narrowSearch(functionalSearch("code", code), "type", typ)
                )
    else:
        set_of_all_options = datas
    # print(set_of_all_options)
    optionstoschedules(set_of_all_options)


def trimOptions(options):
    """
    Removes course sections outside of preferred time range, input as part of the function
    """
    newoptions = []
    firsttime = 0
    lasttime = 2400
    while True:
        inp = input("Earliest Acceptable time (leave blank for no limit): ")
        if inp == "" or (0 <= int(inp) <= 2400):
            if inp != "":
                firsttime = int(inp)
            inp = input("Latest Acceptable time (leave blank for no limit): ")
            if inp == "":
                break
            elif 0 <= int(inp) <= 2400:
                lasttime = int(inp)
                break

    for i in range(len(options)):
        eachclass = options[i]
        newoptions.append([])
        for j in range(len(eachclass)):
            eachcrn = eachclass[j]
            course: Course = allCourses[eachcrn]
            if (
                (
                    course.times.time < firsttime or course.times.time > lasttime
                )  # course is outside of time range
                and course.code != "SCCO0999U"  # dont reject co-op success course
                and course.times.time
                != 0  # dont reject courses with time 0 (they're not actually at midnight)
            ):
                #### Conditions in which to reject course section
                continue
            else:
                newoptions[i].append(eachcrn)  # accept course otherwise
    return newoptions


def trimoptions(options, min, max):
    """
    Removes course sections outside of preferred time range min-max
    """
    newoptions = []
    firsttime = min
    lasttime = max

    for i in range(len(options)):
        eachclass = options[i]
        newoptions.append([])
        for j in range(len(eachclass)):
            eachcrn = eachclass[j]
            course: Course = allCourses[eachcrn]
            if (
                (
                    course.times.time < firsttime or course.times.time > lasttime
                )  # course is outside of time range
                and course.code != "SCCO0999U"  # dont reject co-op success course
                and course.times.time
                != 0  # dont reject courses with time 0 (they're not actually at midnight)
            ):
                #### Conditions in which to reject course section
                continue
            else:
                newoptions[i].append(eachcrn)  # accept course otherwise
    return newoptions


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
            result += f"{self.totalYears} Years, "
        if self.totalDays != 0:
            result += f"{self.remDays} Days, "
        if self.totalHours != 0:
            result += f"{self.remHours} Hours, "
        if self.totalMinutes != 0:
            result += f"{self.remMinutes} Minutes, "
        if self.totalSeconds != 0:
            result += f"{self.remSeconds} Seconds"
        return result


class date:
    def __init__(self, value):
        self.ms = value
        self.time = time.localtime(value)

    def __str__(self):
        result = f"{self.time.tm_hour}:{self.time.tm_min}:{self.time.tm_sec}"
        return result


all_valid_schedules_json = []


def optionstoschedules(set_of_options: list[list[str]]):
    """
    Terrible function that looks like it was made by a highschool computer science student who has something against recursion (it was :3)

    Takes an array of arrays of course sections, all of which are potential courses for the generated schedule

    Uses ~10 nested for loops, and if you want more/less classes than that, you have to go into the code and manually add/remove nested for loops.

    We _might_ want to use recursion for this one.

    Returns a list of schedule-score pairs, sorted by score-descending.
    """
    set_of_options = trimOptions(set_of_options)
    all_valid_schedules = []
    crnlist = []
    total = 1
    for eachclass in set_of_options:
        count = 0
        for eachcrn in eachclass:
            count += 1
        total = total * count
    print(total)
    completed = 0
    validcount = 0
    lastbatch = 0
    progress = 0
    absstarttime = (time.time() * 1000) // 1
    for crn0 in set_of_options[0]:
        for crn1 in set_of_options[1]:
            crnlist = [crn0, crn1]
            for i in range(len(crnlist)):
                crnlist[i] = allCourses[crnlist[i]]
            schedule = Schedule(crnlist)
            if not schedule.checkValid():
                completed += (
                    len(set_of_options[9])
                    * len(set_of_options[8])
                    * len(set_of_options[7])
                    * len(set_of_options[6])
                    * len(set_of_options[5])
                    * len(set_of_options[4])
                    * len(set_of_options[3])
                    * len(set_of_options[2])
                )
                continue
            for crn2 in set_of_options[2]:
                crnlist = [crn0, crn1, crn2]
                for i in range(len(crnlist)):
                    crnlist[i] = allCourses[crnlist[i]]
                schedule = Schedule(crnlist)
                if not schedule.checkValid():
                    completed += (
                        len(set_of_options[9])
                        * len(set_of_options[8])
                        * len(set_of_options[7])
                        * len(set_of_options[6])
                        * len(set_of_options[5])
                        * len(set_of_options[4])
                        * len(set_of_options[3])
                    )
                    continue
                for crn3 in set_of_options[3]:
                    crnlist = [crn0, crn1, crn2, crn3]
                    for i in range(len(crnlist)):
                        crnlist[i] = allCourses[crnlist[i]]
                    schedule = Schedule(crnlist)
                    if not schedule.checkValid():
                        completed += (
                            len(set_of_options[9])
                            * len(set_of_options[8])
                            * len(set_of_options[7])
                            * len(set_of_options[6])
                            * len(set_of_options[5])
                            * len(set_of_options[4])
                        )
                        continue
                    for crn4 in set_of_options[4]:
                        crnlist = [crn0, crn1, crn2, crn3, crn4]
                        for i in range(len(crnlist)):
                            crnlist[i] = allCourses[crnlist[i]]
                        schedule = Schedule(crnlist)
                        if not schedule.checkValid():
                            completed += (
                                len(set_of_options[9])
                                * len(set_of_options[8])
                                * len(set_of_options[7])
                                * len(set_of_options[6])
                                * len(set_of_options[5])
                            )
                            continue
                        for crn5 in set_of_options[5]:
                            crnlist = [crn0, crn1, crn2, crn3, crn4, crn5]
                            for i in range(len(crnlist)):
                                crnlist[i] = allCourses[crnlist[i]]
                            schedule = Schedule(crnlist)
                            if not schedule.checkValid():
                                completed += (
                                    len(set_of_options[9])
                                    * len(set_of_options[8])
                                    * len(set_of_options[7])
                                    * len(set_of_options[6])
                                )
                                continue
                            for crn6 in set_of_options[6]:
                                crnlist = [crn0, crn1, crn2, crn3, crn4, crn5, crn6]
                                for i in range(len(crnlist)):
                                    crnlist[i] = allCourses[crnlist[i]]
                                schedule = Schedule(crnlist)
                                if not schedule.checkValid():
                                    completed += (
                                        len(set_of_options[9])
                                        * len(set_of_options[8])
                                        * len(set_of_options[7])
                                    )
                                    continue
                                for crn7 in set_of_options[7]:
                                    crnlist = [
                                        crn0,
                                        crn1,
                                        crn2,
                                        crn3,
                                        crn4,
                                        crn5,
                                        crn6,
                                        crn7,
                                    ]
                                    for i in range(len(crnlist)):
                                        crnlist[i] = allCourses[crnlist[i]]
                                    schedule = Schedule(crnlist)
                                    if not schedule.checkValid():
                                        completed += len(set_of_options[9]) * len(
                                            set_of_options[8]
                                        )
                                        continue
                                    for crn8 in set_of_options[8]:
                                        crnlist = [
                                            crn0,
                                            crn1,
                                            crn2,
                                            crn3,
                                            crn4,
                                            crn5,
                                            crn6,
                                            crn7,
                                            crn8,
                                        ]
                                        for i in range(len(crnlist)):
                                            crnlist[i] = allCourses[crnlist[i]]
                                        schedule = Schedule(crnlist)
                                        if not schedule.checkValid():
                                            completed += len(set_of_options[9])
                                            continue
                                        for crn9 in set_of_options[9]:
                                            completed += 1
                                            crnlist = [
                                                crn0,
                                                crn1,
                                                crn2,
                                                crn3,
                                                crn4,
                                                crn5,
                                                crn6,
                                                crn7,
                                                crn8,
                                                crn9,
                                            ]
                                            for i in range(len(crnlist)):
                                                crnlist[i] = allCourses[crnlist[i]]
                                            schedule = Schedule(crnlist)
                                            if (
                                                schedule.checkValid()
                                            ):  # and schedule.lunchBreaks() == 5:
                                                validcount += 1
                                                all_valid_schedules.append(schedule)
                                                all_valid_schedules_json.append(
                                                    schedule.crns
                                                )
                                            scale = 10
                                            if (
                                                completed % math.ceil(total / scale)
                                                == 0
                                                or progress + 1
                                                < completed * scale / total
                                            ):
                                                progress = (
                                                    math.ceil(completed * scale / total)
                                                    - 1
                                                )
                                                if validcount > lastbatch:
                                                    try:
                                                        with open(
                                                            "outputfile.json", "w"
                                                        ) as f:
                                                            json.dump(
                                                                all_valid_schedules_json,
                                                                f,
                                                            )
                                                    except:
                                                        pass
                                                    lastbatch = validcount
                                                updt(
                                                    completed,
                                                    total,
                                                    validcount,
                                                    absstarttime,
                                                )
    with open("outputfile.json", "w") as f:
        json.dump(all_valid_schedules_json, f)
    print(len(all_valid_schedules) + " valid schedules")
    scored_list = []
    for i in range(
        len(all_valid_schedules)
    ):  # score all schedules (might be time consuming if calcscore has O(n^2+) efficiency)
        all_valid_schedules[i].calcscore()
        scored_list.append(all_valid_schedules[i])
    scored_list = sorted(scored_list, key=getscore, reverse=True)  # Sort by score
    presentSchedules(scored_list)
    return scored_list


def presentSchedules(scored_list: list[Schedule]):
    """
    Presents a list of schedules in the console, allowing the user to view only the first 6
    """
    for scored in scored_list[:6]:
        print(scored.display("timetable"))
    while True:
        inp = input("Enter a number (1-6) for details on that schedule: ")
        if inp.isnumeric() and (1 <= int(inp) <= 6):
            scored_list[int(inp) - 1].display("")
        elif inp == "":
            break
        else:
            print("number 1-6 pls")


def getscore(x: Schedule):
    """
    Used to sort scored_list in optionstoschedules()
    """
    return x.score


def updt(completed: int, total: int, validcount: int, absstarttime: int):
    """
    Print the progress through generating all very many schedules (realistically 10 billion at most)
    """
    if completed % (total // 100) == 0:
        elapsedtime = ((time.time() * 1000) // 1) - absstarttime
        remainingschedules = total - completed
        remainingTime = timeAmount(elapsedtime * total / completed - elapsedtime)
        eta = date(time.time() + remainingTime.totalSeconds)
        print(
            f"{math.ceil((completed*100)/total)}% done, {remainingschedules} schedules left! (estimated {remainingTime} remaining), Completed by {eta}"
        )
        print(
            (completed * 10000 // total) / 100,
            "% done with ",
            validcount,
            " valid and ",
            (completed - validcount),
            " invalid (",
            (validcount * 100 / completed),
            "% pass rate)\n",
            sep="",
        )


def makedatas():
    """
    Get list of needed courses from user in console, print list of course sections to the console.
    """
    inp = input("Number of Individual classes (usually ~10): ")
    set_of_all_options = []
    for i in range(int(inp)):
        code = input("Course code (Ex: CSCI2050U): ")
        for classType in LTLListfromCourse(code):
            # classType = input(
            #     "Course Type: (Should be one of: Lecture Tutorial Laboratory): "
            # )
            set_of_all_options.append(
                narrowSearch(functionalSearch("code", code), "type", classType)
            )
    print(set_of_all_options)


def launchDemo():
    print("Demo Launched")
    import scheduleGUI

def manualSchedule():
    """
    Asks user for individual crns to construct a schedule, no optimizing, no generating, no verifying.

    Saves the schedule to the schedule json file
    """
    global savedschedulesJSON
    readSchedules()
    inp = input("input all crns for schedule ('stop' to stop): ")
    courses = []
    while inp != "stop" and inp != "":
        if not inp.isnumeric():
            print("Crns must be numbers")
            inp = input("input all crns for schedule ('stop' to stop): ")
            continue
        inp = int(inp)
        if inp in allCourses:
            courses.append(allCourses[inp])
        else:
            print("CRN " + inp + " matches no known course.")
        inp = input("input all crns for schedule ('stop' to stop): ")
    name = input("Choose a name for your schedule")
    sched = Schedule(courses, name)
    temp = []
    for i in range(len(sched.courses)):
        temp.append(sched.courses[i].crn)
    scheduleJSON = {"crns": temp, "name": name}
    savedschedules[name] = sched
    savedschedulesJSON.append(scheduleJSON)
    with open("Schedules.json", "w") as f:
        json.dump(savedschedulesJSON, f)


def lookupCourse():
    """
    Search for a singular class by crn, output all details for this class
    """
    while True:
        inp = input("Enter CRN (ex: 41935): ")
        if not inp.isnumeric():
            print("You must enter a number")
            continue
        inp = int(inp)
        if not inp in allCourses:
            print("crn " + str(inp) + " not found")
            continue
        for field in allCourses[inp].__dict__.keys():
            print("\t" + field + ": " + str(allCourses[inp].get(field)))
            if field == "times":
                for ffield in allCourses[inp].get(field).__dict__.keys():
                    print("\t\t" + ffield + ": " + str(allCourses[inp].get(ffield)))
        # print(allCourses[inp].fullDetail())
        break


def functionalSearch(field: str, target):
    """
    Returns a list of all courses whose 'field' match 'target'
    """
    results = []
    resultcount = 0
    for key in allCourses:
        course: Course = allCourses[key]
        if (
            field.lower() == "day"
            and longtoshortday(target.lower().capitalize()) in course.times.days
        ) or str(course.get(field)).count(target) > 0:
            resultcount += 1
            results.append(course.crn)
    if resultcount == 0:
        print("No matches :(")
        return []
    else:
        return results


def narrowSearch(crns, field, target):
    """
    Filters a list of crns to those whose 'field' match 'target'
    """
    results = []
    resultcount = 0
    for crn in crns:
        course: Course = allCourses[crn]
        if (
            field.lower() == "day"
            and longtoshortday(target.lower().capitalize()) in course.times.days
        ) or str(course.get(field)).count(target) > 0:
            resultcount += 1
            results.append(course.crn)
    if resultcount == 0:
        print("No matches :(")
    else:
        return results


def fieldSearch():
    subset = allCourses
    while True:
        print("What would you like to search by?")
        inp = input(":")
        if inp == "":
            break
        target = input(f"what {inp} would you like to search for?")
        results = 0
        back = subset
        subset = dict()
        invert = False
        if target[0] == "!" or target[0] == "~":
            target = target[1:]
            invert = True
        for key in back:
            course: Course = allCourses[key]
            if (
                inp.lower() == "day"
                and longtoshortday(target.lower().capitalize()) in course.times.days
            ) or str(course.get(inp)).count(target) > 0:
                if not invert:
                    results += 1
                    subset[course.crn] = course
                    print(course)
            else:
                if invert:
                    results += 1
                    subset[course.crn] = course
                    print(course)
        if results == 0:
            print("No matches :(")
            print("(you can continue your search from the previous results though)")
            subset = back


def schedulemenu():
    readSchedules()
    while True:
        print("\n\n")
        print("1. Read schedules from file")
        print("2. Build new schedule")
        print("3. Display schedule")
        print("4. List schedules")
        print("5. Output possible crns list")
        print("6. Generate Schedules")
        print("7. Back")
        inp = input("Make a Selection: ")
        if not inp.isnumeric():
            print("input must be a number")
            continue
        else:
            inp = int(inp)
        match inp:
            case 1:
                readSchedules()
            case 2:
                manualSchedule()
            case 3:
                for key in savedschedules:
                    print(savedschedules[key])
                inp1 = input("Make a Selection: ")
                inp2 = input("choose display type ('timetable' 'notes' 'window' 'map'): ")
                if inp1 in savedschedules:
                    savedschedules[inp1].display(inp2)
                else:
                    print("No timetable exists with name", inp1)
            case 4:
                for key in savedschedules:
                    if (savedschedules[key].checkValid()):
                        print(str(savedschedules[key]))
            case 5:
                makedatas()
            case 6:
                generateSchedules()
            case 7:
                break
            case _:
                print("invalid choice")


def mapmenu():
    while True:
        print("\n\n")
        print("1. Show a Course location on a map")
        print("2. Cycle through several courses on the map")
        print("3. Show all Courses currently running")
        print("4. Back")
        inp = inp = input("Make a Selection: ")
        if not inp.isnumeric():
            print("input must be a number")
            continue
        else:
            inp = int(inp)
        match inp:
            case 1:
                crn = input("Enter CRN (ex: 41935): ")
                if not crn.isnumeric():
                    print("You must enter a number")
                    continue
                crn = int(crn)
                if crn in allCourses:
                    campusmap.display(crn)
            case 2:
                mylist = [70021, 73308]
                for crn in mylist:
                    campusmap.display(crn)
                    pygame.time.delay(500)
            case 3:
                running = []
                day = input("Day:")
                if day not in ["now", "M", "T", "W", "R", "F", "S"]:
                    print("invalid day")
                    continue
                time = 0
                if day != "now":
                    time = input("Time:")
                    if not time.isnumeric():
                        print("Time must be a number")
                        continue
                    time = int(time)
                    if not 0 <= time < 2359:
                        print("Time must be 0000-2400")
                        continue
                else:
                    days = ["M", "T", "W", "R", "F", "S", "S"]
                    current_datetime = datetime.now()
                    day = days[current_datetime.weekday()]
                    time = int(
                        f"{str(current_datetime)[11:13]}{str(current_datetime)[14:16]}"
                    )
                for crn in allCourses:
                    course: Course = allCourses[crn]
                    if course.isattime(day, time):
                        running.append(course.crn)
                campusmap.displaylist(running)
            case 4:
                break
            case _:
                print("invalid choice")


def searchmenu():
    while True:
        print("\n\n")
        print("1. Lookup course by crn")
        print("2. Search by field")
        print("3. List all Courses")
        print("4. Exit")
        inp = input("Make a Selection: ")
        if not inp.isnumeric():
            print("input must be a number")
            continue
        else:
            inp = int(inp)
        match inp:
            case 1:
                lookupCourse()
            case 2:
                fieldSearch()
            case 3:
                for key in allCourses:
                    print(allCourses[key])
                print(str(len(allCourses)) + " courses")
            case 4:
                break
            case _:
                print("invalid choice")


def courseAddingMenu():
    while True:
        print("\n\n")
        print("1. Add courses manually (input each field)")
        print("2. Add courses by page")
        print("3. Exit")
        inp = input("Make a Selection: ")
        if inp[-23:] == "Ontario Tech University":
            fastestAddCourses(True)
            continue
        if not inp.isnumeric():
            print("input must be a number")
            continue
        else:
            inp = int(inp)
        match inp:
            case 1:
                addCourses()
            case 2:
                fastestAddCourses()
            case 3:
                break
            case _:
                print("invalid choice")



def main():
    global coursefile
    pygame.init()
    global title_font
    global text_font
    global big_font
    title_font = pygame.font.SysFont("Lucida Console", 15)
    text_font = pygame.font.SysFont("Lucida Console", 10)
    big_font = pygame.font.SysFont("Lucida Console", 30)
    coursefile = ""
    files = []
    for f in os.listdir("CourseFiles"):
        files.append(f)
        print(f, end=" ")
    print()

    while True:
        inp = input("Course File Name: ")
        if inp in files:
            coursefile = inp
            break
        if inp == "":
            coursefile = "Winter2025.json"
            break
        if inp[-5:] != ".json":
            inp += ".json"
        if inp[1].isnumeric():
            match inp[0]:
                case "S":
                    inp = "Summer" + inp[1:]
                case "F":
                    inp = "Fall" + inp[1:]
                case "W":
                    inp = "Winter" + inp[1:]
                case _:
                    continue
            if inp.count("20") == 0:
                x = firstNumIndex(inp)
                inp = inp[:x] + "20" + inp[x:]
        if inp in files:
            coursefile = inp
            break

    coursefile = "CourseFiles/" + coursefile

    readCourses()
    readRooms()
    readSchedules()
    while True:
        print("\n\n")
        print("1. Add Courses")
        print("2. Maps")
        print("3. Schedules")
        print("4. Search courses")
        print("5. Launch demo")
        print("6. Exit")
        inp = input("Make a Selection: ")
        if not inp.isnumeric():
            print("input must be a number")
            continue
        else:
            inp = int(inp)
        match inp:
            case 1:
                courseAddingMenu()
            case 2:
                mapmenu()
            case 3:
                schedulemenu()
            case 4:
                searchmenu()
            case 5:
                launchDemo()
            case 6:
                break
            case 7:
                removeDupes()
            case _:
                print("invalid choice")

if __name__ == "__main__":
    main()