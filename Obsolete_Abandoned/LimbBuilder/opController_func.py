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
	
	return locatorPV, handle[0]
	
	
def opCreateController(prefix, object, controllerSize, fk):	
	ctrl = ''
	#create crvs 
	if (fk == True):
		ctrl = mel.eval('curve -d 1 -p 0 1 0 -p 0 0.987688 -0.156435 -p 0 0.951057 -0.309017 -p 0 0.891007 -0.453991 -p 0 0.809017 -0.587786 -p 0 0.707107 -0.707107 -p 0 0.587785 -0.809017 -p 0 0.453991 -0.891007 -p 0 0.309017 -0.951057 -p 0 0.156434 -0.987689 -p 0 0 -1 -p 0 -0.156434 -0.987689 -p 0 -0.309017 -0.951057 -p 0 -0.453991 -0.891007 -p 0 -0.587785 -0.809017 -p 0 -0.707107 -0.707107 -p 0 -0.809017 -0.587786 -p 0 -0.891007 -0.453991 -p 0 -0.951057 -0.309017 -p 0 -0.987688 -0.156435 -p 0 -1 0 -p -4.66211e-09 -0.987688 0.156434 -p -9.20942e-09 -0.951057 0.309017 -p -1.353e-08 -0.891007 0.453991 -p -1.75174e-08 -0.809017 0.587785 -p -2.10734e-08 -0.707107 0.707107 -p -2.41106e-08 -0.587785 0.809017 -p -2.65541e-08 -0.453991 0.891007 -p -2.83437e-08 -0.309017 0.951057 -p -2.94354e-08 -0.156434 0.987688 -p -2.98023e-08 0 1 -p -2.94354e-08 0.156434 0.987688 -p -2.83437e-08 0.309017 0.951057 -p -2.65541e-08 0.453991 0.891007 -p -2.41106e-08 0.587785 0.809017 -p -2.10734e-08 0.707107 0.707107 -p -1.75174e-08 0.809017 0.587785 -p -1.353e-08 0.891007 0.453991 -p -9.20942e-09 0.951057 0.309017 -p -4.66211e-09 0.987688 0.156434 -p 0 1 0 -p -0.156435 0.987688 0 -p -0.309017 0.951057 0 -p -0.453991 0.891007 0 -p -0.587785 0.809017 0 -p -0.707107 0.707107 0 -p -0.809017 0.587785 0 -p -0.891007 0.453991 0 -p -0.951057 0.309017 0 -p -0.987689 0.156434 0 -p -1 0 0 -p -0.987689 -0.156434 0 -p -0.951057 -0.309017 0 -p -0.891007 -0.453991 0 -p -0.809017 -0.587785 0 -p -0.707107 -0.707107 0 -p -0.587785 -0.809017 0 -p -0.453991 -0.891007 0 -p -0.309017 -0.951057 0 -p -0.156435 -0.987688 0 -p 0 -1 0 -p 0.156434 -0.987688 0 -p 0.309017 -0.951057 0 -p 0.453991 -0.891007 0 -p 0.587785 -0.809017 0 -p 0.707107 -0.707107 0 -p 0.809017 -0.587785 0 -p 0.891006 -0.453991 0 -p 0.951057 -0.309017 0 -p 0.987688 -0.156434 0 -p 1 0 0 -p 0.951057 0 -0.309017 -p 0.809018 0 -0.587786 -p 0.587786 0 -0.809017 -p 0.309017 0 -0.951057 -p 0 0 -1 -p -0.309017 0 -0.951057 -p -0.587785 0 -0.809017 -p -0.809017 0 -0.587785 -p -0.951057 0 -0.309017 -p -1 0 0 -p -0.951057 0 0.309017 -p -0.809017 0 0.587785 -p -0.587785 0 0.809017 -p -0.309017 0 0.951057 -p -2.98023e-08 0 1 -p 0.309017 0 0.951057 -p 0.587785 0 0.809017 -p 0.809017 0 0.587785 -p 0.951057 0 0.309017 -p 1 0 0 -p 0.987688 0.156434 0 -p 0.951057 0.309017 0 -p 0.891006 0.453991 0 -p 0.809017 0.587785 0 -p 0.707107 0.707107 0 -p 0.587785 0.809017 0 -p 0.453991 0.891007 0 -p 0.309017 0.951057 0 -p 0.156434 0.987688 0 -p 0 1 0 ;')
	else: 
		ctrl = mel.eval('curve -d 1 -p -1 1 1 -p -1 1 -1 -p 1 1 -1 -p 1 1 1 -p -1 1 1 -p -1 -1 1 -p -1 -1 -1 -p -1 1 -1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 -p 1 1 1 -p 1 1 -1 -p 1 -1 -1 -p 1 -1 1 -p 1 -1 -1 -p -1 -1 -1 ;')
	
	#parent
	cmds.parentConstraint(object,ctrl,mo=False)
	#del con
	cmds.delete(ctrl,cn=True)
	#controller size
	cmds.scale(controllerSize*1, controllerSize*1, controllerSize*1, ctrl)
	#freeze Transforms
	cmds.makeIdentity(ctrl, apply= True, t = 0, r = 0, s= 1, n = 0, pn = 1)

	if (fk == True):
		#find shape
		child = cmds.listRelatives(ctrl, c=True)
		#parent shape
		cmds.parent(child, object, r= True, s=True)
		#del transform
		cmds.delete(ctrl)
		#rename child
		cmds.rename(child, object + 'Shape')
		#lock fk ctrl
		cmds.setAttr(object+'.tx', lock = True, channelBox = False, keyable = False)
		cmds.setAttr(object+'.ty', lock = True, channelBox = False, keyable = False)
		cmds.setAttr(object+'.tz', lock = True, channelBox = False, keyable = False)
		cmds.setAttr(object+'.v', lock = True, channelBox = False, keyable = False)
	else:
		pass

#testing area
if __name__ == "__main__":
	opCreateController("test", cmds.ls(sl=True)[0], 0.5, False)
	