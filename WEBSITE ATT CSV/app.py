from flask import Flask, render_template
import pandas as pd
import csv
import os
from datetime import datetime as dt

app = Flask(__name__)

time_now = pd.Timestamp.now().strftime('%H:%M:%S')

time_late = pd.to_datetime('12:30:0').strftime('%H:%M:%S')

date = dt.now().strftime('%d:%m:%Y')

file_path = os.path.join('attendance', date + '.csv')  

data = []

#make csv
def csvmak(): 
    if not os.path.exists(file_path):  
        with open(file_path, 'w', newline='') as file:
            csvr = csv.writer(file)
            names = []
            Header = f'Name, Time, Status'
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
        if time_now > time_late:
            list = att.writelines(f'\n{name}, {time_now}, {"LATE"}')
            data.append(list)
        else:
            list = att.writelines(f'\n{name}, {time_now}, {"PRESENT"}')
            data.append(list)





@app.route('/')
def index():
    return render_template('format.html',data=data)





