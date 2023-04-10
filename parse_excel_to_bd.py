import sqlite3

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

group_to_bd("1224455", "БСБО-10-22")
