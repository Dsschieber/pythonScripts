from maya import cmds, OpenMaya
import maya.cmds as cmds 
import math


def getPoleVectorPos(startJoint, midJoint, endJoint, name):
	"""gets the pole vector position from three points in worldspace"""
	print(startJoint, midJoint, endJoint, name)
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
	locatorPV = cmds.spaceLocator(n=name+'_pvCtrl_1')[0]
	cmds.xform(locatorPV, ws=1, t= (finalV.x, finalV.y, finalV.z))
	
	#rotations of pole vector
	cmds.xform(locatorPV, ws=1, rotation=((rot.x/math.pi*180.0),
									(rot.y/math.pi*180.0),
									(rot.z/math.pi*180.0)))
if __name__ == "__main__":
	joints = cmds.ls(sl=True)
	getPoleVectorPos(joints[0],joints[1],joints[2],str(joints[0]))