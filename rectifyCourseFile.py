import os
import json

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

myJSON = []

with open("CourseFiles/" + coursefile, "r") as f:
    myJSON = json.load(f)

fields = ["curpop", "maxpop", "instructor"]
defaults = [0, 0, []]

alreadygood = True

for e in myJSON:
    for i in range(len(fields)):
        field = fields[i]
        default = defaults[i]
        if field in e.keys():
            continue
        alreadygood = False
        e[field] = default

if not alreadygood:
    print("Fixed "+coursefile)
    with open("CourseFiles/" + coursefile, "w") as f:
        json.dump(myJSON, f)
else:
    print(coursefile + " is already good vro, no need to fix it ")
