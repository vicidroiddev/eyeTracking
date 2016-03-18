import time
from Analyzer import Analyzer
from db import Database
import sys
import logging
import os
import Utils
from debug import FeatureDebug
from learning.ParamsConstructor import ParamsConstructor
import math

if FeatureDebug.COMPARE_WITH_MATPLOTLIB:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib import pyplot as plt

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

DEFAULT_DIRECTORY = 'imageLeftCam'
IMAGE_DIRECTORY = './processing/'
PROCESSING_DIR = 'processing/'
PROCESSING_DIR_JAN_11 = 'image/Jan11'
PROCESSING_DIR_JAN_13 = 'image/tim_jan13'
TEST_DIR = 'image/DISTANCE_IMAGE'
TEST_DB = 'db-tim_distance'
PROCESSING_DIR_READING = 'image/READING_IMAGE'


# def compareResults(results, THRESHOLD=20):
#    annotated , (truthX, truthY) = Database.getTruth(results.getFileName())
#
#    if annotated:
#
#        for entry in results.getHeuristics():
#            heuristic = entry.itervalues().next()
#            xDiff = abs(heuristic['x'] - truthX)
#            yDiff = abs(heuristic['y'] - truthY)
#
#            if xDiff < THRESHOLD and yDiff < THRESHOLD:
#                pass
#                # print 'SUCCESS'


# global dist_error
dist_error = []
successCount = 0
totalImages = 0

global db
db = Database.Database(databaseName=TEST_DB)

def compareResults(img_file, pupil):
    global successCount
    global dist_error

    annotated , (truthX, truthY) = db.getTruth(img_file)

    if annotated:
        successCount += 1
        deltaX = (pupil[0] - truthX)
        deltaY = (pupil[1] - truthY)
            
        errorLen = math.sqrt(deltaX**2 + deltaY**2)
        logger.info('error: %s', errorLen)

        dist_error.append(errorLen)

def logStats():
    logger.info('Final Stats: \n\t Successful Pupils Detected: {} \n\t Total Images: {} \n\t Success Rate: {}'.format(successCount, totalImages, successCount/totalImages))
    pass

def processImages():
    global totalImages
    os.chdir(TEST_DIR)


    params = ParamsConstructor().constructDefaultParams()

    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('jpg') or f.endswith('jpeg') ]
    totalImages = len(files)
    for image in files:

        analysis = Analyzer(image, params)
        eyeData = analysis.getEyeData()

        (x,y) = eyeData.getRandomPupilTruth()
        reflections = eyeData.getReflection()

        if reflections:
            (xReflect, yReflect) = (reflections[0]['x'], reflections[0]['y'])
            logger.info('Reflection Location : x: {}, y: {}'.format(xReflect,yReflect))
        else:
            (xReflect, yReflect) = (-1, -1)

        # logger.info('Random Pupil Truth: x: {}, y: {}'.format(x,y))
        logger.info(image)
        if FeatureDebug.COMPARE_WITH_MATPLOTLIB:
            compareResults(image, [xReflect,yReflect])

    logStats()

    if  FeatureDebug.COMPARE_WITH_MATPLOTLIB:
        plt.hist(dist_error, bins=100)
        plt.title(TEST_DIR)
        plt.xlabel('pixel distance')
        plt.ylabel('counts')
        plt.show()




if  __name__ == '__main__':

    if Utils.isBeagalBone():
        raise AssertionError('Do not start this on the beaglebone system, use StartBB.py instead.')

    processImages()

