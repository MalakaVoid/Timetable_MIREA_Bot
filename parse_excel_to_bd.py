import sqlite3

def group_to_bd(user_id, group):
    sqlite_connection = sqlite3.connect('Timetable_DB.db')
    cursor = sqlite_connection.cursor()
    insert_user_id = f"INSERT INTO User (user_tg_id, group_num) VALUES ({user_id}, {group})"
    cursor.execute(insert_user_id)


