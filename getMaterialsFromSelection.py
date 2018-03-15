import pymel.core as pm
from maya import cmds
# from see import see
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
""" I plan to impliment this into render layers script for saving materials """


def getMaterialFromShape(curSel):
    """ gets material from node type mesh """
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
    """ gets a material from object if object has material """
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
