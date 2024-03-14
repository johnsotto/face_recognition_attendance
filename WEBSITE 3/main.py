import os, sys
import face_recognition as fr 
import numpy as np
import cv2
import pickle
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from app import *
import threading


class Watcher(FileSystemEventHandler):
    def __init__(self, face_recognition_instance):
        self.face_recognition_instance = face_recognition_instance

    def on_created(self, event):
        print(f'New file detected: {event.src_path}')
        self.face_recognition_instance.encode_faces()

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

    def start_watching_faces_directory(self):
        path = 'faces'
        event_handler = Watcher(self)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

def run():
    face_recognition_instance = FaceRecognition()
    threading.Thread(target=face_recognition_instance.start_watching_faces_directory).start()
    face_recognition_instance.run_recog()

if __name__ == '__main__':
    frc_th = threading.Thread(target=run)
    frc_th.start()
    app.run(debug=True)