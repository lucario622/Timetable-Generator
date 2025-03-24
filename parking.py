import json
import math
import pygame
from pygame.locals import *
from datetime import datetime
import time

pygame.init()

WIDTH = 1920
HEIGHT = 1080

coursefile = ""
files = [
    "pFall2023.json",
    "pWinter2024.json",
    "pSummer2024.json",
    "pFall2024.json",
    "pFall2024_old.json",
    "pWinter2025.json",
    "pWinter2025_old.json",
]
while True:
    inp = input("Course File Name: ")
    if inp in files:
        coursefile = inp
        break
    if inp == "":
        coursefile = "pFall2024.json"
        break


WIDTH = 860
HEIGHT = 540

title_font = pygame.font.SysFont("Lucida Console", 15)
text_font = pygame.font.SysFont("Lucida Console", 10)
big_font = pygame.font.SysFont("Lucida Console", 30)

class CourseTime:
    def __init__(self, days: list, time: int, length: int, biweekly: int):
        self.days = days
        self.time = time
        self.length = length
        self.biweekly = biweekly

    def overlap(self, otherTime: object):
        for day in self.days:
            for otherday in otherTime.days:
                if day == otherday:
                    if (
                        self.time >= otherTime.time
                        and self.time <= otherTime.time + otherTime.length
                    ) or (
                        otherTime.time >= self.time
                        and otherTime.time <= self.time + self.length
                    ):
                        return True
        return False


class Course:
    def __init__(
        self, room: str, crn: int, times
    ):
        self.crn = crn
        self.room = room
        self.times = times

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
        return f"{self.crn}: At {self.times.time} on {self.times.days} for {self.times.length} minutes in room {self.room}"

    def overlap(self, otherCourse):
        return self.times.overlap(otherCourse.times)

    def get(self, query: str):
        match query.lower():
            case "room":
                return self.room
            case "crn":
                return self.crn
            case "days":
                return self.times.days
            case "time":
                return self.times.time
            case "length":
                return self.times.length
            case "biweekly":
                return self.times.biweekly
            case _:
                return ""

def minutes2hours(minutes):
    return ((minutes // 60) * 100) + (minutes % 60)


def getTime(course):
    return course.times.time


def miltoreadable(time: int):
    if time % 100 == 60:
        time += 40
    if time >= 1300:
        time -= 1200
    result = str(math.floor(time / 100)) + ":" + str(time)[-2:]
    return result


def makeText(window: object, text: str, color: str, x: int, y: int, size: int = 15, rot: int = 0):
    if size == 15:
        txt = text_font.render(text, True, color)
    elif size == 30:
        txt = title_font.render(text, True, color)
    else:
        txt = big_font.render(text, True, color)
    txt = pygame.transform.rotate(txt,360-rot)
    txt_rect = txt.get_rect()
    txt_rect.topleft = (x, y)
    window.blit(txt, txt_rect)

def makeTextCent(window: object, text: str, color: str, x: int, y: int, size: int = 15, rot: int = 0):
    if size == 15:
        txt = text_font.render(text, True, color)
    elif size == 30:
        txt = title_font.render(text, True, color)
    else:
        txt = big_font.render(text, True, color)
    txt = pygame.transform.rotate(txt,360-rot)
    txt_rect = txt.get_rect()
    txt_rect.center = (x, y)
    window.blit(txt, txt_rect)

allCourses = dict()
allCoursesJSON = []


def readCourses():
    """
    Reads list of objects from file into dictionary of objects
    """
    global allCoursesJSON
    global allCourses
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
            course["room"],
            course["crn"],
            temptimes
        )
        allCourses[crn] = temp
    allCourses = dict(sorted(allCourses.items()))

def longtoshortday(longday):
    days = [
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        ["M", "T", "W", "R", "F"],
    ]
    result = days[1][days[0].index(longday)]
    return result


def timerangetotimeandlength(timerange):
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


def fastestAddCourses(skip = False):
    line = " "
    content = []
    if skip: content.append("Ontario Tech University")
    while line != "":
        if line[-8:] == "Per Page":
            input(":")
            # input(":")
            break
        line = input(":")
        if line.count("\t") == 2:
            line = "?" + line
        content.append(line)
    content = "\n".join(content)
    index = content.index("Sections	\n")
    content = content[index + 10 :]
    totals = content.split("?")
    for total in totals:
        if len(total) > 20:
            biweekly = 0
            if len(total) > 400:
                biweekly = 1
            try:
                index = total.index("	")
            except:
                continue
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
            section = total[:index]
            if section.isnumeric():
                section = int(section)
            elif section[1:].isnumeric():
                section = int(section[1:])
            else:
                section = int(section[2:])
            total = total[index + 1 :]

            index = total.index("\n")
            crn = int(total[:index])
            total = total[index + 1 :]

            days = []
            if len(total) <= 12:
                time, length = 0,0
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
                match stuff:
                    case "Software and Informatics Resea":
                        room += "SIR"
                    case "Shawenjigewining Hall":
                        room += "SHA"
                    case _:
                        pass
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


def fastAddCourses():
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
        match stuff:
            case "Software and Informatics Resea":
                room += "SIR"
            case "Shawenjigewining Hall":
                room += "SHA"
            case _:
                pass
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
        room = input("Room (Ex: UA1350): ")
        biweekly = int(input("Biweekly? (0 1 2)"))
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

class date :
    def __init__(self,value):
        self.ms = value
        self.time = time.localtime(value)
    
    def __str__(self):
        result = f"{self.time.tm_hour}:{self.time.tm_min}:{self.time.tm_sec}"
        return result


def lookupCourse():
    while True:
        inp = input("Enter CRN (ex: 41935): ")
        if not inp.isnumeric():
            print("You must enter a number")
            continue
        inp = int(inp)
        if not inp in allCourses:
            print("crn " + str(inp) + " not found")
            continue
        print(allCourses[inp])
        break


def functionalSearch(field, target):
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
    else:
        return results


def narrowSearch(crns, field, target):
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


def searchmenu():
    while True:
        print("\n\n")
        print("1. Lookup course by crn")
        print("2. Search by field")
        print("3. Exit")
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
                break
            case _:
                print("invalid choice")


readCourses()
while True:
    print("\n\n")
    print("1. Read courses from file")
    print("2. Add courses manually")
    print("3. Add courses by page")
    print("4. Print list of courses")
    print("5. Search courses")
    print("6. Exit")
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
            readCourses()
        case 2:
            addCourses()
        case 3:
            fastestAddCourses()
        case 4:
            for key in allCourses:
                print(allCourses[key])
        case 5:
            searchmenu()
        case 6:
            break
        case _:
            print("invalid choice")