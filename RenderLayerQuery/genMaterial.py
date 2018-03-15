import pymel.core as pm
from maya import cmds
import os
import logging
import json

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

try:
    import cPickle as pickle
except:
    import pickle

# path to our default pickle file
iconsFolderPath = os.path.join(os.path.dirname(__file__), 'Images')
defaultLibraryPath = os.path.join(os.path.dirname(__file__), 'matInfo.pkl')
_logger.debug(defaultLibraryPath)

try:
    matsDict = pickle.load(open(defaultLibraryPath, 'rb'))
    tempDictStr = json.dumps(matsDict, indent=4)
    _logger.debug("matsDict: {0}".format(tempDictStr))
except:
    _logger.warn("no existing library of controls:{0}".format(defaultLibraryPath))
    matsDict = {}


def matsList():
    """returns a list of available cons"""
    return matsDict.keys()


def getMaterialFromShape(curSel):
    matShapes = curSel[0].getShapes()
    shaderGrps = []
    for everyShade in matShapes:
        if everyShade.listConnections(type="shadingEngine") != []:
            shaderGrps.append(everyShade.listConnections(type="shadingEngine"))
    shadersCmd = cmds.ls(cmds.listConnections(shaderGrps[0]), materials=1)
    shaders = []
    for each in shadersCmd:
        shaders.append(pm.PyNode(each))
    return shaders


def getMaterial():
    sel = pm.ls(sl=True)
    shaders = []
    # see(sel[0])
    if sel:
        connections = sel[0].listHistory()
        for each in connections:
            if each.nodeType() == 'mesh':
                _logger.debug("Found Mesh")
                shaders = getMaterialFromShape(sel)
                break
        else:
            try:
                shadersCmd = cmds.ls(sel, materials=1)
                shaders.append(pm.PyNode(shadersCmd[0]))
            except:
                _logger.error("Cannot get material from {0}".format(sel[0]))
    else:
        _logger.error("Nothing selected")
    return shaders


if __name__ == "__main__":
    shaders = getMaterial()
