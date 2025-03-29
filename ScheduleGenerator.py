from datetime import date
import json
import math
import time

allCourses = dict()

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
        if type(courses[0])==int:
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
        
    # def __init__(self, crns: list[int], name: str = "Untitled Schedule"):
    #     self.crns = crns
    #     self.courses = []
    #     for crn in self.crns:
    #         self.courses.append(allCourses[crn]) # type: ignore
    #     self.name = name
    #     self.fullClasses = 0
    #     self.score = 0

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

    def display(self):
        for course in self.courses:
            print("\t", course)

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

def getscore(x):
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
        print(f"{math.ceil((completed*100)/total)}% done, {remainingschedules} schedules left! (estimated {remainingTime} remaining), Completed by {eta}")
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

def functionalSearch(field: str, target, allCourses:dict):
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

def narrowSearch(crns:list[int], field:str, target, allCourses:dict):
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

def makedatas(courses:list[str],allCourses1:dict,remcrns:list[int]):
    """
    Get list of needed classes from list of courses
    """
    global allCourses
    allCourses = allCourses1
    set_of_all_options = []
    for code in courses:
        for classType in LTLListfromCourse(code,allCourses1):
            set_of_all_options.append(narrowSearch(functionalSearch("code", code,allCourses1), "type", classType,allCourses1))
    newoptions:list[list[int]] = []
    for i in range(len(set_of_all_options)):
        newoptions.append([])
        for eachcrn in set_of_all_options[i]:
            if eachcrn in remcrns:
                pass
            else:
                newoptions[i].append(eachcrn)
            
    return newoptions

def trimOptions(options:list[list[int]], min:int, max:int, allCourses:dict):
    """
    Removes course sections outside of preferred time range min-max
    """
    newoptions:list[list[int]] = []
    firsttime = min
    lasttime = max

    for i in range(len(options)):
        eachclass:list[int] = options[i]
        newoptions.append([])
        for j in range(len(eachclass)):
            eachcrn = eachclass[j]
            course = allCourses[eachcrn]
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

def LTLListfromCourse(code,allCourses:dict):
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
    
def prod(arr:list,i0:int,n:int):
    result = 1
    for i in range(i0,n):
        result *= arr[i]
    return result

def Sigma(arr:list,i0:int,n:int):
    result = 0
    for i in range(i0,n):
        result += arr[i]
    return result
    
def optionstoschedules(set_of_options: list[list[str]], allCourses:dict):
    """
    Terrible function that looks like it was made by a highschool computer science student who has something against recursion (it was :3)

    Takes an array of arrays of crns (datas), all of which are potential courses for the generated schedule

    Uses ~10 nested for loops, and if you want more/less classes than that, you have to go into the code and manually add/remove nested for loops.

    We _might_ want to use recursion for this one.

    Returns a list of schedules, sorted by score-descending.
    """
    if len(set_of_options) != 10:
        return []
    set_of_options:list[list[int]] = trimOptions(set_of_options)
    all_valid_schedules:list[Schedule] = []
    crnlist:list[int] = []
    total = 1
    for eachclass in set_of_options:
        total *= len(eachclass)
    completed = 0
    validcount = 0
    invalidcount = 0
    fullcount = 0
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
                                            for i in range(len(crnlist)): # 
                                                crnlist[i] = allCourses[crnlist[i]]
                                            schedule = Schedule(crnlist)
                                            if (schedule.checkValid()): # Add to valid if valid
                                                validcount += 1
                                                all_valid_schedules.append(schedule)
                                            else:
                                                invalidcount += 1
    print(len(all_valid_schedules) + " valid schedules")
    scored_list:list[Schedule] = []
    for i in range(
        len(all_valid_schedules)
    ):  # score all schedules (might be time consuming if calcscore has O(n^2+) efficiency)
        all_valid_schedules[i].calcscore()
        scored_list.append(all_valid_schedules[i])
    scored_list = sorted(scored_list, key=getscore, reverse=True)  # Sort by score
    return scored_list

def betteroptionstoschedules(set_of_options: list[list[str]], allCourses:dict):
    """
    Takes an array of arrays of crns (datas), all of which are potential courses for the generated schedule

    Uses ~10 nested for loops, and if you want more/less classes than that, you have to go into the code and manually add/remove nested for loops.

    We _might_ want to use recursion for this one.

    Returns a list of schedules, sorted by score-descending.
    """
    all_valid_schedules:list[Schedule] = []
    crnlist:list[int] = []
    total = 1
    for eachclass in set_of_options:
        total *= len(eachclass)
    completed = 0
    validcount = 0
    invalidcount = 0
    fullcount = 0
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
                                            for i in range(len(crnlist)): # 
                                                crnlist[i] = allCourses[crnlist[i]]
                                            schedule = Schedule(crnlist)
                                            if (schedule.checkValid()): # Add to valid if valid
                                                validcount += 1
                                                all_valid_schedules.append(schedule)
                                            else:
                                                invalidcount += 1
    print(str(len(all_valid_schedules)) + " valid schedules")
    scored_list:list[Schedule] = []
    for i in range(
        len(all_valid_schedules)
    ):  # score all schedules (might be time consuming if calcscore has O(n^2+) efficiency)
        all_valid_schedules[i].calcscore()
        scored_list.append(all_valid_schedules[i])
    scored_list = sorted(scored_list, key=getscore, reverse=True)  # Sort by score
    return scored_list