from openpyxl import load_workbook

workbook = load_workbook('temp.xlsx')
first_sheet = workbook.get_sheet_names()[0]
ws = workbook.get_sheet_by_name(first_sheet)

index = 0
for i in range(1, 500):
    if ws.cell(row=2, column=i).value == "БСБО-10-21":
        index = i
        break
print(index)
print("---------------------------")
for j in range(4,88):
    if ws.cell(row=j, column=1).value!=None:
        print(ws.cell(row=j, column=1).value)
    if ws.cell(row=j, column=index).value != "":
        #Четность нечетность
        print(ws.cell(row=j, column=5).value, end=" || ")
        #Время начало пары
        tmp=j
        if ws.cell(row=j, column=3).value==None:
            tmp=j-1
        print(ws.cell(row=tmp, column=3).value, end=" || ")
        print(ws.cell(row=tmp, column=4).value, end=" || ")
        #Вывод названия предмета
        print(ws.cell(row=j, column=index).value, end=" || ")
        #Лекция или практика
        print(ws.cell(row=j, column=index+1).value, end=" || ")
        #Аудитория
        print(ws.cell(row=j, column=index+2).value, end="\n")