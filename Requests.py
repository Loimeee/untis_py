import requests
from datetime import datetime
import json
from datetime import timedelta

now = datetime.now()

s = requests.Session()

with open("id_dict.json", "r") as file:
    id_dict = json.load(file)

with open("teacher_dict.json", "r") as file:
    teacher_dict = json.load(file)


def all(year, month, day, decode):
    date = str(year) + "-" + str(month) + "-" + str(day)
    # erste Website für JSESSION
    s.get("https://tipo.webuntis.com/WebUntis/?school=helmholz+gymnasium+karlsruhe")
    # zweite Website für Auth und traceId
    data = {"school": "helmholz gymnasium karlsruhe", "j_username": "9b#li#20041021", "j_password": "springField100%"}
    s.post("https://tipo.webuntis.com/WebUntis/j_spring_security_check", data=data)
    # dritte Website für timetable

    week_request = s.get(
        "https://tipo.webuntis.com/WebUntis/api/public/timetable/weekly/data?elementType=1&elementId=197&date=" + date + "&formatId=1").text
    if decode:
        decode = json.loads(week_request)
        lessondecode = decode["data"]["result"]["data"]["elementPeriods"]["197"]
        return lessondecode
    else:
        return week_request


def jsession():
    s.get("https://tipo.webuntis.com/WebUntis/?school=helmholz+gymnasium+karlsruhe")


def traceid():
    data = {"school": "helmholz gymnasium karlsruhe", "j_username": "9b#li#20041021", "j_password": "springField100%"}
    s.post("https://tipo.webuntis.com/WebUntis/j_spring_security_check", data=data)


def timetable():
    week_request = s.get(
        "https://tipo.webuntis.com/WebUntis/api/public/timetable/weekly/data?elementType=1&elementId=197&date=" + str(
            now.year) + "-" + str(now.month) + "-" + str(now.day) + "&formatId=1").text
    return week_request


def jsondecode(data):
    decode = json.loads(data)
    lessondecode = decode["data"]["result"]["data"]["elementPeriods"]["197"]
    return lessondecode


def get_lessoninfo(year, month, day, weekday, lessonname):
    for lesson in id_dict:
        if id_dict[lesson] == lessonname:
            lessonid = lesson
            break
    for period in all(year, month, day, True):
        period_weekday = datetime.strptime(str(period["date"]), "%Y%m%d").weekday()
        # Die str() sind nur dazu da, um alle auf einen Type zu bringen,
        # sodass es zu keinen Fehlern kommt wenn str und int verglichen werden
        if str(period["lessonId"]) == str(lessonid) and str(period_weekday) == str(weekday):
            element = all(year, month, day, True).index(period)
            break
    decode = json.loads(all(year, month, day, False))
    lessondecode = decode["data"]["result"]["data"]["elementPeriods"]["197"]
    r = lessondecode[element]
    # request an spezielle URL für angeforderte Stunde
    single_lesson = s.get(
        "https://tipo.webuntis.com/WebUntis/api/public/period/info?date=" + str(r["date"]) + "&starttime=" + str(
            r["startTime"]) + "&endtime=" + str(
            r["endTime"]) + "&elemid=197&elemtype=1&ttFmtId=1&selectedPeriodId=" + str(r["id"])).text
    single_decode_one = json.loads(single_lesson)["data"]["blocks"]
    for period in range(0, len(single_decode_one)):
        if str(json.loads(single_lesson)["data"]["blocks"][period][0]["lesson"]["id"]) in id_dict:
            right_lesson = period
            break
    single_decode = json.loads(single_lesson)["data"]["blocks"][right_lesson][0]
    return single_decode


def get_teachername(year, month, day, weekday, lessonname):
    return get_lessoninfo(year, month, day, weekday, lessonname)["teacherName"]


class PeriodData:
    def __init__(self, lessonId, startTime, endTime, weekday, lessonText, date):
        self.lessonId = lessonId
        self.startTime = startTime
        self.endTime = endTime
        self.weekday = weekday
        self.lessonText = lessonText
        self.date = datetime.strptime(str(date), "%Y%m%d")
        self.datebad = date
        # self.lessonname = id_dict[str(self.lessonId)]
        # self.teachername_dict = teacher_dict[str(self.lessonId)]
        # self.teachername_request = get_teachername(self.date.year, self.date.month, self.date.day, self.weekday, self.lessonname)

    def room(self):
        return str(get_lessoninfo(self.date.year, self.date.month, self.date.day, self.weekday, self.lessonname())[
                       "roomSubstitutions"][0]["curRoom"]["name"])

    def lessonname(self):
        if str(self.lessonId) in id_dict:
            return id_dict[str(self.lessonId)]
        else:
            pass

    def teachername_dict(self):
        if str(self.lessonId) in id_dict:
            return teacher_dict[str(self.lessonId)]
        else:
            pass

    def teachername_request(self):
        if str(self.lessonId) in id_dict:
            return get_teachername(self.date.year, self.date.month, self.date.day, self.weekday, self.lessonname())
        else:
            pass

    def weekday_converter(self):
        if self.weekday == 0:
            return "Montag"
        if self.weekday == 1:
            return "Dienstag"
        if self.weekday == 2:
            return "Mittwoch"
        if self.weekday == 3:
            return "Donnerstag"
        if self.weekday == 4:
            return "Freitag"


def entfall(year, month, day):
    with open("perfect_week.json", "r") as file:
        perfect_week = json.load(file)

    entfall = []
    all_encoded = all(year, month, day, False)

    all_decoded = jsondecode(all_encoded)

    for perfect in perfect_week:

        for period in all_decoded:

            if str(period["lessonId"]) not in id_dict:
                continue
            else:
                weekday = datetime.strptime(str(period["date"]), "%Y%m%d").weekday()
                # period = PeriodData(period["lessonId"], period["startTime"], period["endTime"], weekday,
                #                    period["lessonText"], period["date"])
                if perfect["lessonId"] == period["lessonId"] and perfect["startTime"] == period["startTime"] and \
                        perfect["weekday"] == weekday:
                    entf = False
                    break
                else:
                    entf = True
        if entf:
            first_of_week = datetime(year, month, day) - timedelta(datetime(year, month, day).weekday())
            date = first_of_week + timedelta(perfect["weekday"])
            perfect = PeriodData(perfect["lessonId"], perfect["startTime"], perfect["endTime"], perfect["weekday"],
                                 "None", (str(date.year) + str(date.month) + str(date.day)))
            entfall.append(perfect)
    return entfall


def special_periods(year, month, day):
    special_periods = []

    for period in all(year, month, day, True):
        weekday = datetime.strptime(str(period["date"]), "%Y%m%d").weekday()
        if period["cellState"] == "ADDITIONAL":
            period = PeriodData(period["lessonId"], period["startTime"], period["endTime"], weekday,
                                period["lessonText"], period["date"])
            special_periods.append(period)

    return special_periods


def exam(year, month, day):
    exam = []

    for period in all(year, month, day, True):
        if period["cellState"] == "EXAM" and str(period["lessonId"]) in id_dict:
            weekday = datetime.strptime(str(period["date"]), "%Y%m%d").weekday()
            period = PeriodData(period["lessonId"], period["startTime"], period["endTime"], weekday,
                                period["lessonText"], period["date"])
            exam.append(period)
    return exam


def substitution(year, month, day):
    substitution = []

    for period in all(year, month, day, True):
        if period["cellState"] == "SUBSTITUTION" and str(period["lessonId"]) in id_dict:
            weekday = datetime.strptime(str(period["date"]), "%Y%m%d").weekday()
            period = PeriodData(period["lessonId"], period["startTime"], period["endTime"], weekday,
                                period["lessonText"], period["date"])
            substitution.append(period)
    return substitution


def roomsubstitution(year, month, day):
    roomsubstitution = []

    for period in all(year, month, day, True):
        if period["cellState"] == "ROOMSUBSTITUTION" and str(period["lessonId"]) in id_dict:
            weekday = datetime.strptime(str(period["date"]), "%Y%m%d").weekday()
            period = PeriodData(period["lessonId"], period["startTime"], period["endTime"], weekday,
                                period["lessonText"], period["date"])
            roomsubstitution.append(period)
    return roomsubstitution


def week(year, month, day):
    if len(entfall(year, month, day)) != 0:
        entfall_list = []
        for period in entfall(year, month, day):
            to_append = period.lessonname() + " entfällt am " + period.weekday_converter()
            if to_append not in entfall_list:
                entfall_list.append(to_append)
        entfall_joined = " --- ".join(entfall_list)
    else:
        entfall_joined = "Kein Entfall diese Woche"

    if len(substitution(year, month, day)) != 0:
        substitution_list = []
        for period in substitution(year, month, day):
            to_append = period.lessonname() + " wird am " + period.weekday_converter() + " bei " + period.teachername_request() + " in Raum " + period.room() + " vertreten"
            if to_append not in substitution_list:
                substitution_list.append(to_append)
        substitution_joined = " --- ".join(substitution_list)
    else:
        substitution_joined = "Keine Vertretung diese Woche"

    if len(roomsubstitution(year, month, day)) != 0:
        substitution_list = []
        for period in roomsubstitution(year, month, day):
            to_append = period.lessonname() + " am " + period.weekday_converter() + " wird verlegt nach Raum " + period.room()
            if to_append not in substitution_list:
                substitution_list.append(to_append)
        roomsubstitution_joined = " --- ".join(substitution_list)
    else:
        roomsubstitution_joined = "Keine Raumvertretung diese Woche"

    if len(exam(year, month, day)) != 0:
        exam_list = []
        for period in exam(year, month, day):
            to_append = "In " + period.lessonname() + " wird am " + period.weekday_converter() + " eine Arbeit geschrieben"
        if to_append not in exam_list:
            exam_list.append(to_append)
        exam_joined = " --- ".join(exam_list)
    else:
        exam_joined = "Keine Arbeiten diese Woche"

    if len(special_periods(year, month, day)) != 0:
        special_list = []
        for period in special_periods(year, month, day):
            to_append = "Diese Woche gibt es am " + period.weekday_converter() + " eine spezielle Stunde mit dem Text: " + period.lessonText
        if to_append not in special_list:
            special_list.append(to_append)
        special_joined = " --- ".join(special_list)
    else:
        special_joined = "Keine speziellen Stunden diese Woche"

    return entfall_joined + "\n" + \
           substitution_joined + "\n" + \
           roomsubstitution_joined + "\n" + \
           exam_joined + "\n" + \
           special_joined
