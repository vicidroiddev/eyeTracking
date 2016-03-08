from multiprocessing import Process, Lock, Pipe
import sys
import time
from Analyzer import Analyzer
import Test2
import Utils
import logging

sys.path.insert(0, '../pyCam/')
import Cam

from learning.ParamsConstructor import ParamsConstructor

__author__ = 'Raphael'

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

#GLOBAL VARS
PARAMS = ParamsConstructor().constructDefaultParams()
IMAGE_DIRECTORY = './processing/'

LOCK_OBJ = Lock()


def retrieveImageBB(imageDir, lock, pipe):
    logger.info('Init BB System')

    # initialize cameras
    camRight = Cam.Cam(IMAGE_DIRECTORY, "R")
    camLeft = Cam.Cam(IMAGE_DIRECTORY, "L")

    # looping to capture and process images
    for i in range(1,100):
        timestamp = int(time.time())
        camRight.takeImg()
        camLeft.takeImg()

        rightImg = camRight.getImg(timestamp)
        leftImg = camLeft.getImg(timestamp)

        # Must be locked when setting
        Test2.setLeftImage(leftImg)
        Test2.setRightImage(rightImg)

        #Send something through the pipe
        pipe.send(leftImg)

        time.sleep(1)

    # close connections to cameras
    camLeft.closeConn()
    camRight.closeConn()


def analyzeImageBB(lock):
    if Test2.getLeftImage() is not None:
        logger.log('Getting Left image is valid')
        (xL, yL) = Analyzer(Test2.getLeftImage()).getEyeData().getRandomPupilTruth()

    if Test2.getRightImage() is not None:
        logger.log('Getting right image is valid')
        (xR, yR) = Analyzer(Test2.getRightImage()).getEyeData().getRandomPupilTruth()


if  __name__ == '__main__':

    if not Utils.isBeagalBone():
        raise AssertionError('The system was meant for the beaglebone! Use a different Start.py file')

    # Pipe for connecting retrieval to analysis
    analyzePipe, retrievePipe = Pipe()

    # Processes for
    imageRetrieval = Process(target=retrieveImageBB, name = "CAMERA", args=(IMAGE_DIRECTORY, LOCK_OBJ, retrievePipe))
    imageAnalysis = Process(target=analyzeImageBB, name = "ANALYZER", args=())

    imageRetrieval.start()
    imageAnalysis.start()