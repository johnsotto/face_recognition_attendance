import pandas as pd
import mysql.connector

db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'juss2005',
    database = 'attendance'

)
 

time_now = pd.Timestamp.now().strftime('%H:%M:%S')

time_late = pd.to_datetime('12:30:0').strftime('%H:%M:%S')

cr = db.cursor()

format = "INSERT INTO attendances (date, name, time, status) VALUES (CURRENT_DATE(), %s, CURRENT_TIME(), %s)"


def marked(name):  
    if time_now > time_late:
        value = (name, 'LATE')
        cr.execute(format, value)


    else: 
        value = (name, 'PRESENT')
        cr.execute(format, value)
    
    db.commit()

marked("johnasdasdsss")
