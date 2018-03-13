import os
import json
import logging
import pymel.core as pm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

try:
    import cPickle as pickle
except:
    import pickle

# path to our default pickle file
iconsFolderPath = os.path.join(os.path.dirname(__file__), 'Images')
defaultLibraryPath = os.path.join(os.path.dirname(__file__), 'consPickle.pkl')
_logger.debug(defaultLibraryPath)

try:
    consDict = pickle.load(open(defaultLibraryPath, 'rb'))
    tempDictStr = json.dumps(consDict, indent=4)
    _logger.debug("consDict: {0}".format(tempDictStr))
except:
    _logger.warn("no existing library of controls:{0}".format(defaultLibraryPath))
    consDict = {}


def consList():
    """returns a list of available cons"""
    return consDict.keys()


def saveCon(con=None, conName=None, doScreenGrab=False, doCrop=True, debug=False):
    """ saves selected nurbs curve to the pickle file
    """
    global consDict

    con = con or pm.selected()[0]

    conShape = con.getShape()

    degree = conShape.degree()  # 1 or 3
    form = conShape.form().key  # periodic or open
    spans = conShape.spans.get()  # same as number of CVs
    knots = conShape.getKnots()  # list of float values
    cvs = conShape.getCVs()  # list of cv points

    _logger.debug("print knots: {0}".format(knots))

    conName = conName or pm.promptBox("provide controller name", "Name:", "Ok", "Cancel")

    if not conName:
        return
    _logger.debug("conName: {0}".format(conName))

    tempDict = {}
    tempDict['degree'] = degree
    tempDict['knots'] = knots
    tempDict['form'] = form
    tempDict['spans'] = spans

    # convert to tuples so json will not choke on the data
    tempDict['cvs'] = [tuple(cv) for cv in cvs]

    # tempDictStr = json.dumps(tempDict,indent=4)
    # _logger.debug("tempDict: {0}".format(tempDictStr))

    # appending to main dictionary
    consDict[conName] = tempDict

    tempDictStr = json.dumps(consDict, indent=4)
    _logger.debug("consDict: {0}".format(tempDictStr))

    # export to pickle
    pickle.dump(consDict, open(defaultLibraryPath, 'wb'))

    # debug
    if debug:
        with open(defaultLibraryPath.replace(".pkl", ".json"), 'w') as outfile:
            json.dump(consDict, outfile, indent=4)

    if doScreenGrab:
        screenGrap(conName)
        _logger.info("Created Screengrab")
    if doCrop:
        cropImage(conName)


def cropImage(conName):
    """ runs a process to crop the image to 240x240 """
    screenGrap(conName=conName)


def screenGrap(conName):
    """ captures the 3D viewport as an Icon Pic"""
    import maya.OpenMaya as api
    import maya.OpenMayaUI as apiUI

    # get active view
    view = apiUI.M3dView.active3dView()

    # create an empty image viewer
    img = api.MImage()
    view.readColorBuffer(img, True)

    img.resize(250, 250, True)
    # estImage = r'C:\Users\Doug\Documents\maya\scripts\Images\textImage.png'
    iconFileName = os.path.join(iconsFolderPath, "{0}.jpg".format(conName))

    # write to disk
    img.writeToFile(iconFileName, 'jpg')


def generateCon(conName=None, scale=1.0, color=0):
    """ generate a nurbs curve controller
    """

    if not conName:
        _logger.warn("No Controller Name provided. example: conName='diamond' ")
        return

    conToCreate = consDict.get(conName, None)

    if not conToCreate:
        _logger.error("Control does not exist in the pickle file")
        return

    tempDictStr = json.dumps(conToCreate, indent=4)
    _logger.debug("conToCreate: {0}".format(tempDictStr))

    periodic = True if conToCreate.get('form') == 'periodic' else False
    degree = conToCreate.get('degree')
    cvs = conToCreate.get('cvs')
    knots = conToCreate.get('knots')

    # create the curve
    crv = pm.curve(d=degree, p=cvs, k=knots, per=periodic)

    crv.scale.set((scale, scale, scale))
    pm.makeIdentity(crv, apply=True, t=False, r=0, s=1, n=0)

    crv.getShape().overrideEnabled.set(1)
    crv.getShape().overrideColor.set(color)

    return crv
