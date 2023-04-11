from openpyxl import load_workbook
from datetime import datetime, timedelta, date
import sqlite3

# Функция проверки наличия группы

def is_group_aviable(str_group):
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    select_groups = cursor.execute(f"SELECT group_num FROM timetable WHERE group_num = '{str_group}'")
    if select_groups.fetchall() == []:
        return False
    else:
        return True

# Вспомогательная функция определяющая четность или нечетность актуальной недели
def is_even(date):
    first_week = datetime(2023, 2, 5)
    todaydate = date
    amountDays = todaydate - first_week
    if (amountDays.days // 7) % 2 == 0:
        return False
    else:
        return True

def is_even_current():
    first_week = datetime(2023, 2, 5)
    todaydate = datetime.today()
    amountDays = todaydate - first_week
    if (amountDays.days // 7) % 2 == 0:
        return False
    else:
        return True

# Функция определения расписания на актуальную неделю

def current_week_timetable(user_id):
    arr_of_parameters = []
    arr_days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
    str_output = "<b>Расписание на текущую неделю</b>" + "\n\n"
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database1 = cursor.execute(f"SELECT group_num FROM User WHERE user_tg_id = '{user_id}'")
    group = question_to_database1.fetchall()[0][0]
    datetime_date_input = datetime.today()
    current_date = current_day_of_the_week(datetime_date_input)
    if is_even(datetime_date_input):
        even_num = "II"
    else:
        even_num = "I"
    question_to_database = cursor.execute(
        f"SELECT interval_pairs, name, type, place, teacher_name, day_of_week FROM timetable WHERE group_num = '{group}' AND even = '{even_num}'")
    arr_of_parameters = question_to_database.fetchall()
    for each_day in arr_days:
        str_output += "<b>" + each_day + "</b>" + "\n"
        for each in arr_of_parameters:
            if each[5] == each_day:
                time = each[0]
                time = time.replace("-", ":")
                time = time.replace(" ", "-")
                str_output += "<b>" + time + "</b>" + "\n"
                str_output += "<em>" + each[1] + "</em>" + "\n"
                str_output += each[2] + " | " + each[3] + " | " + each[4] + "\n\n"
        str_output += "\n"
    return str_output

# Вспомогательная функция определения дня недели по его номеру

def current_day_of_the_week(date):
    datetime_date = date
    week_num = datetime_date.isoweekday()
    if week_num == 1:
        return "ПОНЕДЕЛЬНИК"
    elif week_num == 2:
        return "ВТОРНИК"
    elif week_num == 3:
        return "СРЕДА"
    elif week_num == 4:
        return "ЧЕТВЕРГ"
    elif week_num == 5:
        return "ПЯТНИЦА"
    elif week_num == 6:
        return "СУББОТА"

# Функция определения расписания на конкретный день

def current_day_timetable(user_id, datetime_date_input):
    arr_of_parameters = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database1 = cursor.execute(f"SELECT group_num FROM User WHERE user_tg_id = '{user_id}'")
    group = question_to_database1.fetchall()[0][0]
    current_date = current_day_of_the_week(datetime_date_input)
    str_output = f"<b>Расписание на {datetime_date_input.strftime('%d.%m.%Y')}</b>" + "\n\n"
    if is_even(datetime_date_input):
        even_num = "II"
    else:
        even_num = "I"
    question_to_database = cursor.execute(f"SELECT interval_pairs, name, type, place, teacher_name FROM timetable WHERE group_num = '{group}' AND day_of_week = '{current_date}' AND even = '{even_num}'")
    arr_of_parameters = question_to_database.fetchall()
    for each in arr_of_parameters:
        time = each[0]
        time = time.replace("-", ":")
        time = time.replace(" ", "-")
        str_output += "<b>" + time + "</b>" + "\n"
        str_output += "<em>" + each[1] + "</em>" + "\n"
        str_output += each[2] + " | " + each[3] + " | " + each[4] + "\n\n"
    return str_output

def group_to_bd(user_id, group):
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = cursor.execute(f"SELECT user_tg_id FROM User WHERE user_tg_id = '{user_id}'")
    if question_to_database.fetchall() == []:
        insert_user_id = f"INSERT INTO User (user_tg_id, group_num) VALUES ('{user_id}', '{group}')"
        cursor.execute(insert_user_id)
    else:
        update_user_id = f"UPDATE User SET group_num = '{group}' WHERE user_tg_id = '{user_id}'"
        cursor.execute(update_user_id)
    sqlite_connection.commit()


