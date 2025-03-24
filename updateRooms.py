import json
import os

print("Make sure you are ready to input the image coordinates when prompted with a room")
coursefile = ""
files = []
for f in os.listdir("CourseFiles"):
    files.append(f)


def firstNumIndex(str: str):
    for i in range(len(str)):
        if str[i].isnumeric():
            return i


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

coursefile = "CourseFiles/"+coursefile

with open("rooms.json", "r") as f:
    roomsJSON = json.load(f)
    rooms = roomsJSON[0]

with open(coursefile, "r") as f:
    allCoursesJSON = json.load(f)


listofrooms = []
with open("rooms.txt", "w") as f:
    for course in allCoursesJSON:
        room = course["room"]
        if room in listofrooms:
            continue
        else:
            listofrooms.append(room)
    listofrooms.sort()
    for room in listofrooms:
        f.write(room + "\n")


try:
    for room in listofrooms:
        if room in rooms:
            continue
        else:
            inpx = input(f"{room} x: ")
            inpy = input(f"{room} y: ")
            if (
                inpx.isnumeric()
                and inpy.isnumeric()
                and 0 <= int(inpx) <= 1920
                and 0 <= int(inpy) <= 1080
            ):
                rooms[room] = [int(inpx), int(inpy)]
    with open("rooms.json", "w") as f:
        json.dump([rooms], f)
except:
    with open("rooms.json", "w") as f:
        json.dump([rooms], f)
