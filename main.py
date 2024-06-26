import os, sys
import face_recognition as fr 
import numpy as np
import cv2
import pickle
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading
from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import csv
import os
from datetime import datetime as dt

app = Flask(__name__, template_folder='templates')

time_now = dt.now().strftime('%H:%M:%S')

time_late = '12:30:00'

date = dt.now().strftime('%d_%m_%Y')

file_path = os.path.join('attendance', date + '.csv') 


def csvmak():
    try:
        with open(file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            header = ['Name', 'Time', 'Status']
            csv_writer.writerow(header)
    except (OSError):
        os.mkdir('attendance')
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
    return render_template('login.html')

@app.route('/download/<filename>')
def download_file(filename):
    directory = os.path.join(app.root_path, 'attendance')
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found"

@app.route('/list')
def list():
    data_df = pd.read_csv(file_path)
    datas = data_df.to_dict(orient='records')
    return render_template('list.html', datas=datas)

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
    
@app.route('/files')
def list_files():
    directory = os.path.join(app.root_path, 'attendance')
    files = os.listdir(directory)
    return render_template('files.html', files=files)
    



class Watcher(FileSystemEventHandler):
    def __init__(self, fri):
        self.fri = fri

    def on_created(self, event):
        print(f'New file detected: {event.src_path}')
        self.fri.encode_faces()

class FaceRecognition:
    face_loc = []
    face_enc = []
    face_nam = []
    fam_face_enc = []
    fam_face_nam = []
    detect_frame = True

    def __init__(self):
        self.encode_faces()

    def encode_faces(self):
        try:
            with open('cache.pkl', 'rb') as f:
                self.fam_face_enc, self.fam_face_nam = pickle.load(f)
        except (FileNotFoundError, EOFError):
            self.fam_face_enc = []
            self.fam_face_nam = []
            try:
                for image in os.scandir('faces'):
                    face_image = fr.load_image_file(image.path)
                    face_encoding = fr.face_encodings(face_image)[0]
                    self.fam_face_enc.append(face_encoding)
                    self.fam_face_nam.append(image.name)
            except (FileNotFoundError):
                os.mkdir('faces')
                for image in os.scandir('faces'):
                    face_image = fr.load_image_file(image.path)
                    face_encoding = fr.face_encodings(face_image)[0]
                    self.fam_face_enc.append(face_encoding)
                    self.fam_face_nam.append(image.name)
                    with open('cache.pkl', 'wb') as f:
                        pickle.dump((self.fam_face_enc, self.fam_face_nam), f)

    def run_recog(self):
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            sys.exit('No camera detected')

        while True:
            ret, frame = video_capture.read()

            if self.detect_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

                self.face_loc = fr.face_locations(small_frame)
                self.face_enc = fr.face_encodings(small_frame, self.face_loc)

                for face_encoding in self.face_enc:
                    match = fr.compare_faces(self.fam_face_enc, face_encoding)
                    face_distances = fr.face_distance(self.fam_face_enc, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if match[best_match_index]:
                        name_with_extension = self.fam_face_nam[best_match_index]
                        name = os.path.splitext(name_with_extension)[0]

                        if name not in self.face_nam:
                            self.face_nam.append(name)
                            list_att(name, file_path)

            self.detect_frame = not self.detect_frame

            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

    def start_detect(self):
        path = 'faces'
        event_handler = Watcher(self)
        Observer().schedule(event_handler, path, recursive=False)
        Observer().start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            Observer().stop()
        Observer().join()

def run():
    fri = FaceRecognition()
    threading.Thread(target=fri.start_detect).start()
    fri.run_recog()
    

if __name__ == '__main__':
    frc_th = threading.Thread(target=run)
    frc_th.start()
    csvmak()
    app.run()