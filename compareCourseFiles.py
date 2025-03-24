import json

file1 = "CourseFiles/"+"Winter2025.json"
file2 = "CourseFiles/"+"Winter2025_old.json"

allCoursesJSON1 = []
allCoursesJSON2 = []
allCourses1 = dict()
allCourses2 = dict()

class Course:
    def __init__(
        self, title: str, room: str, crn: int, type: str, code: str, times, section: int
    ):
        self.title = title
        self.room = room
        self.crn = crn
        self.type = type
        self.code = code
        self.times = times
        self.section = section

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
        # print(f"comparing {self.crn} to {otherCourse.crn}")
        return self.times.overlap(otherCourse.times)

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
            
    def __eq__(self, value: object):
        if (self.title == value.title and
            self.room == value.room and
            self.crn == value.crn and
            self.type == value.type and
            self.code == value.code and
            self.section == value.section and
            self.times.days == value.times.days and
            self.times.time == value.times.time and
            self.times.length == value.times.length and
            self.times.biweekly == value.times.biweekly):
            return True
        return False

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

def minutes2hours(minutes):
    return ((minutes // 60) * 100) + (minutes % 60)
    
with open(file1, "r") as f:
    allCoursesJSON1 = json.load(f)
for course in allCoursesJSON1:
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
    )
    # if not (crn in allCourses):
    allCourses1[crn] = temp
with open(file2, "r") as f:
    allCoursesJSON2 = json.load(f)
for course in allCoursesJSON2:
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
    )
    # if not (crn in allCourses):
    allCourses2[crn] = temp
allCourses1 = dict(sorted(allCourses1.items()))
allCourses2 = dict(sorted(allCourses2.items()))

removedcount = 0
identicalcount = 0
changes = []
fields = ["title","room","crn","type","code","section","day","time","length","biweekly"]
for field in fields:
    changes.append([field,0])
changed = 0

for crn in allCourses1:
    course1 = allCourses1[crn]
    if not crn in allCourses2:
        removedcount += 1
        continue
    course2 = allCourses2[course1.crn]
    if course1 == course2:
        identicalcount += 1
        continue
    changed += 1
    if course1.title != course2.title:
        changes[0][1] += 1
    if course1.room != course2.room:
        changes[1][1] += 1
    if course1.crn != course2.crn:
        changes[2][1] += 1
    if course1.type != course2.type:
        changes[3][1] += 1
    if course1.code != course2.code:
        changes[4][1] += 1
    if course1.section != course2.section:
        changes[5][1] += 1
    if course1.times.days != course2.times.days:
        changes[6][1] += 1
    if course1.times.time != course2.times.time:
        changes[7][1] += 1
    if course1.times.length != course2.times.length:
        changes[8][1] += 1
    if course1.times.biweekly != course2.times.biweekly:
        changes[9][1] += 1

addedCount = 0

for crn in allCourses2:
    if not crn in allCourses1:
        addedCount += 1
        if addedCount < 10:
            print(allCourses2[crn])
        continue


print(f'{removedcount} courses were removed at some point')
print(f'{addedCount} courses were added at some point')
print(f'{identicalcount} courses were unchanged')
print(f'{changed} courses were modified at some point')
for each in changes:
    print(f'\t{each[1]} {each[0]}s were modified')