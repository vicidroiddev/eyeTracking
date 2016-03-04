import datetime
import Utils
from learning.ParamsNew import ParamsNew
import copy
import pprint

#Always make a deep copy when using these to create new dicts
# SCHEMA = {"fileName":"","cameraType":"","color":"","verified":{"x":"","y":"","isReading":"True","radius":""},"imageProperties":{"mean":"","variance":""},"heuristics":[]}
# SCHEMA_HEURISTICS = {"histogramNormalized":"","threshold":"","param1":"","param2":"","minRadius":"","maxRadius":"","minContourRadius":"","hough":{"x":"","y":"","radius":""},"contour":{"x":"","y":"","radius":""}}



TRUTH = 'truth'
X = 'x'
Y = 'y'
RADIUS = 'radius'
HEURISTICS = 'heuristics'
HOUGH = "hough"
CONTOUR = "contour"
UPDATED_AT = "updated_at"

CENTRE = 60



class Eyeball():


    def __init__(self, fileName = None):
        self.dict = Utils.newDict({"fileName":"","updated_at":"","truth":{"x":"","y":""},"heuristics":[]})
        self.dict['fileName'] = fileName

    def getDict(self):
        return self.dict

    def getHeuristics(self):
        return self.getDict()[HEURISTICS]

    def getFileName(self):
        return self.dict['fileName']

    def getRandomPupilTruth(self):
        heuristics = self.getDict()[HEURISTICS]

        x = -1
        y = -1

        for h in heuristics:

            if 'contour' in h:
                xNew = h['contour']['x']
                yNew = h['contour']['y']

                if abs(xNew - CENTRE) < abs(x - CENTRE):
                    x = xNew
                    y = yNew

        return (x, y)

    def addPupilTruth(self, x, y):
        self.dict[TRUTH][X] = x
        self.dict[TRUTH][Y] = y
        pprint.pprint(self.dict)
        self.updateTimeStamp()
        pass

    def addThreshold(self, min, max, isNormalized):
        self.dict[HEURISTICS]

    #warning immuatable errors here
    def addHoughCircle(self, x, y, r):
        heuristics = {}
        hough = {}
        heuristics[HOUGH] = hough

        heuristics[HOUGH][X] = x
        heuristics[HOUGH][Y] = y
        heuristics[HOUGH][RADIUS] = r

        self.dict[HEURISTICS].append(heuristics)
        self.updateTimeStamp()


    def addContourCircle(self, x, y, r):
        heuristics = {}
        contour = {}
        heuristics[CONTOUR] = contour

        heuristics[CONTOUR][X] = x
        heuristics[CONTOUR][Y] = y
        heuristics[CONTOUR][RADIUS] = r

        self.dict[HEURISTICS].append(heuristics)
        self.updateTimeStamp()


    def updateTimeStamp(self):
        self.dict[UPDATED_AT] = datetime.datetime.now()


