'''
empty
'''
from maya import cmds, OpenMaya
import maya.cmds as cmds 
import maya.mel as mel
import pymel.core as pm
import math

class IKFKgui(object):
  def __init__(self):
    pass
  #@static
  #Works well, needs a change in strings for object naming. 
  def createObjects():
    ikObjects = IkFkBuilder(prefix = 'leg', joint1 = 'limb_loc_1', joint2 =  'limb_loc_2', joint3 =  'limb_loc_3', twistAxis = 'x')
    ikObjects.makeLimb("ik")
    ikObjects.createIkjointChain()
    ikObjects.doIt()
    fkObjects = IkFkBuilder(prefix = 'leg', joint1 = 'limb_loc_1', joint2 =  'limb_loc_2', joint3 =  'limb_loc_3', twistAxis = 'x')
    fkObjects.makeLimb("fk")
    #fkObjects.to_String()
    fkObjects.createFKjointChain()
