import csv
from datetime import datetime
import os

date_now = datetime.now().strftime("%Y-%m-%d")
file_path = os.path.join('attendance', date_now + '.csv')  
#make csv
def csvmak():   
    with open(file_path, 'w', newline='') as file:
        csvr = csv.writer(file)
        names = []
        Header = f'Name, Time'
        Header = Header.split(',')
        names.insert(0, Header)
        csvr.writerows(names)

#list the name in attendace
def list_att(name,csva):
    with open(csva, 'r+') as att:
        dataL =  att.readlines()
        names = []
        for i in dataL:
            entry = i.split(',')
            names.append(entry[0])
        if name not in names:    
            time = datetime.now().strftime('%H:%M')
            att.writelines(f'\n{name}, {time}')
            
