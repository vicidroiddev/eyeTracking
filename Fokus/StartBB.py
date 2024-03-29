from multiprocessing import Process, Lock, Pipe
import sys
import time
from Analyzer import Analyzer
from actuation import Actuate
import db
from eyeVergence.BinaryTree import DecisionTree
import Utils
import logging

sys.path.insert(0, '../pyCam/')
import Cam

from learning.ParamsConstructor import ParamsConstructor

__author__ = 'Raphael'

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logger = logging.getLogger(__name__)

loggerRetrieval = logging.getLogger("ImageRetrieval")
loggerProcessor = logging.getLogger("Processing")

#GLOBAL VARS
PARAMS = ParamsConstructor().constructDefaultParams()
IMAGE_DIRECTORY = './processing/'
TREE_DIRECTORY = './eyeVergence/trees/tree1.csv'
ANALYZE_IMAGES = True #warning threadsafety
RETRIEVE_IMAGES = True #warning threadsafety


def retrieveImageBB(imageDir, pipe, captureDelay):
    loggerRetrieval.info('Init Camera Loop')

    # initialize cameras
    camRight = Cam.Cam(IMAGE_DIRECTORY, "R")
    camLeft = Cam.Cam(IMAGE_DIRECTORY, "L")

    # looping to capture and process images
    # for i in range(1,100):
    while RETRIEVE_IMAGES:
        timestamp = int(time.time())
        camRight.takeImg()
        camLeft.takeImg()

        rightImg = camRight.getImg(timestamp)
        leftImg = camLeft.getImg(timestamp)

        #Send images through the pipe to be received by the Analyzer
        pipe.send(leftImg)
        pipe.send(rightImg)

        if captureDelay:
            time.sleep(captureDelay)

    # close connections to cameras
    camLeft.closeConn()
    camRight.closeConn()


def analyzeImageBB(pipe):

    loggerProcessor.info('Init Analyzing Loop')

    dTree = DecisionTree()
    dTree.importTree(TREE_DIRECTORY)

    motor = Actuate.Actuate("P8_13","P9_14", 3,-1)
    motor.startup()
    motor.actuate("FAR")

    currentPrescription = "FAR"
    
    while ANALYZE_IMAGES:
        pass

        leftImg = pipe.recv()
        rightImg = pipe.recv()

        if leftImg is not None and rightImg is not None:
            ipTime = int(time.time())
            (xL, yL) = Analyzer(leftImg).getEyeData().getPupilCentreCandidate(db.Eyeball.Eyeball.FilterOptions.REFLECTION)
            (xR, yR) = Analyzer(rightImg).getEyeData().getPupilCentreCandidate(db.Eyeball.Eyeball.FilterOptions.REFLECTION)
            loggerProcessor.info('Got x: {} y: {}'.format(xL, yL))
            loggerProcessor.info('Got x: {} y: {}'.format(xR, yR))
            
            if all(v != -1 for v in (xL, yL, xR, yR)):
#                pupils = {'x1': xR, 'x2': yR, 'x3': xL,'x4': yL}
                pupils = {'x1': yR, 'x2': xR, 'x3': yL,'x4': xL}
                prescription = dTree.traverseTree(pupils, dTree.root) 
                loggerProcessor.info('vergence computed: %s', prescription)

                if currentPrescription is not prescription:
                    motor.actuate(prescription)
                    currentPrescription = prescription
        else:
            loggerProcessor.error('Image was none')

if  __name__ == '__main__':

    if not Utils.isBeagalBone():
        raise AssertionError('The system was meant for the beaglebone! Use a different Start.py file')

    # Pipe for connecting retrieval to analysis
    analyzePipe, retrievePipe = Pipe()

#    imageRetrieval = Process(target=retrieveImageBB, name = "CAMERA", args=(IMAGE_DIRECTORY, retrievePipe, 1))
    imageRetrieval = Process(target=retrieveImageBB, name = "CAMERA", args=(IMAGE_DIRECTORY, retrievePipe, 0))
    imageAnalysis = Process(target=analyzeImageBB, name = "ANALYZER", args=(analyzePipe,))

    imageRetrieval.start()
    imageAnalysis.start()
