#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
baking tools script.

functions
-bakeJointsToWorld
-selectJointsFromGeometry


"""


import pymel.core as pm
from maya import cmds
import logging
import maya.OpenMayaAnim as animAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def bakeJointsToWorld():
    """

    takes a selection of joints, creates a joint,
    bakes that joint to worldPos of selection, then parents selection under bakedJoints. 
    This is good if your fbx joints are losing their local space.

    """

    selObj = cmds.ls(sl=True)

    #Check if an object is selected
    if selObj == []:
        cmds.confirmDialog(t='Warning!',message='Please Select min. one Child Object',ds='ok',icn='information')



    bakeList = []
    for n in selObj:
        
        #check if selected object is a child of an object           
        par = cmds.listRelatives(n,parent=True)
        if par == None:
            cmds.confirmDialog(t='Warning!',message='%s has no Parent Object' %n ,ds='ok',icn='information')
            
        else:
            #duplicate object 
                                    
            duplObj = cmds.duplicate(n,name=n+'_bakedToWorld',rc=True,rr=True)
            
            childrenTd = cmds.listRelatives(duplObj,c=True,pa=True)
            if childrenTd > 0:
                for c in childrenTd[1:]:
                    cmds.delete(c)

            toBake = cmds.parent(duplObj,w=True)
            bakeList.append(toBake)
            cmds.parentConstraint(n,toBake,mo=False)
            cmds.scaleConstraint(n,toBake,mo=False)
            
            

    #get Start and End Frame of Time Slider
    startFrame = cmds.playbackOptions(q=True,minTime=True)
    endFrame = cmds.playbackOptions(q=True,maxTime=True)

    # bake Animation and delete Constraints

    for i in bakeList:
        cmds.bakeResults(i, t=(startFrame,endFrame))
        cmds.delete(i[0] + '*Constraint*')
    for i in range(len(selObj)):
        cmds.parent( selObj[i], bakeList[i])

def selectJointsFromGeometry():
    """ 
    this function takes a selection of skinned geometry 
    and will select the joints that are skinned to it. 
    """

    skinnedObject = pm.ls(sl=True)
    uniqueJointList = []

    #when there is more than one skin connection it will throw an error (example skinned blendshape)
    for s in skinnedObject:
        toNode = pm.PyNode(s)
        objectConnections = pm.listHistory(toNode, exactType ="skinCluster")
        if objectConnections == []:
            logger.info(s + " does not have a skinCluster. Script will now cancel.")
            return
        objectJoints = objectConnections[0].getWeightedInfluence()
        for x in objectJoints:
            if not x in uniqueJointList:
                uniqueJointList.append(x)
    
    pm.select(uniqueJointList)

def getBlendShapeAttributeNames():
    """ Gets all the the attributes names on blendshape at each weight index
    """
    #the node var only has to list some blendshape. I have it listing all blendshapes in scene which you probably don’t want
    node = cmds.ls(type='blendShape')
    # returns tuple of weight attrs
    blendAttrSize = cmds.getAttr(node[0]+'.weight')

    #loop over the attributes now and get their name info
    for i in range(len(blendAttrSize[0])):
        attrName = node[0] + ".weight[" + str(i) + "]"
        logger.info("Attribute name at index " + str(i) + " is " + cmds.aliasAttr(attrName, q=True))

def getTargetsFromSelection():
    """This function will get the blendshape on selected and print out
    the blendshape name,
    the base shape name, and
    all the targets at their weight index
    """
    selectedNode = pm.ls(sl=True)
    #I only have this getting history from first selected.
    nodeHis = pm.listHistory(selectedNode[0])
    objectBlendshape = []

    #append blendshape to a list
    for each in nodeHis:
        if (pm.nodeType(each) == 'blendShape'): 
            objectBlendshape.append(each)
    logger.info("Blendshape node name: {0}".format(objectBlendshape[0]))
    #loop through number of blendshapes get the targets and base shape on blendshape 
    for psds in objectBlendshape:
        targets = psds.getTarget()
        baseShape = psds.getBaseObjects()
        logger.info("Base Shape: {0}".format(baseShape[0]))
        for i in range(len(targets)):
            logger.info("Target Shape at Index {0}: {1}".format(str(i), targets[i]))

def bakeBlendShapesScene():
    """ bakes blendshapes based on timeline length """
    sceneBlendShapes = cmds.ls(type='blendShape')
    
    if sceneBlendShapes > 0:
        cmds.select(sceneBlendShapes)
        blendshapeNodes = cmds.ls(selection=True)

       # gets the playback start & end time
        minValue = animAPI.MAnimControl.minTime().value()
        maxValue = animAPI.MAnimControl.maxTime().value()

        for blendshapeNode in blendshapeNodes:
            # get list of meshes in each blend deformer
            blendMeshes = cmds.blendShape(blendshapeNode, target=True, query=True)
            # bake blendshape attributes
            cmds.bakeResults(blendshapeNode, animation="objects", attribute=blendMeshes, simulation=True, time=(minValue, maxValue))
    
if __name__ == "__main__":
    getTargetsFromSelection()
    getBlendShapeAttributeNames()
    bakeBlendShapesScene()