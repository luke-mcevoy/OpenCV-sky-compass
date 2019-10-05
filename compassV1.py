# Luke McEvoy
# Digital Compass

# Algorithm that determines compass orientation of user
# anywhere in world when devices is pointed at the sun

import pandas as pd
import numpy as np
import datetime
import cv2
import matplotlib.pyplot as plt
import math
from math import cos, sin
import sched, time
from PIL import Image


#VARIABLES
# excel file of azimuth readings for user's current location
excel_file = '/Users/lukemcevoy/Desktop/excelTutorial/huntington_large_test.xlsx'

# extracts datafranes from the excel document
df = pd.read_excel(excel_file)

#takes the current time of when the application is ran
now = pd.datetime.now()

# METHODS

# compares the current time to the times of excel
# data frame and determines the closest one
def timeComp(df): 
    i = 1
    while (now.hour > df.iloc[i,0].hour):
        i = i + 1
    while now.minute > df.iloc[i,0].minute:
        i = i + 1
    return compassValue(df.iloc[i,2])

# uses a dictionary of compass orientations and
# finds the value closest to given azimuth value
def compassValue(azimuth):
    d = { 
    'N' : 0.0,
    'NbE' : 11.25,
    'NNE' : 22.5,
    'NEbN' : 33.75,
    'NE' : 45.0,
    'NEbE' : 56.25,
    'ENE' : 67.5,
    'EbN' : 78.75,
    'E' : 90.0,
    'EbS' : 101.25,
    'ESE' : 112.5,
    'SEbE' : 123.75,
    'SE' : 135.0,
    'SEbS' : 146.25,
    'SSE' : 157.5,
    'SbE' : 168.75,
    'S' : 180.0,
    'SbW' : 191.25,
    'SSW' : 202.5,
    'SWbS' : 213.75,
    'SW' : 225.0,
    'SWbW' : 236.25,
    'WSW' : 247.5,
    'WbS' : 258.75,
    'W' : 270.0,
    'WbN' : 281.25,
    'WNW' : 292.5,
    'NWbW' : 303.75,
    'NW' : 315.0,
    'NWbN' : 362.25,
    'NNW' : 337.5,
    'NbW' : 348.75
     }
    for key in d:
        if azimuth <= d[key]:
            return d.get(key)

# main function for calculations off of
# livestream of handheld device
def cameraComp(direction):
    
    def Reverse(tuples): 
        new_tup = tuples[::-1] 
        return new_tup

    # finds the highest pixel value which
    # is the sun
    def findMax(frame):
        conv = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        arr = np.array(conv)
        vertex = np.unravel_index(arr.argmax(), arr.shape)
        return Reverse(vertex)
    
    # initiates livestream
    cap = cv2.VideoCapture(0)

    # determines the width and height of
    # the livestream for later calculations
    global width
    global height    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # writes the livestream to the computer screen
    writer = cv2.VideoWriter('webCamLive.mp4', cv2.VideoWriter_fourcc(*'XVID'), 20, (width,height))

    # image of compass on users screen that turns
    # in sync with changing position of sun to show
    # the user's compass orientation
    speedo = Image.open('compass.png').convert('RGBA')
    speedo = speedo.rotate(direction)
    w, h = speedo.size
        
    while True:
        def rotateHelper(speedo, answer, width, height):
            if x <= width//2 and y <= height//2:
                speedo = speedo.rotate(degreeTurn)
            elif x >= width//2 and y <= height//2:
                speedo = speedo.rotate(270 + degreeTurn)
            elif x >= width//2 and y >= height//2:
                speedo  = speedo.rotate(180 + degreeTurn)
            else:
                speedo = speedo.rotate(90 + degreeTurn)
            return speedo
        
        ret, frame = cap.read()
        global answer
        answer = findMax(frame)
        global x,y
        x = answer[0]
        y = answer[1]
        degreeTurn = dictionaryHelper(dictionary())
        pilim = Image.fromarray(frame)
        newSpeedo = rotateHelper(speedo, answer, width, height)
        pilim.paste(newSpeedo,box=((width-w)//2,(height-h)//2),mask=newSpeedo)
        frame = np.array(pilim)
        cv2.putText(frame, str(direction), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255),1)
        cv2.imshow('frame', frame)
        
        # kills livestream when the user presses 'esc'
        if cv2.waitKey(1) & 0XFF == 27:
            break
            
    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    
# divides the livestream into grids and 
def dictionary():
    
    incX = width//20
    incY = height//12
    centerX = width//2
    centerY = height//2
    
    def higher(var, axis):
        i = 0
        if axis == 0:
            answer = centerX
            while var >= answer:
                answer = answer + incX
                i = i + 1
            if i == 11:
                i = i - 1
            return i
        else :
            answer = centerY
            while var >= answer:
                answer = answer + incY
                i = i + 1
            if i == 7:
                i = i - 1
            return i

    def lower(var, axis):
        i = 0
        if axis == 0:
            answer = centerX
            while var <= answer:
                answer = answer - incX
                i = i + 1
            if i == 11:
                i = i - 1
            return i
        else :
            answer = centerY
            while var <= answer:
                answer = answer - incY
                i = i + 1
            if i == 7:
                i = i - 1
            return i

    def quadTest():
        global quad
        if x >= width//2 and y <= height//2:
            quad = 1
            return str(higher(x, 0)) + 'x ' + str(lower(y, 1)) + 'y'
        elif x <= width//2 and y <= height//2:
            quad = 2
            return str(lower(x, 0)) + 'x ' + str(lower(y, 1)) + 'y'
        elif x <= width//2 and y >= height//2:
            quad = 3
            return str(lower(x, 0)) + 'x ' + str(higher(y, 1)) + 'y'
        else:
            quad = 4
            return str(higher(x, 0)) + 'x ' + str(higher(y, 1)) + 'y'

    d = {
        '1x 1y' : 45.0,
        '1x 2y' : 78.75,
        '1x 3y' : 90.0,
        '1x 4y' : 90.0,
        '1x 5y' : 90.0,
        '1x 6y' : 90.0,
        '2x 1y' : 28.125,
        '2x 2y' : 50.625,
        '2x 3y' : 73.125,
        '2x 4y' : 78.75,
        '2x 5y' : 84.375,
        '2x 6y' : 84.375,
        '3x 1y' : 11.25,
        '3x 2y' : 45.0,
        '3x 3y' : 61.875,
        '3x 4y' : 73.125,
        '3x 5y' : 73.125,
        '3x 6y' : 78.75,
        '4x 1y' : 5.625,
        '4x 2y' : 33.75,
        '4x 3y' : 50.625,
        '4x 4y' : 61.875,
        '4x 5y' : 67.5,
        '4x 6y' : 73.125,
        '5x 1y' : 5.625,
        '5x 2y' : 28.125,
        '5x 3y' : 39.375,
        '5x 4y' : 56.25,
        '5x 5y' : 61.875,
        '5x 6y' : 67.5,
        '6x 1y' : 5.625,
        '6x 2y' : 22.5,
        '6x 3y' : 33.75,
        '6x 4y' : 45.0,
        '6x 5y' : 56.25,
        '6x 6y' : 61.875,
        '7x 1y' : 5.625,
        '7x 2y' : 16.875,
        '7x 3y' : 28.125,
        '7x 4y' : 39.375,
        '7x 5y' : 50.625,
        '7x 6y' : 56.25,
        '8x 1y' : 5.625,
        '8x 2y' : 16.875,
        '8x 3y' : 28.125,
        '8x 4y' : 33.75,
        '8x 5y' : 45.0,
        '8x 6y' : 50.625,
        '9x 1y' : 5.625,
        '9x 2y' : 16.875,
        '9x 3y' : 22.5,
        '9x 4y' : 28.125,
        '9x 5y' : 39.375,
        '9x 6y' : 50.625,
        '10x 1y' : 5.625,
        '10x 2y' : 11.25,
        '10x 3y' : 16.875,
        '10x 4y' : 28.125,
        '10x 5y' : 39.375,
        '10x 6y' : 45.0,
    }
    temp = quadTest() 
    for key in d:
        if temp == key:
            return d[key]

# if the quadrant is 1 or 3 the readings
# are unaltered, else they are adjusted by 90
# degrees to compensate for geometrical reflection
def dictionaryHelper(degrees):
    if quad == 2 or quad == 4:
        return 90 - degrees
    else:
        return degrees

def main():
    cameraComp(timeComp(df))
    

if __name__ == "__main__":
    main()
