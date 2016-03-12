import pprint
import sys

import cv2
import numpy as np
import logging

from ip.Blob import Blob
from db.Eyeball import Eyeball
from ip.ReflectionReduction import ReflectionReduction
from learning import Parameters
from ip.CornerDetection import CornerDetection
from debug import DebugOptions as tb, FeatureDebug
from ImageHelper import ImageHelper
from ip.Morphology import Morphology
from ip.PupilDetector import PupilDetector
from ip.Threshold import Threshold
import Utils
from ip.EdgeDetection import EdgeDetection
from learning.ParamsConstructor import ParamsConstructor

selecting = False
startX = -1
startY = -1

INVALID = -1

COLOR_WHITE_LB = np.array([0,0,0])
COLOR_WHITE_UB = np.array([151,35,95])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

def close():
    cv2.destroyAllWindows()

def forceExit():
    cv2.destroyAllWindows()
    sys.exit()

class Analyzer:

    def __init__(self, src, params=None):

        if isinstance(src, basestring):
            self.originalImage = cv2.imread(src)

        if isinstance(src, list):
            leBuf = np.asarray(bytearray(src))
            self.originalImage = cv2.imdecode(leBuf, 1)

        if self.originalImage is None:
            raise ValueError('Failed to get image with src: ' + src)
        else:
            self.cameraType = 0 # deprecated
            self.eyeball = Eyeball(src)
            self.fileName = src
            self.params = ParamsConstructor().constructDefaultParams() if params is None else params
            self.imgWidth, self.imgHeight = self.originalImage.shape[:2]
            self.imgIndex = 0
            self.__analyze__()



    def __analyze__(self):

        originalImage = self.originalImage.copy()
        self.imageCanny = self.originalImage.copy()

        ImageHelper.showImage('Original Image', originalImage)

        #Invert image with ~ and convert to grayscale
        processedImage = cv2.cvtColor(~originalImage, cv2.COLOR_BGR2GRAY)
        ImageHelper.showImage('Grey Image', processedImage)

        if FeatureDebug.BLOB_DETECTOR:
            blobbed = Blob(processedImage).detect()
            ImageHelper.showImage('BLOBBED', blobbed)

        if FeatureDebug.THRESHOLD:
            thresholder = Threshold(processedImage, self.cameraType, self.params)
            processedImage = thresholder.getBinaryThreshold()
            thresholder.getAdaptiveThreshold(150, 3, -5)

        #Clean up the binary threshold image to get a better pupil representation
        if FeatureDebug.MORPHOLOGY:
            morpher = Morphology(self.processedImage)
            processedImage = morpher.cleanImage()

        self.pupilDetector = PupilDetector(originalImage, processedImage, self.cameraType, self.params, self.eyeball)
        self.pupilDetector.doHoughTransform()
        self.pupilDetector.findPupilCircle()

        if FeatureDebug.PRINT_HEURISTICS:
            self.printDebugInfo()

        if Utils.isMac() and FeatureDebug.SHOW_CV2_IMAGES:
            self.waitForKeyPress()

    def getEyeData(self):
        return self.eyeball

    def printDebugInfo(self):
        print '\n Heuristics:'
        pprint.pprint(self.eyeball.dict['heuristics'])

    def waitForKeyPress(self, delay=None):
        print 'Waiting for key press....'
        if  delay is None:
            keyPressed =  cv2.waitKey()
        else:
            keyPressed = cv2.waitKey(delay)

        if keyPressed == ord('n'):
            cv2.destroyAllWindows()
        elif keyPressed == ord('e'):
            forceExit()