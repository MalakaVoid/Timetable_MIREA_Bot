from datetime import datetime, timedelta, date
import math
import sqlite3


def is_group_aviable(str_group):
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    select_groups = cursor.execute(f"SELECT group_num FROM timetable WHERE group_num = '{str_group}'")
    if select_groups.fetchall() == []:
        return False
    else:
        return True


def is_even(date):
    first_week = datetime(2023, 2, 5)
    todaydate = date
    amountDays = todaydate - first_week
    if week_num_by_day(date) % 2 == 0:
        return True
    else:
        return False


def is_even_current():
    first_week = datetime(2023, 2, 5)
    todaydate = datetime.today()
    amountDays = todaydate - first_week
    if math.ceil((amountDays.days + 1) / 7) == 0:
        return False
    else:
        return True


def current_week_timetable(user_id):
    arr_of_parameters = []
    arr_days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
    str_output = "<b>Расписание на текущую неделю</b>" + "\n\n"
    if datetime.today() < datetime(year=2023, month=2, day=6) or datetime.today() > datetime(year=2023, month=6, day=4):
        str_output += '<b>У вас нет пар!</b>\n\n'
        return str_output
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = cursor.execute(f"SELECT group_num FROM User WHERE user_tg_id = '{user_id}'")
    group = question_to_database.fetchall()[0][0]
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


def current_day_timetable(user_id, datetime_date_input):
    arr_of_parameters = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database1 = cursor.execute(f"SELECT group_num FROM User WHERE user_tg_id = '{user_id}'")
    group = question_to_database1.fetchall()[0][0]
    current_date = current_day_of_the_week(datetime_date_input)
    str_output = f"<b>Расписание на {datetime_date_input.strftime('%d.%m.%Y')}</b>" + "\n\n"
    if datetime_date_input < datetime(year=2023, month=2, day=6) or datetime_date_input > datetime(year=2023, month=6,
                                                                                                   day=4):
        str_output += '<b>У вас нет пар!</b>\n\n'
        str_output += current_day_events(user_id, datetime_date_input)
        return str_output
    if is_even(datetime_date_input):
        even_num = "II"
    else:
        even_num = "I"
    question_to_database = cursor.execute(
        f"SELECT interval_pairs, name, type, place, teacher_name FROM timetable WHERE group_num = '{group}' AND day_of_week = '{current_date}' AND even = '{even_num}'")
    arr_of_parameters = question_to_database.fetchall()
    for each in arr_of_parameters:
        flag = False
        if is_exception_remove(each[1]):
            exception_arr = array_of_exceptions(each[1])
            num_of_week = week_num_by_day(datetime_date_input)
            for num in exception_arr:
                if num_of_week == int(num):
                    flag = True
                    break
            if flag:
                continue
            else:
                pair = exception_controller(each[1])
        elif is_exception_add(each[1]):
            exception_arr = array_of_exceptions(each[1])
            num_of_week = week_num_by_day(datetime_date_input)
            for num in exception_arr:
                if num_of_week == int(num):
                    flag = True
                    break
            if flag:
                pair = exception_controller(each[1])
            else:
                continue
        else:
            pair = each[1]
        time = each[0]
        time = time.replace("-", ":")
        time = time.replace(" ", "-")
        str_output += "<b>" + time + "</b>" + "\n"
        str_output += "<em>" + pair + "</em>" + "\n"
        str_output += each[2] + " | " + each[3] + " | " + each[4] + "\n\n"

    str_output += current_day_events(user_id, datetime_date_input)
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


def enter_event(chat_id, date, time, event):
    arr_of_parameters = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = cursor.execute(
        f"SELECT date, event, time FROM user_events WHERE user_tg_id = '{chat_id}' AND date = '{date.date()}'")
    arr_of_parameters = question_to_database.fetchall()
    if arr_of_parameters == []:
        cursor.execute(
            f"INSERT INTO user_events (user_tg_id, date, event, time, event_id) VALUES ('{chat_id}', '{date.date()}', '{event}', '{time}', '1')")
        sqlite_connection.commit()
    else:
        event_index = len(arr_of_parameters) + 1
        cursor.execute(
            f"INSERT INTO user_events (user_tg_id, date, event, time, event_id) VALUES ('{chat_id}', '{date.date()}', '{event}', '{time}', '{event_index}')")
        sqlite_connection.commit()
    update_and_sort_events_by_id(date, chat_id)
    return "Ивент добавлен"


def update_description_event(event, event_id, chat_id, date):
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = f"UPDATE user_events SET event = '{event}' WHERE event_id = '{event_id}' AND user_tg_id = '{chat_id}' AND date = '{date.date()}'"
    cursor.execute(question_to_database)
    sqlite_connection.commit()
    return "Описание ивента обновлёно"


def update_time_event(time, event_id, chat_id, date):
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = f"UPDATE user_events SET time = '{time}' WHERE event_id = '{event_id}' AND user_tg_id = '{chat_id}' AND date = '{date.date()}'"
    cursor.execute(question_to_database)
    sqlite_connection.commit()
    update_and_sort_events_by_id(date, chat_id)
    return "Время ивента обновлёно"


def current_day_events(user_id, datetime_date_input):
    str_output = ""
    arr_of_parameters = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = cursor.execute(
        f"SELECT event_id, time, event FROM user_events WHERE user_tg_id = '{user_id}' AND date = '{datetime_date_input.date()}' ORDER BY event_id")
    arr_of_parameters = question_to_database.fetchall()
    if event_existense(datetime_date_input, user_id):
        str_output += "<b>СОБЫТИЯ</b>" + "\n"
    for each in arr_of_parameters:
        str_output += "<b>" + each[0] + "</b> - <em>" + each[1] + " " + each[2] + "</em>"
        str_output += "\n"
    return str_output


def delete_event(event_id, chat_id, date):
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = f"DELETE FROM user_events WHERE event_id = '{event_id}' AND user_tg_id = '{chat_id}' AND date = '{date.date()}'"
    cursor.execute(question_to_database)
    sqlite_connection.commit()
    update_and_sort_events_by_id(date, chat_id)
    return "Ивент удалён"


def update_and_sort_events_by_id(datetime_date_input, chat_id):
    arr_of_time = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = f"SELECT time, id from user_events WHERE user_tg_id = '{chat_id}' AND date = '{datetime_date_input.date()}' ORDER BY time(time)"
    arr_of_time = cursor.execute(question_to_database).fetchall()
    tmp = 1
    for each in arr_of_time:
        question_to_database = f"UPDATE user_events SET event_id = '{tmp}' WHERE time = '{each[0]}' AND id = {each[1]}"
        cursor.execute(question_to_database)
        tmp += 1
        sqlite_connection.commit()


def week_num_by_day(date):
    first_week = datetime(2023, 2, 6)
    todaydate = date
    amount_days = todaydate - first_week
    week_num = math.ceil((amount_days.days + 1) / 7)
    return week_num


def event_existense(date, chat_id):
    arr_of_parameters = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = cursor.execute(
        f"SELECT event_id, time, event FROM user_events WHERE user_tg_id = '{chat_id}' AND date = '{date.date()}' ORDER BY event_id")
    arr_of_parameters = question_to_database.fetchall()
    if arr_of_parameters == []:
        return False
    else:
        return True


def event_id_arr(date, chat_id):
    arr_of_parameters = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database = cursor.execute(
        f"SELECT event_id FROM user_events WHERE user_tg_id = '{chat_id}' AND date = '{date.date()}' ORDER BY event_id")
    arr_of_parameters = question_to_database.fetchall()
    return arr_of_parameters


def current_day_timetable_upd(user_id, datetime_date_input):
    arr_of_parameters = []
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    question_to_database1 = cursor.execute(f"SELECT group_num FROM User WHERE user_tg_id = '{user_id}'")
    group = question_to_database1.fetchall()[0][0]
    current_date = current_day_of_the_week(datetime_date_input)
    question_to_database = cursor.execute(
        f"SELECT interval_pairs, name, type, place, teacher_name FROM timetable WHERE group_num = '{group}' AND day_of_week = '{current_date}'")
    arr_of_parameters = []
    arr_of_parameters = question_to_database.fetchall()
    print(arr_of_parameters)


def exception_controller(str_input):
    str_output = ""
    if is_exception_remove(str_input) or is_exception_add(str_input):
        index = str_input.rfind("н. ") + 3
        str_output = str_input[index::]
    else:
        str_output = str_input
    return str_output


def is_exception_remove(str_input):
    if "кр." in str_input:
        return True
    else:
        return False


def is_exception_add(str_input):
    if not is_exception_remove(str_input) and "н." in str_input:
        return True
    else:
        return False


def array_of_exceptions(str_input):
    arr_output = []
    if is_exception_remove(str_input):
        index = str_input.rfind("н. ") + 3
        str_input = str_input[:index:]
        arr_output = str_input.split()
        arr_output = arr_output[1].split(",")
    elif is_exception_add(str_input):
        index = str_input.rfind("н. ") + 3
        str_input = str_input[:index:]
        arr_output = str_input.split()
        arr_output = arr_output[0].split(",")
    return arr_output