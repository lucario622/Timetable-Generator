const WIDTH = 1500;
const HEIGHT = 850;

var selector;
var sbmtbutton;
var jsoninputdiv;

var obj;
var allCourses;

files = [
  "Fall2023.json",
  "Winter2024.json",
  "Summer2024.json",
  "Fall2024.json",
  "Winter2025.json",
];
var coursefile = "";

class CampusMap {
  rooms = [];

  constructor(rooms) {
    this.rooms = rooms;
  }

  display(crn) {
    if (!(crn in allCourses)) {
      return 0;
    }
    let fullroom = obj[crn].room;
    const notrooms = [
      "None",
      "OFFSITE",
      "SYN",
      "GEORGI_1",
      "GEORGI_2",
      "GEORGI_3",
    ];
    if (notrooms.includes(fullroom)) {
      console.log("Cancelled due to uncool room");
      return 0;
    }
    if (!isNumeric(fullroom[fullroom.length - 1])) {
      console.log("Cancelled due to lack of number(?)");
      return 0;
    }
    let building = "";
    let floor = 1;
    let roomid = 0;
    for (let i in fullroom) {
      if (
        isNumeric(fullroom.substring(i)) ||
        (isNumeric(fullroom.substring(i + 1)) &&
          fullroom[i] == "B" &&
          fullroom.length - i == 4 &&
          fullroom[0] != "D")
      ) {
        console.log("thats alot of conditions");
        floor = fullroom[i];
        if (floor == "B") {
          floor = 0;
        }
        floor = parseInt(floor);
        building = fullroom.substring(0, i);
        break;
      }
    }
    let flname = findfile(building, floor);
    // suspended due to lack of file accessing ability
  }
}

var campusmap = new CampusMap([]);

class CourseTime {
  constructor(days, time, length, biweekly) {
    this.days = days;
    this.time = time;
    this.length = length;
    this.biweekly = biweekly;
  }

  overlap(otherTime) {
    for (let i in this.days) {
      let day = days[i];
      for (let j in otherTime.days) {
        otherday = otherTime[j];
        if (
          (this.time >= otherTime.time &&
            self.time <= otherTime.time + otherTime.length) ||
          (otherTime.time >= this.time &&
            otherTime.time <= this.time + self.length)
        ) {
          return true;
        }
      }
    }
    return false;
  }
}

class Course {
  constructor(title, room, crn, type, code, times, section) {
    this.title = title;
    this.room = room;
    this.crn = crn;
    this.type = type;
    this.code = code;
    this.times = times;
    this.section = section;
  }

  isattime(day, time) {
    if (this.times.days.includes(day)) {
      if (
        time >= this.times.time &&
        time <= this.times.time + minutes2hours(this.times.length)
      ) {
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  }

  isattimegen(time) {
    if (
      time >= this.times.time &&
      time <= this.times.time + minutes2hours(this.times.length)
    ) {
      return true;
    } else {
      return false;
    }
  }

  toString() {
    return (
      this.crn +
      ": " +
      this.code +
      "|" +
      this.title +
      " " +
      this.type +
      " Section " +
      this.section +
      ". Meets at " +
      this.times.time +
      " on " +
      this.times.days +
      " for " +
      this.times.length +
      " minutes in room " +
      this.room
    );
  }

  overlap(otherCourse) {
    return this.times.overlap(otherCourse.times);
  }

  get(query) {
    switch (query.toLowerCase()) {
      case "title":
        return this.title;
      case "room":
        return this.room;
      case "crn":
        return this.crn;
      case "type":
        return this.type;
      case "code":
        return this.code;
      case "days":
        return this.times.days;
      case "time":
        return this.times.time;
      case "length":
        return this.times.length;
      case "biweekly":
        return this.times.biweekly;
      default:
        return "";
    }
  }
}

class Schedule {
  constructor(courses, name) {
    this.courses = courses;
    let crns = [];
    for (let i in this.courses) {
      crns.push(this.courses[i].crn);
    }
    this.crns = crns;
    this.name = name;
    this.score = 0;
  }

  checkValid() {
    for (let i in this.courses) {
      let course = this.courses[i];
      for (let j in this.courses) {
        let course1 = this.courses[j];
        if (course == course1) {
          continue;
        }
        if (course.overlap(course1)) {
          return false;
        }
      }
    }
    return true;
  }

  calcscore() {
    this.daycount = 0;
    let counteddays = [0, 0, 0, 0, 0];
    const days = ["M", "T", "W", "R", "F"];
    for (let i in this.courses) {
      let course = this.courses[i];
      for (let j in days) {
        let day = days[j];
        if (course.times.days.includes(day)) {
          counteddays[days.indexOf(day)] = 1;
        }
      }
    }
    this.daycount = counteddays.reduce((partialSum, a) => partialSum + a, 0);

    let classtime = 0;
    let schooltime = 0;
    let timeranges = [];
    for (let i in days) {
      let day = days[i];
      let starttime = 0;
      let endtime = 0;
      // idek anymore
    }
  }

  toString() {
    return (
      this.name + ", " + this.courses.length + " courses, Score: " + self.score
    );
  }

  addCourse(crn) {
    if (!(crn in allCourses)) {
      return false;
    }
    this.courses.push(allCourses[crn]);
    this.crns.push(crn);
    if (this.checkValid()) {
      return true;
    }
    this.crns.pop();
    this.courses.pop();
    return false;
  }

  combineWith(otherSchedule) {
    this.courses.concat(otherSchedule.courses);
  }

  lunchBreaks() {
    let count = 0;
    const days = ["M", "T", "W", "R", "F"];
    for (let i in days) {
      let day = days[i];
      if (
        this.courseatdaytime(day, 1200) == 0 ||
        this.courseatdaytime(day, 1240) == 0
      ) {
        count += 1;
      }
    }
    return count;
  }

  courseatdaytime(day, time) {
    for (let i in this.courses) {
      let course = this.courses[i];
      if (course.isattime(day, time)) {
        return course;
      }
    }
    return 0;
  }

  display(type) {
    console.log(this.name + ": score = " + this.score);
    const days = [
      ["Monday", "Tuedsay", "Wednesday", "Thursday", "Friday"],
      ["M", "T", "W", "R", "F"],
      [1, 2, 3, 4, 5],
    ];
    switch (type) {
      case "map":
        break;
      case "clock":
        break;
      case "window":
        for (let i = 700; i < 2200; i++) {
          let j = i;
          if (i % 100 == 30) {
            j += 20;
          }
          if (i % 100 == 0 || (i - 30) % 100 == 0) {
            console.log(miltoreadable(i));
          }
        }
        for (let j = 0; j < days[0].length; j++) {
          console.log(days[0][j]);
        }
        for (let k = 0; k < this.courses.length; k++) {
          const course = this.courses[k];
          for (let l = 0; l < course.times.days.length; l++) {
            const day = course.times.days[l];
            let x = (0.1 + 0.18 * days[1].indexOf(day)) * WIDTH;
            let y = 40 + (course.times.time - 700) * ((HEIGHT - 55) / 1500);
            //gonna need a canvas for this one methinks
          }
        }
      case "timetable":
        console.log(
          "_____|    Monday     |    Tuesday    |   Wednesday   |   Thursday    |    Friday     |"
        );
        let line = "";
        for (let i = 700; i < 2200; i++) {
          line = "";
          if (!(1000 <= i && i <= 1230)) {
            line += " ";
          }
          line += "|";
          for (let j = 0; j < days[0].length; j++) {
            let found = false;
            for (let k = 0; k < this.courses.length; k++) {
              let course = this.courses[k];
              let content = course + " " + course.type;
              if (
                days[1][j] in course.times.days &&
                course.times.time == i + 10
              ) {
                found = true;
                if (content.length < 15) {
                  line += content;
                  for (let p = 0; p < 15 - content.length; p++) {
                    line += "_";
                  }
                } else {
                  line += content.substring(0, 15);
                }
                line += "|";
              } else if (
                course.times.days.includes(days[1][j]) &&
                (course.times.time == i - 20 || course.times.time == i - 60) &&
                content.length > 15 &&
                course.isattime(days[1][j], i - 1)
              ) {
                found = true;
                if (content.length < 30) {
                  line += content.substring(15);
                  for (let p = 0; p < 30 - content.length; p++) {
                    line += " ";
                  }
                } else {
                  line += content.substring(15, 30);
                }
                line += "|";
              } else if (
                course.times.days.includes(days[1][j]) &&
                (course.times.time == i - 50 || course.times.time == i - 90) &&
                content.length > 30 &&
                course.isattime(days[1][j], i - 1)
              ) {
                found = true;
                if (content.length < 45) {
                  line += content.substring(30);
                  let certainchar = " ";
                  if (course.times.length == 80) {
                    certainchar = "_";
                  }
                  for (let p = 0; p < 45 - content.length; p++) {
                    line += certainchar;
                  }
                } else {
                  line += content.substring(30, 45);
                }
                line += "|";
              } else if (
                course.times.days.includes(days[1][j]) &&
                (course.times.time == i - 50 || course.times.time == i - 90) &&
                course.isattime(days[1][j], i - 1)
              ) {
                found = true;
                line += "_______________|";
              } else if (course.isattime(days[1][j], i + 1)) {
                found = true;
                line += "               |";
              }
            }
            if (!found) {
              line += "_______________|";
            }
          }
        }
        if (line != "") {
          console.log(line);
        }
    }
  }
}

function minutes2hours(minutes) {
  return Math.floor(minutes / 60) * 100 + (minutes % 60);
}

function getTime(course) {
  return course.times.time;
}

function miltoreadable(time) {
  if (time % 100 == 60) time += 40;
  if (time >= 1300) time -= 1200;
  let result =
    Math.floor(time / 100).toString() +
    ":" +
    time.toString().substring(time.toString().length - 2);
  return result;
}

function longtoshortday(longday) {
  let days = [
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    ["M", "T", "W", "R", "F"],
  ];
  return days[1][days[0].indexOf(longday)];
}

function replace(str, old, replacement) {
  let result = "";
  for (let i = 0; i < str.length; i++) {
    let element = str[i];
    if (element != old) {
      result += element;
    } else {
      result += replacement;
    }
  }
  return result;
}

function int(str) {
  return parseInt(str);
}

function timerangetotimeandlength(timerange) {
  let time = 0;
  let length = 0;
  if (timerange.length < 10) {
    return time, length;
  }
  timerange = replace(timerange, ":", "");
  time = parseInt(timerange.substring(0, 4));
  if (timerange[5] == "P" && time < 1200) {
    time += 1200;
  }
  timerange = timerange.substring(10);
  let time2 = parseInt(timerange.substring(0, 4));
  if (timerange[5] == "P" && time2 < 1200) {
    time2 += 1200;
  }
  let hr1 = Math.floor(time / 100);
  let mn1 = time % 100;
  let hr2 = Math.floor(time2 / 100);
  let mn2 = time2 % 100;
  let hr = hr2 - hr1;
  let mn = mn2 - mn1;
  if (mn < 0) {
    hr -= 1;
    mn += 60;
  }
  length = mn + 60 * hr;
  return time, length;
}

function getscore(x) {
  return x[0].score;
}

function str(x) {
  return x.toString();
}

function getTextInput(str, remfunc) {
  console.log(str);
  let tempinput = document.createElement("input");
  let tempinputprompt = document.createElement("p");
  let tempinputsbmt = document.createElement("button");
  tempinputprompt.innerText = str;
  jsoninputdiv.insertBefore(
    tempinputprompt,
    jsoninputdiv.childNodes[jsoninputdiv.childNodes.length]
  );
  jsoninputdiv.insertBefore(
    tempinput,
    jsoninputdiv.childNodes[jsoninputdiv.childNodes.length]
  );
  jsoninputdiv.insertBefore(
    tempinputsbmt,
    jsoninputdiv.childNodes[jsoninputdiv.childNodes.length]
  );
  tempinputsbmt.onclick = function () {
    remfunc(tempinput.value);
    tempinputprompt.remove();
    tempinputsbmt.remove();
    tempinput.remove();
  };
}

function lookupCourse() {
  inp = getTextInput("Enter CRN (ex: 41935): ", function (inp) {
    if (!isNumeric(inp)) {
      console.log("You must enter a number");
    }
    inp = int(inp);
    if (!(inp in allCourses)) {
      console.log("crn " + str(inp) + " not found");
    }
    console.log(allCourses[inp]);
  });
}

function upper(str) {
  return str.charAt(0) + str.substring(1);
}

function functionalSearch(field, target) {
  let results = [];
  let resultcount = 0;
  for (let i in allCourses) {
    let course = allCourses[i];
    if (
      (field.toLowerCase() == "day" &&
        course.times.days.includes(
          longtoshortday(upper(target.toLowerCase()))
        )) ||
      str(course.get(field)).includes(target)
    ) {
      resultcount += 1;
      results.push(course.crn);
    }
  }
  if (resultcount == 0) {
    console.log("No matches :(");
  } else {
    return results;
  }
}

function narrowSearch(crns, field, target) {
  let results = [];
  let resultcount = 0;
  for (let i in crns) {
    let crn = crns[i];
    let course = allCourses[crn];
    if (
      (field.toLowerCase() == "day" &&
        course.times.days.includes(
          longtoshortday(upper(target.toLowerCase()))
        )) ||
      str(course.get(field)).includes(target)
    ) {
      resultcount += 1;
      results.push(course.crn);
    }
  }
  if (resultcount == 0) {
    console.log("No matches :(");
  } else {
    return results;
  }
}

function fieldSearch() {
  let subset = allCourses;
  getTextInput("What would you like to search by?", function (inp) {
    if (inp == "") {
      return;
    }
  });
  // come back to this one
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function init() {
  selector = document.getElementById("term-select");
  sbmtbutton = document.getElementById("sbmtcoursefile");
  jsoninputdiv = document.getElementById("jsoninputdiv");

  for (let i in files) {
    file = files[i];
    let tempoption = document.createElement("option");
    tempoption.innerText =
      file.substring(0, file.length - 9) +
      " " +
      file.substring(file.length - 9, file.length - 5);
    tempoption.value = file;
    selector.insertBefore(
      tempoption,
      selector.childNodes[selector.childNodes.length]
    );
    if (localStorage.getItem(file) == null) {
      askforJSON(file);
    } else {
      // console.log(localStorage.getItem(file));
    }
  }
}

function askforJSON(filename) {
  let tempprmpt = document.createElement("p");
  let tempinput = document.createElement("input");

  tempprmpt.innerText =
    "Input the " + filename.substring(0, filename.length - 5);
  tempinput.type = "file";
  jsoninputdiv.insertBefore(tempprmpt, jsoninputdiv.childNodes[0]);
  jsoninputdiv.insertBefore(tempinput, jsoninputdiv.childNodes[1]);

  tempinput.addEventListener("change", function () {
    let fr = new FileReader();
    fr.onload = function () {
      localStorage.setItem(filename, fr.result);
    };
    tempprmpt.remove();
    tempinput.remove();

    fr.readAsText(this.files[0]);
  });
}

function sbmtcfile() {
  console.log(selector.value + " Selected");
  if (selector.value != "") {
    coursefile = selector.value;
    selector.hidden = true;
    sbmtbutton.hidden = true;
    mainfunction();
  }
}

function readCourses() {}

function readRooms() {}

function readSchedules() {}

function mainfunction() {
  if (coursefile == "Winter2024.json") {
    datas = [
      [70154, 70155, 70167, 70851, 75638],
      [
        70156, 70157, 70158, 70159, 70160, 70161, 70162, 70163, 70164, 70165,
        70166, 70168, 70169, 70170, 70171, 70172, 70852, 71950, 71951, 72278,
        72660, 72676, 72865, 72866, 72867, 72868, 73689, 75640, 75641, 75642,
        75643, 75644,
      ],
      [72642, 75155, 75156, 75510],
      [
        72670, 72671, 72672, 73009, 73776, 73922, 74534, 74868, 74894, 74895,
        75459, 75511, 75512,
      ],
      [71974, 75332],
      [70197, 70198, 72883, 73014],
      [
        70199, 70200, 70201, 70202, 70203, 70204, 70205, 70206, 70207, 71906,
        71907, 71908, 71909, 71910, 71911, 71912, 71913, 71914, 71915, 71916,
        71941, 71966, 72277, 72876, 72877, 72878, 72879, 72880, 72881, 72882,
        73015, 73016, 73017, 73018, 73019, 73020, 75575, 75576, 75646, 75647,
        75648, 75649, 75651, 75653, 75654, 75655, 75656,
      ],
      [
        70208, 70209, 70210, 70211, 70212, 70213, 70214, 70215, 70855, 70856,
        72393, 72394, 72395, 72396, 72397, 72884, 72885, 72886, 72887, 72888,
        73021, 73022, 73023, 73024, 75574, 75577, 75578, 75657, 75658, 75659,
        75660,
      ],
      [73772, 74360, 75188],
      [
        73773, 73774, 73775, 73921, 74361, 74439, 74606, 74888, 75218, 75219,
        75449,
      ],
    ];
  } else if (coursefile == "Fall2023.json") {
    datas = [
      [40288, 40289, 40290, 40291, 45633],
      [
        40292, 40293, 40294, 40295, 40296, 40297, 40298, 40299, 40300, 40301,
        40302, 40303, 40304, 40305, 40306, 40308, 40309, 40310, 41560, 41576,
        41964, 42002, 42003, 42958, 42959, 42960, 42961, 45708, 45709, 45710,
        45711,
      ],
      [42684, 42942, 44933],
      [
        42685, 42686, 42687, 42688, 42943, 42944, 42945, 42946, 42947, 42948,
        45100, 45101,
      ],
      [40363, 40364, 40365, 40366, 42035],
      [
        40367, 40368, 40369, 40370, 40371, 40372, 40373, 40374, 40375, 40376,
        40377, 40378, 40379, 40914, 40915, 41155, 41156, 41918, 41920, 41921,
        41922, 41923, 41924, 41925, 41926, 41927, 41928, 41929, 41930, 41931,
        41970, 41972, 41973, 41974, 41976, 42084, 42334, 42336, 42337, 42693,
        42695, 45753, 45754, 45755, 45756, 45757, 45758, 45764,
      ],
      [
        40380, 40381, 40382, 40383, 41919, 41975, 41977, 42335, 42338, 42339,
        42340, 42702, 42703, 42704, 42705, 42969, 42970, 42971, 42972, 42973,
        42974, 42975, 42976, 42977, 42978, 42979, 43715, 43879, 43880, 45759,
        45760, 45761, 45765,
      ],
      [43913, 44487, 45388],
      [
        43914, 43915, 43916, 44108, 44488, 44572, 44984, 45102, 45249, 45250,
        45389, 45390, 45391, 45628,
      ],
      [
        42752, 42753, 42754, 42755, 42756, 42757, 42758, 42759, 42760, 42761,
        42762, 42763, 42764, 42765, 42766, 42767, 42768, 43976, 45630, 45773,
      ],
    ];
  } else if (coursefile == "Fall2024.json") {
    datas = [];
  } else {
    datas = [];
  }
  let txt = localStorage.getItem(coursefile);
  obj = JSON.parse(txt);
  allCourses = {};
  for (let i in obj) {
    let curobj = obj[i];
    let crn = curobj.crn;
    let title = curobj.title;
    let code = curobj.code;
    let room = curobj.room;
    let section = curobj.section;
    let type = curobj.type;

    let times = curobj.times;
    let time = times.time;
    let days = times.days;
    let length = times.length;
    let biweekly = times.biweekly;

    let tempTime = new CourseTime(days, time, length, biweekly);
    let tempCourse = new Course(
      title,
      room,
      crn,
      type,
      code,
      tempTime,
      section
    );
    allCourses[crn] = tempCourse;
  }
  console.log(
    "" +
      allCourses[
        Object.keys(allCourses)[
          Math.floor(Math.random() * Object.keys(allCourses).length)
        ]
      ]
  );
  readCourses();
  readRooms();
  readSchedules();
}

function startGame() {
  // Initialization code
  myGameArea.start();
}

function updateGameArea() {
  myGameArea.clear();
  myGameArea.frameNo++;
  // every frame code - use if(everyinterval(n)) to do something every n frames
}

function everyinterval(n) {
  // no touch
  if ((myGameArea.frameNo / n) % 1 == 0) {
    return true;
  }
  return false;
}

function rad(deg) {
  return (deg / 180) * Math.PI;
}
// Draws text ON CANVAS
function makeText(text, color, x, y, fontSize = 15, rot = 0) {
  ctx = myGameArea.context;
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(rad(rot));
  ctx.font = fontSize + "px sans-serif";
  ctx.fillStyle = color;
  ctx.fillText(text, 0, 0);
}

// function input(prompt) {
//     box.hidden = false;
//     prmpt.hidden = false;
//     sbmt.hidden = false;
//     prmpt.textContent = prompt;
// }

// function inputhelper() {
//     console.log(box.value);
//     box.hidden = true;
//     prmpt.hidden = true;
//     sbmt.hidden = true;
//     startGame();
// }
