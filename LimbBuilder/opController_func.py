'''

Responsible for creation and building of controllers, ik joint chain



================================================================================
					FUNCTIONS:
						
opStretchIK
opGroupSpecial
opPoleVectorIK
opCreateController

================================================================================
				    NOTES:


================================================================================

'''

from maya import OpenMaya
import os, sys
sys.path.append("C:\Users\Doug\Documents\GitHub\pythonScripts\LimbBuilder\mMath-master")
import maya.cmds as cmds 
import maya.mel as mel
import pymel.core as pm
import math
import nVec

def opStretchIK(startDrv, endDrv, poleVec):
	#declaring initial vectors
	startV = nVec.NVec(start_drv+".worldPosition", "sStretch")
	endV = nVec.NVec(end_drv+".worldPosition", "eStretch")
	poleV = nVec.NVec(poleVec_drv+".worldPosition", "pStretch")
	stretchV= nVec.NScalar(end_drv+".stretch","stretch")
	lockV= nVec.NScalar(end_drv+".lock","lock")
	
	#computing the length between the end and the start of the chain
	distV = endV - startV
	length = distV.length()
	
	#getting initial chain length and converting into vectors
	upLen = cmds.getAttr(chain[1] + '.tx')
	lowLen = cmds.getAttr(chain[2] + '.tx')
	upLenV = nVec.NScalar.from_value(upLen, "upLen")
	lowLenV = nVec.NScalar.from_value(lowLen, "lowLen")
	
	#getting total length chain (this can be easily multiplied by the global scale)
	initLen = upLenV+lowLenV
	
	#finding theratio
	ratio = length /initLen
	
	#calculating scaled length
	scaledUp = upLenV * ratio
	scaledlow = lowLenV * ratio
	
	#computing final blended stretch
	finalScaledUp = upLenV.blend(scaledUp, stretchV)
	finalScaledLow = lowLenV.blend(scaledlow,stretchV)
	
	#condition node (old school)
	cnd = cmds.createNode("condition")
	ratio.connect_to(cnd + '.firstTerm')
	cmds.setAttr(cnd + '.secondTerm' ,1)
	cmds.setAttr(cnd + '.operation', 3)
	
	#connecting our final calculaded stretch node to the cnd colors
	finalScaledUp.connect_to(cnd + '.colorIfTrueR')
	upLenV.connect_to(cnd + '.colorIfFalseR')
	finalScaledLow.connect_to(cnd + '.colorIfTrueG')
	lowLenV.connect_to(cnd + '.colorIfFalseG')
	
	#now compute the pole vector lock
	#get polevec vectors
	upPoleVec = poleV - startV
	lowPoleVec = poleV - endV
	
	#computing the length
	upPoleLen = upPoleVec.length()
	lowPoleLen= lowPoleVec.length()
	
	#blending default length with poleVec vectors
	upPoleBlen = upLenV.blend(upPoleLen, lockV)
	lowPoleBlen = lowLenV.blend(lowPoleLen, lockV)
	
	#connecting a NScalar to the output of the node
	finalStrUp = nVec.NScalar(cnd + '.outColorR')
	finalStrLow = nVec.NScalar(cnd + '.outColorG')
	
	#blending the stretch and lock lengths
	resUp = finalStrUp.blend(upPoleBlen,lockV)
	resLow =finalStrLow.blend(lowPoleBlen,lockV)
	
	#connect final result
	resUp.connect_to(chain[1] + '.tx')
	resLow.connect_to(chain[2] + '.tx')
	
def opGroupSpecial(objectSelection):
	'''
	creates a null group at location of object
	'''
	groups = []
	# group selected
	if (len(objectSelection) > 0):
		for stuff in objectSelection:
			par = cmds.listRelatives(stuff,p=True)
			#creates a second null group, currently not functioning
			if '_null_' in stuff:
				# split obj
				split = stuff.split('_null_')
				objName = split[0]
				num = split[-1]
				new = int(num) + 1
				if not(cmds.objExists(objName+'_null_'+str(new))):
					# create group
					cmds.group(n=objName+'_null_'+str(new),em=True)
					cmds.parentConstraint(stuff,objName+'_null_'+str(new),mo=False,n='tEmPbLaHbLaH')
					cmds.delete('tEmPbLaHbLaH')
					cmds.parent(stuff,objName+'_null_'+str(new)) 
					groups.append(objName+'_null_'+str(new))
					if (par):
						cmds.parent(objName+'_null_'+str(new),par[0])
					
			#creates null group
			else:
				if (cmds.objExists(stuff+'_null_0')==0):
					cmds.group(n=stuff+'_null_0',em=True)
					cmds.parentConstraint(stuff,stuff+'_null_0',mo=False,n='tEmPbLaHbLaH')
					cmds.delete('tEmPbLaHbLaH')
					cmds.parent(stuff,stuff+'_null_0')
					groups.append(stuff+'_null_0')
					if (par):
						cmds.parent(stuff+'_null_0',par[0])	
	return groups
	
def opPoleVectorIK(joints, prefix):
	'''
	
	creates IK joint chain with a polevector controller
	
	'''
	
	#variables
	startJoint = joints[0]
	midJoint = joints[1]
	endJoint = joints[2]
	ctrlName = prefix
	
	
	#creates ikRPSolver
	handle = cmds.ikHandle(sj=startJoint, ee=endJoint, solver="ikRPsolver", n=prefix+'_ikHandle')
	
	# sel groups
	'''
	some math for finding pole vector control position
	'''
	#poleVector = startPoint + (unit( crossProduct(perpendicularVector, endVector ) ) * multVal)
	
	endPos = cmds.xform(endJoint, q=True, ws=True, t=True)
	midPos = cmds.xform(midJoint, q=True, ws=True, t=True)
	startPos = cmds.xform(startJoint, q=True, ws=True, t=True)
	
	endV = OpenMaya.MVector(endPos[0], endPos[1], endPos[2])
	startV = OpenMaya.MVector(startPos[0], startPos[1], startPos[2])
	midV = OpenMaya.MVector(midPos[0], midPos[1], midPos[2])
	
	startEnd = endV - startV
	startMid = midV - startV
	
	dotP = startMid * startEnd
	proj = float(dotP) / float(startEnd.length())
	startEndN = startEnd.normal()
	projV = startEndN * proj
	
	arrowV = startMid - projV
	arrowV*= 0.5
	
	finalV = arrowV + midV
	
	cross1 = startEnd ^ startMid
	cross1.normalize()
	
	cross2 = cross1 ^ arrowV
	cross2.normalize()
	arrowV.normalize()
	
	matrixV = [ arrowV.x, arrowV.y, arrowV.z, 0,
			cross1.x, cross1.y, cross1.z, 0,
			cross2.x, cross2.y, cross2.z, 0,  
			0, 0, 0, 1]
	
	matrixM = OpenMaya.MMatrix()
	
	OpenMaya.MScriptUtil.createMatrixFromList(matrixV, matrixM)
	
	matrixFn = OpenMaya.MTransformationMatrix(matrixM)
	
	rot = matrixFn.eulerRotation()
	
	#create and move pole vector ctrl
	locatorPV = cmds.spaceLocator(n=ctrlName+'_pvCtrl_1')[0]
	cmds.xform(locatorPV, ws=1, t= (finalV.x, finalV.y, finalV.z))
	
	#rotations of pole vector
	cmds.xform(locatorPV, ws=1, rotation=((rot.x/math.pi*180.0),
									(rot.y/math.pi*180.0),
									(rot.z/math.pi*180.0)))
	
	#create polevector constraint
	cmds.poleVectorConstraint( locatorPV, handle[0] )
	
	#locName = cmds.rename(loc[0], ctrlName+'_pvCtrl_1')
	
	return locatorPV, handle
	
	
def opCreateController(prefix, object, controllerSize):	
	pass