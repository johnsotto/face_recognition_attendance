from flask import Flask, render_template, request
import pandas as pd
import csv
import os
from datetime import datetime as dt

app = Flask(__name__)

time_now = dt.now().strftime('%H:%M:%S')

time_late = '12:30:00'

date = dt.now().strftime('%d_%m_%Y')

file_path = os.path.join('attendance', date + '.csv')  

def csvmak(): 
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            header = ['Name', 'Time', 'Status']
            csv_writer.writerow(header)

def list_att(name, csva):
    status = "PRESENT"
    if time_now > time_late:
        status = "LATE"

    with open(csva, 'r+') as att:
        lines = att.readlines()
        names = [line.split(',')[0] for line in lines]
        
        if name not in names:
            record = f"{name},{time_now},{status}\n"
            att.write(record)


faces_path = 'faces/'

app.config['faces_path'] = faces_path

@app.route('/')
def home():
    return render_template('format.html')

@app.route('/list')
def list():
    data_df = pd.read_csv(file_path)
    datas = data_df.to_dict(orient='records')
    return render_template('list.html', datas=datas)
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/upload', methods=["POST"])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    filename = request.form.get('filename')
    if file.filename == '':
            return 'No selected file'
    if file and filename:
        extension = file.filename.rsplit('.')
        filename = filename +'.'+ extension[1]
        file.save(os.path.join(app.config['faces_path'], filename))
        return 'File uploaded successfully'
    else:
        return 'Error'
    
