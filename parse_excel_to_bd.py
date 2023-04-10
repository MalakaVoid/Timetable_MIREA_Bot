import sqlite3


sqlite_connection = sqlite3.connect('Timetable_DB.db')
cursor = sqlite_connection.cursor()

sqlite_select_query = ""
record = cursor.fetchall()
print("Версия базы данных SQLite: ", record)
cursor.close()
