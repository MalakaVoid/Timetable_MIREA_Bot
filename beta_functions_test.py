from openpyxl import load_workbook
from datetime import datetime, timedelta

workbook = load_workbook('temp.xlsx')
ws = workbook[workbook.sheetnames[0]]

index = 0
for i in range(1, 500):
    if ws.cell(row=2, column=i).value == "БСБО-10-21":
        index = i
        break
print(index)
print("---------------------------")
str_output = ""
for j in range(4,88):
    if ws.cell(row=j, column=1).value!=None:
        str_output += str(ws.cell(row=j, column=1).value) + "\n"
    if ws.cell(row=j, column=index).value != "":
        #Четность нечетность
        str_output += str(ws.cell(row=j, column=5).value) + " || "
        #Время начало пары
        tmp=j
        if ws.cell(row=j, column=3).value==None:
            tmp=j-1
        str_output += str(ws.cell(row=tmp, column=3).value) + " || "
        str_output += str(ws.cell(row=tmp, column=4).value) + " || "
        #Вывод названия предмета
        str_output += str(ws.cell(row=j, column=index).value) + " || "
        #Лекция или практика
        str_output += str(ws.cell(row=j, column=index+1).value) + " || "
        #Аудитория
        if ws.cell(row=j, column=index+2).value != "":
            str_output += str(ws.cell(row=j, column=index+2).value) + "\n"
        else:
            str_output += "\n"

print(str_output)