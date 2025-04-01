import math
import time

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

allCourses:dict[int,Course] = dict()

class Schedule:
    def __init__(self, courses: list[Course], name: str = "Untitled Schedule"):
        if len(courses)>0 and type(courses[0])==int:
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

def narrowSearch(crns:list[int], field:str, target):
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

def trimdatas(set_of_ops:list[list[int]]):
    new_ops:list[list[int]] = []
    specialcourses:list[Course] = []
    for i in range(len(set_of_ops)):
        if len(set_of_ops[i]) == 1:
            specialcourses.append(allCourses[set_of_ops[i][0]])
    for i in range(len(set_of_ops)):
        new_ops.append([])
        if len(set_of_ops[i]) != 1:
            for j in range(len(set_of_ops[i])):
                curcourse = allCourses[set_of_ops[i][j]]
                passes = True
                for specialcourse in specialcourses:
                    if curcourse.overlap(specialcourse): passes = False
                if passes: new_ops[i].append(set_of_ops[i][j])
        else:
            new_ops[i] = [set_of_ops[i][0]]
    return new_ops

def makedatas(courses:list[str],allCourses1:dict[int,Course],remcrns:list[int]):
    """
    Get list of needed classes from list of courses
    """
    global allCourses
    allCourses = allCourses1
    set_of_all_options = []
    for code in courses:
        for classType in LTLListfromCourse(code,allCourses1):
            set_of_all_options.append(narrowSearch(functionalSearch("code", code), "type", classType))
    newoptions:list[list[int]] = []
    for i in range(len(set_of_all_options)):
        newoptions.append([])
        for eachcrn in set_of_all_options[i]:
            if not eachcrn in remcrns:
                newoptions[i].append(eachcrn)
    newoptions = trimdatas(newoptions)
    return newoptions

def LTLListfromCourse(code,allCourses):
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
    
def prod(arr:list,i0:int,n:int=-1):
    result = 1
    if n==-1:
        n = len(arr)
    for i in range(i0,n):
        result *= arr[i]
    return result

def splitPath(str:str):
    if (len(str)%5!=0):
        print(str)
    result:list[int] = []
    for i in range(len(str)//5):
        result.append(int(str[:5]))
        str = str[5:]
    return result

all_valid_schedules:list[Schedule] = []
completedCount = 0
validCount = 0
fullcount = 0
total = 1
datas:list[list[int]] = []
datalengths:list[int] = []

def recursiveSchedules(currentPath:str,nextIndex:int):
    global completedCount
    global validCount
    global fullcount
    if nextIndex >= len(datas):
        completedCount+=1
        thissched = Schedule(splitPath(currentPath))
        if thissched.checkValid(): 
            validCount+=1
            all_valid_schedules.append(thissched)
        if thissched.checkFull(): fullcount+=1
        return
    for nextcrn in datas[nextIndex]:
        nextSchedule:Schedule = Schedule(splitPath(currentPath+str(nextcrn)))
        if nextSchedule.checkValid():
            recursiveSchedules(currentPath+str(nextcrn),nextIndex+1)
        else:
            completedCount+=prod(datalengths,nextIndex+1,len(datas))

def betteroptionstoschedules(set_of_options: list[list[int]]):
    """
    Takes an array of arrays of crns (datas), all of which are potential courses for the generated schedule

    Returns a list of valid schedules.
    """
    global total
    global datalengths
    global datas
    global all_valid_schedules
    global absstarttime
    all_valid_schedules = []
    datas = set_of_options
    total = 1
    for eachclass in set_of_options:
        total *= len(eachclass)
        datalengths.append(len(eachclass))
    if total == 0:
        return [],0
    print(str(total) + "Schedules to be processed")
    
    absstarttime = math.floor(time.time() * 1000)
    for crn0 in set_of_options[0]:
        recursiveSchedules(str(crn0),1)
    
    print(str(completedCount) + "Schedules processed in "+str((math.floor(time.time()*1000)-absstarttime))+" Ms")
    return all_valid_schedules, (math.floor(time.time()*1000)-absstarttime)/1000