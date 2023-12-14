import numpy as np
import cv2


face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
# 눈 감지 eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye_tree_eyeglasses.xml')
profileface_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_profileface.xml')
cap = cv2.VideoCapture(0) 
cap.set(4,640) 
cap.set(5,480) 

while(True):
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1) 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray,1.05, 5)
    # 눈 감지
    #eyes = eye_cascade.detectMultiScale(gray, scaleFactor= 1.5, minNeighbors=3, minSize=(10,10))
    profile = face_cascade.detectMultiScale(gray,1.05,5)
    print("Number of faces detected: " + str(len(faces)))

    if len(faces):
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    # 눈 감지
    '''if len(eyes) :
        for  x, y, w, h in eyes :
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0,0,255), 2, cv2.LINE_4)''' 
    if len(profile):
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    cv2.imshow('result', frame)
    
    k = cv2.waitKey(30) & 0xff
    if k == 27: 
        break