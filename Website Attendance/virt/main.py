import os, sys
import face_recognition as fr 
import numpy as np
import cv2
from timestamps import marked
import pickle


class FaceRecognition:
    face_loc = []
    face_enc = []
    face_nam= []
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
            for image in os.scandir('faces'):
                face_image = fr.load_image_file(image.path)
                face_encoding = fr.face_encodings(face_image)[0]
                self.fam_face_enc.append(face_encoding)
                self.fam_face_nam.append(image.name)
            with open('cache.pkl', 'wb') as f:
                pickle.dump((self.fam_face_enc, self.fam_face_nam), f)
            
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
                    if name not in self.face_nam:
                        marked(name)
                        self.face_nam.append(f'{name}')

                
                    

                    
            self.detect_frame = not self.detect_frame
            
            cv2.imshow('Face Recognition', frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
            
        video_capture.release()
        cv2.destroyAllWindows()
                    
if __name__ == '__main__':
    frc = FaceRecognition()
    frc.run_recog()