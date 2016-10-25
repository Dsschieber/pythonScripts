def helloWorld():
	print("hello World")

'''
Author: Doug Schieber
Version 0.0.5

LimbCreator
	-creates a ikfk chain from locators

Bugs:
	-joint chain is being parented under position locators
	-soft ik stretch is really buggy (seems connections are not being made properly)
	
Future Additions:
	-bind chain
	-blend between fkIk
	-GUI
	-ikfk snapping
	-add offset to ik ctrls


'''




#=======================#
#      MAIN IMPORTS	#
#=======================#
from maya import cmds, OpenMaya
import maya.cmds as cmds 
import maya.mel as mel
import pymel.core as pm
import math




class IkFkBuilder(object):
	
	#creating class variables
	def __init__(self, prefix, joint1, joint2, joint3, twistAxis):
		self.prefix = prefix
		self.joint1 = joint1
		self.joint2 = joint2
		self.joint3 = joint3
		self.twistAxis = twistAxis
	
	def to_String(self):
		print(self.prefix)
		print(self.joint1)
		print(self.joint2)
		print(self.joint3)
		print(self.twistAxis)
	
	
	#seems the joint chains are some how being parented under the position locators
	def makeLimb(self, limbtype):
		
		#decoloration of vars
		limbtype = limbtype
		prefix = self.prefix
		limb = ['limb_loc_1', 'limb_loc_2','limb_loc_3']
		nameSpace = str(limbtype) + "_"+ str(prefix)
		count = 1
		jntObject = []
		
		#create joints
		for v in limb:
			jnt = cmds.joint()
			pos = cmds.xform(v , q =1, ws =1, t =1)
			cmds.xform(jnt, ws =1, t =pos)
			jntObject = cmds.rename(jnt, nameSpace + '_Jnt_' + str(count))
			if count == 1:
				self.joint1 = jntObject
			elif count == 2:
				self.joint2 = jntObject
			else:
				self.joint3 = jntObject
			count = count + 1
		
		#var for reorient
		jntSelect = nameSpace + '_Jnt_1'
		
		#reorient joints
		cmds.joint (jntSelect, e =1, oj = "xyz", secondaryAxisOrient= "yup", ch =1, zso =1)
		
		
				
	def doIt(self):
		
		#class variables
		prefix = self.prefix
		joints = []
		control = self.prefix + "_ikCtrl_1"
		twistAxis = self.twistAxis
		joints = [self.joint1, self.joint2, self.joint3]
		
		''' 
		prefix - Prefix string attached to all nodes
		joints - List of joints in chain. e.g. ['Shoulder_Joint', 'Elbow_Joint', 'Wrist_Joint']
		control - ...
		twistAxis - Axis pointing down the joint chain. Setup requires this. Typically x, but y, z will work. 
		
		USAGE:
		import softIK
		softIK.doIt('left_arm', ['joint1', 'joint2', 'joint3'], 'left_arm_control', 'x')
		
		Attributes (added to control):
		Stretch - Toggles stretching
		Soft - Adjusts amount of softness, adjust as required
		
		'''
		
		# Find the full length of all joints
		length = 0
		for i in range(1, len(joints)):
			length += abs(cmds.getAttr(joints[i]+'.t'+twistAxis))
		
		
		cmds.addAttr(control, longName='stretch', defaultValue=0, minValue=0, maxValue=1, keyable=True)
		cmds.addAttr(control, longName='soft', at='double', defaultValue=0.001, minValue=0.001, maxValue=10, keyable=True)
		
		# Create distance node & locators
		
		startLocator = cmds.spaceLocator(name=prefix+'startDistLoc')
		cmds.pointConstraint(joints[0], startLocator)
		cmds.setAttr(startLocator[0]+'.visibility', 0)
		
		endLocator = cmds.spaceLocator(name=prefix+'endDistLoc')
		cmds.pointConstraint(control, endLocator)
		cmds.setAttr(endLocator[0]+'.visibility', 0)
		
		distLocGroup = cmds.group(empty=True, name=prefix+'distLoc_grp')
		cmds.parent(startLocator, endLocator, distLocGroup)
		
		distanceNode = cmds.createNode('distanceBetween', name=prefix+'distanceBetween')
		cmds.connectAttr(startLocator[0]+'.translate', distanceNode+'.point1')
		cmds.connectAttr(endLocator[0]+'.translate', distanceNode+'.point2')
		
		defaultDist = cmds.getAttr(distanceNode+'.distance')
		
		
		# Build node network
		
		mdn1 = cmds.createNode('multiplyDivide', name=prefix+'soft_IK_01_mult_mdn')
		cmds.connectAttr(control+'.soft', mdn1+'.input1X')
		cmds.setAttr(mdn1+'.input2X', -1)
		
		pma1 = cmds.createNode('plusMinusAverage', name=prefix+'soft_IK_plus_pma')
		cmds.setAttr(pma1+'.input1D[0]', length)
		cmds.connectAttr(mdn1+'.outputX', pma1+'.input1D[1]')
		
		pma2 = cmds.createNode('plusMinusAverage', name=prefix+'soft_IK_01_minus_pma')
		cmds.setAttr(pma2+'.operation', 2)
		cmds.connectAttr(pma1+'.output1D', pma2+'.input1D[0]')
		cmds.connectAttr(distanceNode+'.distance', pma2+'.input1D[1]')
		
		mdn2 = cmds.createNode('multiplyDivide', name=prefix+'soft_IK_01_div_mdn')
		cmds.setAttr(mdn2+'.operation', 2)
		cmds.connectAttr(pma2+'.output1D', mdn2+'.input1X')
		cmds.connectAttr(control+'.soft', mdn2+'.input2X')
		
		mdn3 = cmds.createNode('multiplyDivide', name=prefix+'soft_IK_pow_mdn')
		cmds.setAttr(mdn3+'.operation', 3)
		cmds.setAttr(mdn3+'.input1X', math.e)
		cmds.connectAttr(mdn2+'.outputX', mdn3+'.input2X')
		
		mdn4 = cmds.createNode('multiplyDivide', name=prefix+'soft_IK_02_mult_mdn')
		cmds.connectAttr(control+'.soft', mdn4+'.input1X')
		cmds.connectAttr(mdn3+'.outputX', mdn4+'.input2X')
		
		pma3 = cmds.createNode('plusMinusAverage', name=prefix+'soft_IK_02_minus_pma')
		cmds.setAttr(pma3+'.operation', 2)
		cmds.setAttr(pma3+'.input1D[0]', length)
		cmds.connectAttr(mdn4+'.outputX', pma3+'.input1D[1]')
		
		cdn1 = cmds.createNode('condition', name=prefix+'soft_IK_cdn')
		cmds.setAttr(cdn1+'.operation', 4)
		cmds.connectAttr(distanceNode+'.distance', cdn1+'.firstTerm')
		cmds.connectAttr(distanceNode+'.distance', cdn1+'.colorIfTrueR')
		cmds.connectAttr(pma1+'.output1D', cdn1+'.secondTerm')
		cmds.connectAttr(pma3+'.output1D', cdn1+'.colorIfFalseR')
		
		mdn5 = cmds.createNode('multiplyDivide', name=prefix+'soft_IK_02_div_mdn')
		cmds.setAttr(mdn5+'.operation', 2)
		cmds.connectAttr(distanceNode+'.distance', mdn5+'.input1X')
		cmds.connectAttr(cdn1+'.outColorR', mdn5+'.input2X')
		
		for i in range(1, len(joints)):
			mdn = cmds.createNode('multiplyDivide', name=prefix+'soft_IK_multiply_0%s_pma' % i)
			translateValue = cmds.getAttr(joints[i]+'.t' + twistAxis)
			cmds.setAttr(mdn+'.input1X', translateValue)
			cmds.connectAttr(mdn5+'.outputX', mdn+'.input2X')
			b2a = cmds.createNode('blendTwoAttr', name=prefix+'soft_IK_0%s_b2a' % i)
			cmds.setAttr(b2a+'.input[0]', translateValue)
			cmds.connectAttr(mdn+'.outputX', b2a+'.input[1]')
			cmds.connectAttr(control+'.stretch', b2a+'.attributesBlender') 
			cmds.connectAttr(b2a+'.output', joints[i]+'.t' + twistAxis)
			
			return distLocGroup
			
	
	def createIkjointChain(self):
		
		#class variables
		startJoint = self.joint1
		midJoint = self.joint2
		endJoint = self.joint3
		ctrlName = self.prefix
		
		
		#creates ikRPSolver
		handle = cmds.ikHandle(sj=startJoint, ee=endJoint, solver="ikRPsolver")
	
		'''
		create a box control at end joint. 
		'''
		#select end joint
		sel = cmds.ls(endJoint)
		# check
		if sel:
			ctrls = []
			for stuff in sel:
				# control
				ctrl = mel.eval('curve -d 1 -p -1 1 1 -p -1 1 -1 -p 1 1 -1 -p 1 1 1 -p -1 1 1 -p -1 -1 1 -p -1 -1 -1 -p -1 1 -1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 -p 1 1 1 -p 1 1 -1 -p 1 -1 -1 -p 1 -1 1 -p 1 -1 -1 -p -1 -1 -1 ;')
				# parent
				cmds.parentConstraint(stuff,ctrl,mo=False)
				# del con
				cmds.delete(ctrl,cn=True)
				# rename ctrl
				newName = cmds.rename(ctrlName+'_ikCtrl_#')
				# append selection list
				ctrls.append(newName)	
				# select
				cmds.select(ctrls)
				#parent ikHandle to new control
				cmds.pointConstraint(handle[0], ctrls)
		'''
		some math for finding pole vector control position
		'''
		#endjoint position
		pos = cmds.xform(endJoint, q=True, ws=True, t=True)
		a = om.MVector(pos[0], pos[1], pos[2])
		#startjoint position
		pos = cmds.xform(startJoint, q=True, ws=True, t=True)
		b = om.MVector(pos[0], pos[1], pos[2])
		
		c = b - a 
		d = c * .5
		e = a + d 
		
		#get midjoint position
		pos = cmds.xform(midJoint, q=True, ws=True, t=True)
		c = om.MVector(pos[0], pos[1], pos[2])
		
		f = c - e
		g = f * 2
		h = e + g 
		
		#create and move pole vector ctrl
		loc = cmds.spaceLocator()
		cmds.move(h.x, h.y, h.z, loc[0])
		
		#create polevector constraint
		cmds.poleVectorConstraint( loc[0], handle[0] )
		
		cmds.rename(loc[0], ctrlName+'_pvCtrl_1')
		
	
	def createFKjointChain(self):
		
		#class Vars
		startJoint = self.joint1
		midJoint = self.joint2
		endJoint = self.joint3
		ctrlName = self.prefix
		
		#list of Vars
		sel = cmds.ls(startJoint,midJoint, endJoint)
		#creates and names FK controls
		if sel:
			ctrls = []
			for stuff in sel:
				# control
				ctrl = mel.eval('curve -d 1 -p 0 1 0 -p 0 0.987688 -0.156435 -p 0 0.951057 -0.309017 -p 0 0.891007 -0.453991 -p 0 0.809017 -0.587786 -p 0 0.707107 -0.707107 -p 0 0.587785 -0.809017 -p 0 0.453991 -0.891007 -p 0 0.309017 -0.951057 -p 0 0.156434 -0.987689 -p 0 0 -1 -p 0 -0.156434 -0.987689 -p 0 -0.309017 -0.951057 -p 0 -0.453991 -0.891007 -p 0 -0.587785 -0.809017 -p 0 -0.707107 -0.707107 -p 0 -0.809017 -0.587786 -p 0 -0.891007 -0.453991 -p 0 -0.951057 -0.309017 -p 0 -0.987688 -0.156435 -p 0 -1 0 -p -4.66211e-09 -0.987688 0.156434 -p -9.20942e-09 -0.951057 0.309017 -p -1.353e-08 -0.891007 0.453991 -p -1.75174e-08 -0.809017 0.587785 -p -2.10734e-08 -0.707107 0.707107 -p -2.41106e-08 -0.587785 0.809017 -p -2.65541e-08 -0.453991 0.891007 -p -2.83437e-08 -0.309017 0.951057 -p -2.94354e-08 -0.156434 0.987688 -p -2.98023e-08 0 1 -p -2.94354e-08 0.156434 0.987688 -p -2.83437e-08 0.309017 0.951057 -p -2.65541e-08 0.453991 0.891007 -p -2.41106e-08 0.587785 0.809017 -p -2.10734e-08 0.707107 0.707107 -p -1.75174e-08 0.809017 0.587785 -p -1.353e-08 0.891007 0.453991 -p -9.20942e-09 0.951057 0.309017 -p -4.66211e-09 0.987688 0.156434 -p 0 1 0 -p -0.156435 0.987688 0 -p -0.309017 0.951057 0 -p -0.453991 0.891007 0 -p -0.587785 0.809017 0 -p -0.707107 0.707107 0 -p -0.809017 0.587785 0 -p -0.891007 0.453991 0 -p -0.951057 0.309017 0 -p -0.987689 0.156434 0 -p -1 0 0 -p -0.987689 -0.156434 0 -p -0.951057 -0.309017 0 -p -0.891007 -0.453991 0 -p -0.809017 -0.587785 0 -p -0.707107 -0.707107 0 -p -0.587785 -0.809017 0 -p -0.453991 -0.891007 0 -p -0.309017 -0.951057 0 -p -0.156435 -0.987688 0 -p 0 -1 0 -p 0.156434 -0.987688 0 -p 0.309017 -0.951057 0 -p 0.453991 -0.891007 0 -p 0.587785 -0.809017 0 -p 0.707107 -0.707107 0 -p 0.809017 -0.587785 0 -p 0.891006 -0.453991 0 -p 0.951057 -0.309017 0 -p 0.987688 -0.156434 0 -p 1 0 0 -p 0.951057 0 -0.309017 -p 0.809018 0 -0.587786 -p 0.587786 0 -0.809017 -p 0.309017 0 -0.951057 -p 0 0 -1 -p -0.309017 0 -0.951057 -p -0.587785 0 -0.809017 -p -0.809017 0 -0.587785 -p -0.951057 0 -0.309017 -p -1 0 0 -p -0.951057 0 0.309017 -p -0.809017 0 0.587785 -p -0.587785 0 0.809017 -p -0.309017 0 0.951057 -p -2.98023e-08 0 1 -p 0.309017 0 0.951057 -p 0.587785 0 0.809017 -p 0.809017 0 0.587785 -p 0.951057 0 0.309017 -p 1 0 0 -p 0.987688 0.156434 0 -p 0.951057 0.309017 0 -p 0.891006 0.453991 0 -p 0.809017 0.587785 0 -p 0.707107 0.707107 0 -p 0.587785 0.809017 0 -p 0.453991 0.891007 0 -p 0.309017 0.951057 0 -p 0.156434 0.987688 0 -p 0 1 0 ;')
				# parent
				cmds.parentConstraint(stuff,ctrl,mo=False)
				# del con
				cmds.delete(ctrl,cn=True)
				# rename ctrl
				newName = cmds.rename(ctrlName+'_fkCtrl_#')
				# append selection list
				ctrls.append(newName)	
				# select
				cmds.select(ctrls)
		
		#create constraints
		cmds.orientConstraint(ctrls[0],startJoint, mo=True)
		cmds.orientConstraint(ctrls[1],midJoint, mo=True)
		cmds.orientConstraint(ctrls[2],endJoint, mo=True)
		cmds.pointConstraint(startJoint,ctrls[0], mo=True)
		cmds.pointConstraint(midJoint,ctrls[1], mo=True)
		cmds.pointConstraint(endJoint,ctrls[2], mo=True)
		
		
		place = 1
		# sel
		if (len(ctrls) > 0):
			# group list
			groups = []
			# group selected
			for stuff in ctrls:
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
						if (place == 1):
							cmds.parentConstraint(stuff,objName+'_null_'+str(new),mo=False,n='tEmPbLaHbLaH')
							cmds.delete('tEmPbLaHbLaH')
						cmds.parent(stuff,objName+'_null_'+str(new))
						groups.append(objName+'_null_'+str(new))
						if (par):
							cmds.parent(objName+'_null_'+str(new),par[0])
						cmds.select(cl=True)
				#creates null group
				else:
					if (cmds.objExists(stuff+'_null_0')==0):
						cmds.group(n=stuff+'_null_0',em=True)
						if (place == 1):
							cmds.parentConstraint(stuff,stuff+'_null_0',mo=False,n='tEmPbLaHbLaH')
							cmds.delete('tEmPbLaHbLaH')
						cmds.parent(stuff,stuff+'_null_0')
						groups.append(stuff+'_null_0')
						if (par):
							cmds.parent(stuff+'_null_0',par[0])
						cmds.select(cl=True)
			# sel groups
			if (groups):
				cmds.select(groups,r=True)
		
		#parent fk Controls to each other
		cmds.parent(groups[2],ctrls[1])
		cmds.parent(groups[1],ctrls[0])
		


#@static
def createLocs():
	#create Locators
	varLoc1 = cmds.spaceLocator(name="limb_loc_1")
	varLoc2 = cmds.spaceLocator(name="limb_loc_2")
	varLoc3 = cmds.spaceLocator(name="limb_loc_3")
	
	#move Locators for clarity
	cmds.move( 3, 0, 0, varLoc1, relative=True, objectSpace=True, worldSpaceDistance=True)
	cmds.move( 1.5, 0, 1, varLoc2, relative=True, objectSpace=True, worldSpaceDistance=True)
	cmds.move( 0, 0, 0, varLoc3, relative=True, objectSpace=True, worldSpaceDistance=True)
	
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
	
	
	


createObjects()
createLocs()
#