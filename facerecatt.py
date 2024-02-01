import os, sys
import face_recognition as fr 
import numpy as np
import cv2
import math
import csv
from datetime import datetime

date_now = datetime.now().strftime("%Y-%m-%d")
file_path = os.path.join('attendance', date_now + '.csv')   

#make csv
def csvmak():   
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            csvr = csv.writer(file)
            names = []
            Header = f'Name, Time'
            Header = Header.split(',')
            names.insert(0, Header)
            csvr.writerows(names)
csvmak()
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
            
#class for fr
class FaceRecognition:
    face_loc = []
    face_enc = []
    face_nam= []
    fam_face_enc = []
    fam_face_nam = []
    detect_frame = True
    
    def __init__(self):
        self.encode_faces()
        
        
    #encode faces to fam_fac
    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = fr.load_image_file(f'faces/{image}')
            face_encoding = fr.face_encodings(face_image)[0]
            self.fam_face_enc.append(face_encoding)
            self.fam_face_nam.append(image)
            
    #main program
    def run_recog(self):
        video_capture = cv2.VideoCapture(0) 
        if not video_capture.isOpened():
            sys.exit('No camera detected')
            
        
        while True:
            ret, frame = video_capture.read()
            
            if self.detect_frame:
                small_frame = cv2.resize(frame,(0, 0), fx = .25, fy = .25)
                
                self.face_loc = fr.face_locations(small_frame)
                self.face_enc = fr.face_encodings(small_frame, self.face_loc)
                
                self.face_nam = []
                
                for i in self.face_enc:
                    match = fr.compare_faces(self.fam_face_enc, i) 
                    
                    face_distances = fr.face_distance(self.fam_face_enc,i)
                    
                    best_match = np.argmin(face_distances)
                    
                    
                    
                    if match[best_match]:
                        name = self.fam_face_nam[best_match]
                        
                        
                    name = os.path.splitext(name)[0]
                    self.face_nam.append(f'{name}')
                    
            self.detect_frame = not self.detect_frame
                
            #box display
            for (top, right, bottom , left), name in zip(self.face_loc, self.face_nam):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                cv2.rectangle(frame, (left, top) , (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 20) , (right, bottom), (0, 255, 0), -1)
                cv2.putText(frame, name, (left + 8, bottom - 8), cv2.FONT_HERSHEY_DUPLEX, .8, (255,255,255), 1)
                list_att(name, file_path)
            
            cv2.imshow('Face Recognition', frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
            
        video_capture.release()
        cv2.destroyAllWindows()
                    
if __name__ == '__main__':
    frc = FaceRecognition()
    frc.run_recog()