'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	Contains operations for constructing joints

================================================================================
				    FUNCTIONS:
opMakeJoints
opMirrorJoints
opCreateLocs
opDeleteLocs

================================================================================
				    NOTES:

opStretchIK should be moved to opController_func
================================================================================
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from maya import OpenMaya
import maya.cmds as cmds 
import maya.mel as mel
import pymel.core as pm
import math

	
def opMakeJoints(prefix, limbtype, jointOrientation, locs):
		
		#decoloration of vars
		limb = []
		limb.append(locs[0])
		limb.append(locs[1])
		limb.append(locs[2])
		nameSpace = str(limbtype) + "_"+ str(prefix)
		count = 1
		jntObject = []
		cmds.select(d=True)
		
		
		#create joints
		for v in limb:
			jnt = cmds.joint()
			pos = cmds.xform(v , q =1, ws =1, t =1)
			cmds.xform(jnt, ws =1, t =pos)
			jntObject.append(cmds.rename(jnt, nameSpace + '_Jnt_' + str(count)))
			count = count + 1
		
		#var for reorient
		jntSelect = nameSpace + '_Jnt_1'
		lastJnt = nameSpace + '_Jnt_3'
		
		#reorient joints
		#joint -e  -oj xyz -secondaryAxisOrient zup -ch -zso;
		#jointOrientation shall determine the axis of joints
		#secondary Axis to control orientation
		cmds.joint (jntSelect, e =1, oj = "xyz", secondaryAxisOrient= "zup", ch =1, zso =1)
		cmds.joint(lastJnt, e =1,  oj='none', ch=1, zso=1)
		
		return jntObject
		
def opMirrorJoints(mirrorType, mirrorBehaviorType, mirrorSearchReplace, joints):
	#mirror type switch determines axis joints will be mirrored on
	
	mirroredJoints = []
	
	if mirrorType == 0:
		mirroredJoints = cmds.mirrorJoint(joints[0],mirrorXY=True, mirrorBehavior=mirrorBehaviorType, searchReplace=( mirrorSearchReplace[0], mirrorSearchReplace[1] ))
	elif mirrorType == 1:
		mirroredJoints = cmds.mirrorJoint(joints[0],mirrorXZ=True, mirrorBehavior=mirrorBehaviorType, searchReplace=( mirrorSearchReplace[0], mirrorSearchReplace[1] ))
	else:
		mirroredJoints = cmds.mirrorJoint(joints[0],mirrorYZ=True, mirrorBehavior=mirrorBehaviorType, searchReplace=( mirrorSearchReplace[0], mirrorSearchReplace[1] ))
	
	return mirroredJoints
	

def opDeleteLocs(locs):
	#create Locators
	varLoc1 = locs[0]
	varLoc2 = locs[1]
	varLoc3 = locs[2]
	
	cmds.delete(varLoc1)
	cmds.delete(varLoc2)
	cmds.delete(varLoc3)


def opCreateLocs():
	#create Locators
	varLoc1 = cmds.spaceLocator(name="limb_loc_1")
	varLoc2 = cmds.spaceLocator(name="limb_loc_2")
	varLoc3 = cmds.spaceLocator(name="limb_loc_3")
	
	#move Locators for clarity
	cmds.move( 3, 0, 0, varLoc1, relative=True, objectSpace=True, worldSpaceDistance=True)
	cmds.move( 1.5, 0, 1, varLoc2, relative=True, objectSpace=True, worldSpaceDistance=True)
	
	return varLoc1, varLoc2, varLoc3
	
def opOrientBind(bind, ik, fk):
	
	# get
	binders = []
	wBind=[]
	wIk=[]
	wFk=[]
	# get joints
	# most likely unnecessary. However, its a little bit of error checking to make sure objects ARE joints(effector is bothersome)
	for stuff in bind:
		if (cmds.objectType(stuff)=='joint'):
			wBind.append(stuff)
	for stuff in ik:
		if (cmds.objectType(stuff)=='joint'):
			wIk.append(stuff)
	for stuff in fk:
		if (cmds.objectType(stuff)=='joint'):
			wFk.append(stuff)
	
	# counter
	i=0
	# cycle
	while(i < ((len(wBind))and(len(wIk))and(len(wFk)))):
		
		#create orient 
		bind01 = cmds.orientConstraint(wIk[i], wBind[i] ,mo=False)
		bind02 = cmds.orientConstraint(wFk[i], wBind[i] ,mo=False)
		#setAttr "bn_leg_Jnt_1_orientConstraint1.interpType" 0;
		#cmds.setAttr(wBind[i] + "_orientConstraint1.interpType", 0)
		#no flip has more flip
		
		# create blend color
		blendNode = cmds.shadingNode('blendColors',au=True,n=wBind[i]+'_blendScale')
		bind02.append(blendNode)
		# connect bind,ik,fk
		cmds.connectAttr(wIk[i]+'.scale',wBind[i]+'_blendScale.color2',f=True)
		cmds.connectAttr(wFk[i]+'.scale',wBind[i]+'_blendScale.color1',f=True)
		cmds.connectAttr(wBind[i]+'_blendScale.output',wBind[i]+'.scale',f=True)
		# counter
		i+=1
		#extend binders
		binders.extend(bind02)
		
		
	return binders