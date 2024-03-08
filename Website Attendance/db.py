import mysql.connector

db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'juss2005',
    database = 'attendance'

)
 

cr = db.cursor()
cr.execute("CREATE TABLE attendances (date VARCHAR(255), name VARCHAR(255), time VARCHAR(255), status VARCHAR(255))")