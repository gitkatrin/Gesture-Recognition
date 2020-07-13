<<<<<<< HEAD
#! /usr/bin/env python3

import copy # erlaubt Kopiervorgänge
import cv2 # Bibliothek zur Lösung von vision Problemen
import numpy as np # Daten werden in numpy arrays gespeichert
from keras.models import load_model # Keras API verwenden für DL
import time # ermöglicht viele zeitbezogene Funktionen
import paho.mqtt.client as mqtt
import json
import random
import string


# General Settings
prediction = ''
action = ''
score = 0
img_counter = 500




gesture_names = {0: 'Fist',
                 1: 'L',
                 2: 'Okay',
                 3: 'Palm',
                 4: 'Peace'}

# Öffne gespeichertes Modell / Gewichte aus der .h5-Datei
model = load_model('C:/Users/katri/Documents/Gesture-Recognition/VGG_cross_validated.h5')

def predict_rgb_image(img): #RGB Bild vom Bildschirm abrufen mit Keras 
    result = gesture_names[model.predict_classes(img)[0]] # mit keras, gibt Gesture im Array zurück
    print(result)
    return (result)


def predict_rgb_image_vgg(image):
    # Bild in ein NumPy-Array umwandeln
    image = np.array(image, dtype='float32') 
    image /= 255
    
    # ein Array von Wahrscheinlichkeiten zurückgeben
    pred_array = model.predict(image) 
    print(f'pred_array: {pred_array}')
    # den Index der höchsten Wahrscheinlichkeit erfassen
    result = gesture_names[np.argmax(pred_array)] 
    print(f'Result: {result}')
    print(max(pred_array[0]))
    score = float("%0.2f" % (max(pred_array[0]) * 100)) # float 0.2f, nur 2 Stellen hinter dem Dezimalpunkt anzeigen
    print(result)
    return result, score



# parameters
cap_region_x_begin = 0.5  # start point/total width
cap_region_y_end = 0.8  # start point/total width
threshold = 60  # binary threshold
blurValue = 41  # GaussianBlur parameter
bgSubThreshold = 50
learningRate = 0

# variableslt
isBgCaptured = 0  # bool, whether the background captured
triggerSwitch = False  # if true, keyboard simulator works


# Hintergrundsubtraktion
def remove_background(frame): 
    # Lernrate zum Aktualisieren des Hintergrundmodells
    fgmask = bgModel.apply(frame, learningRate=learningRate) 
    kernel = np.ones((3, 3), np.uint8)
    # erodiert die Grenzen des Vordergrundobjekts
    fgmask = cv2.erode(fgmask, kernel, iterations=1) 
    res = cv2.bitwise_and(frame, frame, mask=fgmask) 
    return res


# startet die Webcam und verwendet sie als Videoquelle
camera = cv2.VideoCapture(1)
camera.set(10, 200)

while camera.isOpened():
    ret, frame = camera.read() # ret gibt true zurück, wenn Kamera läuft. Der Frame erfasst jeden Frame des Video-Feeds
    frame = cv2.bilateralFilter(frame, 5, 50, 100)  # smoothing filter
    frame = cv2.flip(frame, 1)  # flip the frame horizontally
    cv2.rectangle(frame, (int(cap_region_x_begin * frame.shape[1]), 0),
                  (frame.shape[1], int(cap_region_y_end * frame.shape[0])), (255, 0, 0), 2)

    cv2.imshow('original', frame)

    # Run once background is captured
    if isBgCaptured == 1:
        img = remove_background(frame)
        img = img[0:int(cap_region_y_end * frame.shape[0]),
              int(cap_region_x_begin * frame.shape[1]):frame.shape[1]]  # Rahmen (ROI) aussschneiden
        cv2.imshow('mask', img)

        # convert the image into binary image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (blurValue, blurValue), 0)
        # cv2.imshow('blur', blur)
        ret, thresh = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Add prediction and action text to thresholded image
        # cv2.putText(thresh, f"Prediction: {prediction} ({score}%)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
        # cv2.putText(thresh, f"Action: {action}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))  # Draw the text
        # Draw the text
        cv2.putText(thresh, f"Prediction: {prediction} ({score}%)", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 255, 255)) #cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
        cv2.putText(thresh, f"Action: {action}", (10, 80), cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 255, 255))  # Draw the text
        cv2.imshow('ori', thresh)

        # get the contours
        thresh1 = copy.deepcopy(thresh)
        contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        length = len(contours)
        maxArea = -1
        if length > 0:
            for i in range(length):  # find the biggest contour (according to area)
                temp = contours[i]
                area = cv2.contourArea(temp)
                if area > maxArea:
                    maxArea = area
                    ci = i

            res = contours[ci]
            hull = cv2.convexHull(res)
            drawing = np.zeros(img.shape, np.uint8)
            cv2.drawContours(drawing, [res], 0, (0, 255, 0), 2)
            cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 3)

        cv2.imshow('output', drawing)

    # Keyboard OP
    k = cv2.waitKey(10)
    if k == 27:  # press ESC to exit all windows at any time
        break
    elif k == ord('b'):  # press 'b' to capture the background
        bgModel = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
        time.sleep(2)
        isBgCaptured = 1
        print('Background captured')
    elif k == ord('r'):  # press 'r' to reset the background
        time.sleep(1)
        bgModel = None
        triggerSwitch = False
        isBgCaptured = 0
        print('Reset background')
    elif k == 32: 
        # Wenn die Leertaste gedrückt wird
        cv2.imshow('original', frame)
        # copies 1 channel BW image to all 3 RGB channels
        target = np.stack((thresh,) * 3, axis=-1) # Stapel
        target = cv2.resize(target, (224, 224)) # Größe ändern
        target = target.reshape(1, 224, 224, 3) # Umformung
        prediction, score = predict_rgb_image_vgg(target) # Vorhersage
    

    elif k == ord('t'):

        print('Tracker turned on.')

        cap = cv2.VideoCapture(1)
        ret, frame = cap.read()

        # Select Region of Interest (ROI)
        r = cv2.selectROI(frame)

        # Crop image
        imCrop = frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

        # setup initial location of window
        r, h, c, w = 250, 400, 400, 400
        track_window = (c, r, w, h)
        # set up the ROI for tracking
        roi = imCrop
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        # Setup the termination criteria, either 10 iteration or move by at least 1 pt
        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        while (1):
            ret, frame = cap.read()
            if ret == True:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
                # apply meanshift to get the new location
                ret, track_window = cv2.CamShift(dst, track_window, term_crit)
                # Draw it on image
                pts = cv2.boxPoints(ret)
                pts = np.int0(pts)
                img2 = cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                cv2.imshow('img2', img2)
                k = cv2.waitKey(60) & 0xff
                if k == 27:  # if ESC key
                    break
                else:
                    cv2.imwrite(chr(k) + ".jpg", img2)
            else:
                break
        cv2.destroyAllWindows()
        cap.release()
        
        
    if prediction == 'Palm':
        action = "music off"  
    elif prediction == 'Fist':
        action = "music on"
    elif prediction == 'Okay':
        action = "volume up"
    elif prediction == 'Peace':
        action = "volume down"    
    elif prediction == 'L':
        action = "calling police"
        #Methode um Daten zu senden
        def sendData():
            topic = "/hshl/users/" #Das Topic in dem gesendet werden soll
            # Die Daten die gesendet werden sollen
            call = {
                "driver_name": "Katrin",
                "location": [51.67, 8.36], # Array mit Koordinaten
                "reasons": "police", # Array mit reasons
                "id": "k80"
                }
            client.publish(topic, json.dumps(call))
            print("sendet")
        def on_connect(client, userdata, flags, rc):
            client.subscribe('/hshl/users/')
            print("subscribed to the users topic!")
            sendData()  # Aufruf der Senden Methode
        
        # Dont change anything from here!!
        BROKER_ADDRESS = "mr2mbqbl71a4vf.messaging.solace.cloud"  # Adresse des MQTT Brokers
        client = mqtt.Client()

        client.on_connect = on_connect  # Zuweisen des Connect Events
        # Benutzernamen und Passwort zur Verbindung setzen
        client.username_pw_set("solace-cloud-client", "nbsse0pkvpkvhpeh3ll5j7rpha")
        client.connect(BROKER_ADDRESS, port=20614)  # Verbindung zum Broker aufbauen

        print("Connected to MQTT Broker: " + BROKER_ADDRESS)
        #client.loop_forever()  # Endlosschleife um neue Nachrichten empfangen zu können
        #time.sleep(4)
        #client.loop_stop()
        #client.disconnect() # disconnect when get message
        if prediction == 'L':
            client.loop_forever()
        else:
            client.loop_stop()
    else:
        pass


=======
#! /usr/bin/env python3

import copy # erlaubt Kopiervorgänge
import cv2 # Bibliothek zur Lösung von vision Problemen
import numpy as np # Daten werden in numpy arrays gespeichert
from keras.models import load_model # Keras API verwenden für DL
import time # ermöglicht viele zeitbezogene Funktionen
import paho.mqtt.client as mqtt
import json
import random
import string


# General Settings
prediction = ''
action = ''
score = 0
img_counter = 500




gesture_names = {0: 'Fist',
                 1: 'L',
                 2: 'Okay',
                 3: 'Palm',
                 4: 'Peace'}

# Öffne gespeichertes Modell / Gewichte aus der .h5-Datei
model = load_model('C:/Users/katri/Documents/Gesture-Recognition/VGG_cross_validated.h5')

def predict_rgb_image(img): #RGB Bild vom Bildschirm abrufen mit Keras 
    result = gesture_names[model.predict_classes(img)[0]] # mit keras, gibt Gesture im Array zurück
    print(result)
    return (result)


def predict_rgb_image_vgg(image):
    # Bild in ein NumPy-Array umwandeln
    image = np.array(image, dtype='float32') 
    image /= 255
    
    # ein Array von Wahrscheinlichkeiten zurückgeben
    pred_array = model.predict(image) 
    print(f'pred_array: {pred_array}')
    # den Index der höchsten Wahrscheinlichkeit erfassen
    result = gesture_names[np.argmax(pred_array)] 
    print(f'Result: {result}')
    print(max(pred_array[0]))
    score = float("%0.2f" % (max(pred_array[0]) * 100)) # float 0.2f, nur 2 Stellen hinter dem Dezimalpunkt anzeigen
    print(result)
    return result, score



# parameters
cap_region_x_begin = 0.5  # start point/total width
cap_region_y_end = 0.8  # start point/total width
threshold = 60  # binary threshold
blurValue = 41  # GaussianBlur parameter
bgSubThreshold = 50
learningRate = 0

# variableslt
isBgCaptured = 0  # bool, whether the background captured
triggerSwitch = False  # if true, keyboard simulator works


# Hintergrundsubtraktion
def remove_background(frame): 
    # Lernrate zum Aktualisieren des Hintergrundmodells
    fgmask = bgModel.apply(frame, learningRate=learningRate) 
    kernel = np.ones((3, 3), np.uint8)
    # erodiert die Grenzen des Vordergrundobjekts
    fgmask = cv2.erode(fgmask, kernel, iterations=1) 
    res = cv2.bitwise_and(frame, frame, mask=fgmask) 
    return res


# startet die Webcam und verwendet sie als Videoquelle
camera = cv2.VideoCapture(1)
camera.set(10, 200)

while camera.isOpened():
    ret, frame = camera.read() # ret gibt true zurück, wenn Kamera läuft. Der Frame erfasst jeden Frame des Video-Feeds
    frame = cv2.bilateralFilter(frame, 5, 50, 100)  # smoothing filter
    frame = cv2.flip(frame, 1)  # flip the frame horizontally
    cv2.rectangle(frame, (int(cap_region_x_begin * frame.shape[1]), 0),
                  (frame.shape[1], int(cap_region_y_end * frame.shape[0])), (255, 0, 0), 2)

    cv2.imshow('original', frame)

    # Run once background is captured
    if isBgCaptured == 1:
        img = remove_background(frame)
        img = img[0:int(cap_region_y_end * frame.shape[0]),
              int(cap_region_x_begin * frame.shape[1]):frame.shape[1]]  # Rahmen (ROI) aussschneiden
        cv2.imshow('mask', img)

        # convert the image into binary image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (blurValue, blurValue), 0)
        # cv2.imshow('blur', blur)
        ret, thresh = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Add prediction and action text to thresholded image
        # cv2.putText(thresh, f"Prediction: {prediction} ({score}%)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
        # cv2.putText(thresh, f"Action: {action}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))  # Draw the text
        # Draw the text
        cv2.putText(thresh, f"Prediction: {prediction} ({score}%)", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 255, 255)) #cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
        cv2.putText(thresh, f"Action: {action}", (10, 80), cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 255, 255))  # Draw the text
        cv2.imshow('ori', thresh)

        # get the contours
        thresh1 = copy.deepcopy(thresh)
        contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        length = len(contours)
        maxArea = -1
        if length > 0:
            for i in range(length):  # find the biggest contour (according to area)
                temp = contours[i]
                area = cv2.contourArea(temp)
                if area > maxArea:
                    maxArea = area
                    ci = i

            res = contours[ci]
            hull = cv2.convexHull(res)
            drawing = np.zeros(img.shape, np.uint8)
            cv2.drawContours(drawing, [res], 0, (0, 255, 0), 2)
            cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 3)

        cv2.imshow('output', drawing)

    # Keyboard OP
    k = cv2.waitKey(10)
    if k == 27:  # press ESC to exit all windows at any time
        break
    elif k == ord('b'):  # press 'b' to capture the background
        bgModel = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
        time.sleep(2)
        isBgCaptured = 1
        print('Background captured')
    elif k == ord('r'):  # press 'r' to reset the background
        time.sleep(1)
        bgModel = None
        triggerSwitch = False
        isBgCaptured = 0
        print('Reset background')
    elif k == 32: 
        # Wenn die Leertaste gedrückt wird
        cv2.imshow('original', frame)
        # copies 1 channel BW image to all 3 RGB channels
        target = np.stack((thresh,) * 3, axis=-1) # Stapel
        target = cv2.resize(target, (224, 224)) # Größe ändern
        target = target.reshape(1, 224, 224, 3) # Umformung
        prediction, score = predict_rgb_image_vgg(target) # Vorhersage
    

    elif k == ord('t'):

        print('Tracker turned on.')

        cap = cv2.VideoCapture(1)
        ret, frame = cap.read()

        # Select Region of Interest (ROI)
        r = cv2.selectROI(frame)

        # Crop image
        imCrop = frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

        # setup initial location of window
        r, h, c, w = 250, 400, 400, 400
        track_window = (c, r, w, h)
        # set up the ROI for tracking
        roi = imCrop
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        # Setup the termination criteria, either 10 iteration or move by at least 1 pt
        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        while (1):
            ret, frame = cap.read()
            if ret == True:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
                # apply meanshift to get the new location
                ret, track_window = cv2.CamShift(dst, track_window, term_crit)
                # Draw it on image
                pts = cv2.boxPoints(ret)
                pts = np.int0(pts)
                img2 = cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                cv2.imshow('img2', img2)
                k = cv2.waitKey(60) & 0xff
                if k == 27:  # if ESC key
                    break
                else:
                    cv2.imwrite(chr(k) + ".jpg", img2)
            else:
                break
        cv2.destroyAllWindows()
        cap.release()
        
        
    if prediction == 'Palm':
        action = "music off"  
    elif prediction == 'Fist':
        action = "music on"
    elif prediction == 'Okay':
        action = "volume up"
    elif prediction == 'Peace':
        action = "volume down"    
    elif prediction == 'L':
        action = "calling police"
        #Methode um Daten zu senden
        def sendData():
            topic = "/hshl/users/" #Das Topic in dem gesendet werden soll
            # Die Daten die gesendet werden sollen
            call = {
                "driver_name": "Katrin",
                "location": [51.67, 8.36], # Array mit Koordinaten
                "reasons": "police", # Array mit reasons
                "id": "k80"
                }
            client.publish(topic, json.dumps(call))
            print("sendet")
        def on_connect(client, userdata, flags, rc):
            client.subscribe('/hshl/users/')
            print("subscribed to the users topic!")
            sendData()  # Aufruf der Senden Methode
        
        # Dont change anything from here!!
        BROKER_ADDRESS = "mr2mbqbl71a4vf.messaging.solace.cloud"  # Adresse des MQTT Brokers
        client = mqtt.Client()

        client.on_connect = on_connect  # Zuweisen des Connect Events
        # Benutzernamen und Passwort zur Verbindung setzen
        client.username_pw_set("solace-cloud-client", "nbsse0pkvpkvhpeh3ll5j7rpha")
        client.connect(BROKER_ADDRESS, port=20614)  # Verbindung zum Broker aufbauen

        print("Connected to MQTT Broker: " + BROKER_ADDRESS)
        #client.loop_forever()  # Endlosschleife um neue Nachrichten empfangen zu können
        #time.sleep(4)
        #client.loop_stop()
        #client.disconnect() # disconnect when get message
        if prediction == 'L':
            client.loop_forever()
        else:
            client.loop_stop()
    else:
        pass


>>>>>>> b425c431c1c4d41685d19b05921216da55d14ae0
