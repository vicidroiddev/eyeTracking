import cv2
import math
import numpy as np
import CV_
import Parameters
from ImageHelper import ImageHelper

__author__ = 'Raphael'

MIN_AREA = 30 #the min value for creating circles
RED = (0,0,255)
GREEN = (0,255,0)
BLUE = (255,0,0)
DIFF_VALUES = 1
DP = 10 #Dimension in circle space (lower is faster to compute)
CROSSHAIRS = 5
PRINTDEBUG = True

HOUGH_PARAM1 = 1
HOUGH_MAX_PARAM2 = 300
HOUGH_MIN_RADIUS = 0
HOUGH_MAX_RADIUS = 40
HOUGH_MIN_DIST = 20 # the minimum distance two detected circles can be from one another
HOUGH_MAX_ATTEMPTS = 100 #define the number of attempts to find at least one circle

PARAM1 = 'param1'
PARAM2 = 'param2'
MIN_RAD = 'minRadius'
MAX_RAD = 'maxRadius'

DP = 10 #Dimension in circle space (lower is faster to compute)

#Values
DEBUG_RECT = 'Rect'
DEBUG_CENTER = 'Center'
DEBUG_RADIUS = 'Radius'
DEBUG_CANDIDATE_CORNER = 'CandidateCorner'

class PupilDetector(object):

    def __init__(self, originalImg, processedImg, cameraType, callback, params = None):
        self.originalImg = originalImg
        self.processedImg = processedImg
        self.cameraType = cameraType
        self.callback = callback
        self.params = params

    def doHoughTransform(self, param1=None, param2 = None, minRadius = None, maxRadius = None):

        # houghTransformed = self.processedImg.copy()
        result = self.originalImg.copy()

        if param1 is None or param2 is None or minRadius is None or maxRadius is None:
            (param1, param2, minRadius, maxRadius) = self.params.HoughParamaters.getParams(self.cameraType)
            # houghMinDistance = HOUGH_MIN_DIST

        houghCircles = CV_.HoughCirclesWithDefaultGradient(self.processedImg, DP, HOUGH_MIN_DIST,
                                   None, param1, param2, minRadius, maxRadius)

        if houghCircles is not None:
            # self.saveInfo({('Hough Circle', True)})
            circles = np.round(houghCircles[0, :]).astype("int")
            for (x,y,r) in circles:
                cv2.circle(result, (x,y), r, GREEN, 1)
                cv2.line(result,(x - CROSSHAIRS, y - CROSSHAIRS),(x + CROSSHAIRS, y + CROSSHAIRS), RED, 1)
                cv2.line(result,(x + CROSSHAIRS, y - CROSSHAIRS),(x - CROSSHAIRS, y + CROSSHAIRS), RED, 1)

                ImageHelper.showImage('Hough Circle', result)
        else:
            # self.saveInfo({('Hough Circle', False)})
            pass

    def findPupilCircle(self):

        pupilStats = {}

        circleDetectedImage = self.processedImg.copy()
        result = self.originalImg.copy()

        #Fill in contours
        contours, hierachy = CV_.findContours(circleDetectedImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(circleDetectedImage, contours, -1, (255,255,255), -1)
        # Imager.showImage("Fill in contours", srcImage)


        for contour in contours:
            area = cv2.contourArea(contour)
            x,y,width,height = cv2.boundingRect(contour)
            radius = width/2

            #DEBUGGING
            # if area > 0:
            #     print "Area: " + str(area)
            # if width != 0 and height != 0 and radius != 0:
            #     print "Diff1: " + str(abs(1 - width/height))
            #     print "Diff2: " + str(abs(1 - area/(math.pi * math.pow(radius, 2))))


            if  (   area >= MIN_AREA and
                    abs(1 - width/height) <= DIFF_VALUES and
                    abs(1 - area/(math.pi * math.pow(radius, 2))) < DIFF_VALUES):

                # print "Diff1: " + str(abs(1 - width/height))
                # print "Diff2: " + str(abs(1 - area/(math.pi * math.pow(radius, 2))))

                center = (x + radius, y + radius)
                cv2.line(result,(x, y + radius),(x + radius*2, y + radius),(0,0,255),1)
                cv2.line(result,(x + radius, y + radius *2),(x + radius, y),(0,0,255),1)
                cv2.circle(result, center, radius, RED, 1)

                ImageHelper.showImage('Pupil Circle', result)

                self.callback({('DEBUG_RADIUS', radius), ('DEBUG_CENTER', center), ('DEBUG_RECT', (x,y,width,height))})

                # self.saveInfo({(DEBUG_RADIUS, radius), (DEBUG_CENTER, center), (DEBUG_RECT, (x,y,width,height))})

