
'''
Author: Doug Schieber
Version 0.0.8

USE:
	I don't mind what you do with this script, if you take part of it or etc... just give me some credit. 

LimbCreator
	-creates a ikfk chain from locators

Bugs:
	-joint chain is being parented under position locators
	-soft ik stretch is really buggy (seems connections are not being made properly)
	
Future Additions:
	-should there be a wrist control? third FK control seems useless. 
	-GUI
	-ikfk snapping
	-name ikGroup and ikSolver
	-use the null control script multiple times inside functions while it should be a function itself within the class.
	-colors on controls
	-lock control attrs
	-scale factor on controls

Credits:
	SoftIK function by: Nick Miller
	vimeo.com/80905132

'''




#=======================#
#      MAIN IMPORTS	#
#=======================#
from maya import cmds, OpenMaya
import os, sys
import maya.cmds as cmds 
import maya.mel as mel
import pymel.core as pm
import math



class BuildChain(object): 
	binders = ''
	
	def __init__(self, bindChain, ikChain, fkChain, prefix):
		self.bindChain = bindChain
		self.ikChain = ikChain
		self.fkChain = fkChain
		self.binders = ''
		self.prefix = prefix
	
	def to_String(self):
		print(self.bindChain)
		print(self.ikChain)
		print(self.fkChain)
	
	
	def createSwitchCtrl(self):
		#get
		bind = self.bindChain
		binders = BuildChain.binders
		objectName = self.prefix
		ikChain = self.ikChain
		fkChain = self.fkChain
		
		#creating control
		ctrl = mel.eval('curve -d 1 -p 0 0 2 -p -1.5 0 3.5 -p -0.5 0 3.5 -p -0.5 0 5 -p 0.5 0 5 -p 0.5 0 3.5 -p 1.5 0 3.5 -p 0 0 2 -p 0 1.5 3.5 -p 0 0.5 3.5 -p 0 0.5 5 -p 0 -0.5 5 -p 0 -0.5 3.5 -p 0 -1.5 3.5 -p 0 0 2 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 ;')
		cmds.pointConstraint(bind[2],ctrl,mo=False)
		newName = cmds.rename(ctrl, objectName + '_switchFkIk_ctrl_1')
		#addAttr -ln "FK_to_IK"  -at double  -min 0 -max 1 -dv 0 |leg_switchFkIk_ctrl_1;
		cmds.addAttr(newName, k=True , ln='FK_to_IK' , at= 'double' , min=0 , max=1 , dv=0)
		#setAttr -lock true -keyable false -channelBox false "leg_switchFkIk_ctrl_1.tx";
		cmds.setAttr(newName + '.t', lock=True, k=False, channelBox=False)
		cmds.setAttr(newName + '.r', lock=True, k=False, channelBox=False)
		cmds.setAttr(newName + '.s', lock=True, k=False, channelBox=False)
		
		for stuff in binders:
			if (cmds.objectType(stuff)=='orientConstraint'):
				targetList = cmds.orientConstraint(stuff, q=True, tl=True)
				#setDrivenKeyframe -currentDriver leg_switchFkIk_ctrl_1.FK_to_IK bn_leg_Jnt_1_orientConstraint1.ik_leg_Jnt_1W0;
				#setDrivenKeyframe -currentDriver leg_switchFkIk_ctrl_1.FK_to_IK bn_leg_Jnt_1_orientConstraint1.fk_leg_Jnt_1W1;
				
				#propositional logic lol
				cmds.setDrivenKeyframe(stuff+'.'+targetList[0]+'W0', cd = newName + '.FK_to_IK',  dv=1, v=0 )
				cmds.setDrivenKeyframe(stuff+'.'+targetList[0]+'W0', cd = newName + '.FK_to_IK',  dv=0, v=1 )
				cmds.setDrivenKeyframe(stuff+'.'+targetList[1]+'W1', cd = newName + '.FK_to_IK',  dv=0, v=0 )
				cmds.setDrivenKeyframe(stuff+'.'+targetList[1]+'W1', cd = newName + '.FK_to_IK',  dv=1, v=1 )
			else:
				#connectAttr -f leg_switchFkIk_ctrl_1.FK_to_IK bn_leg_Jnt_1_blendScale.blender;
				cmds.connectAttr(newName + '.FK_to_IK', stuff + '.blender', f=True)
				print(stuff)
	
	def orientBind(self):
		# get
		bind = self.bindChain
		ik = self.ikChain
		fk = self.fkChain
		
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
			
			
		BuildChain.binders = binders

'''

- seperating out the create control and pass it back in should save a lot of space




'''
class ControlCreate():
	
	controllers = ''
	
	
	def __init__(self):
		ControlCreate.controllers = ''
		
	def createControl(self, leObjet, suffix, ctrlName):
		#vars
		sel = leObjet
		suffix = suffix
		count = 1
		
		#error check
		if sel:
			ctrls = []
			for stuff in sel:
				#determine control type
				if (suffix == 'ik'): 
					ctrl = mel.eval('curve -d 1 -p -1 1 1 -p -1 1 -1 -p 1 1 -1 -p 1 1 1 -p -1 1 1 -p -1 -1 1 -p -1 -1 -1 -p -1 1 -1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 -p 1 1 1 -p 1 1 -1 -p 1 -1 -1 -p 1 -1 1 -p 1 -1 -1 -p -1 -1 -1 ;')
				elif (suffix == 'fk'):
					ctrl = mel.eval('curve -d 1 -p 0 1 0 -p 0 0.987688 -0.156435 -p 0 0.951057 -0.309017 -p 0 0.891007 -0.453991 -p 0 0.809017 -0.587786 -p 0 0.707107 -0.707107 -p 0 0.587785 -0.809017 -p 0 0.453991 -0.891007 -p 0 0.309017 -0.951057 -p 0 0.156434 -0.987689 -p 0 0 -1 -p 0 -0.156434 -0.987689 -p 0 -0.309017 -0.951057 -p 0 -0.453991 -0.891007 -p 0 -0.587785 -0.809017 -p 0 -0.707107 -0.707107 -p 0 -0.809017 -0.587786 -p 0 -0.891007 -0.453991 -p 0 -0.951057 -0.309017 -p 0 -0.987688 -0.156435 -p 0 -1 0 -p -4.66211e-09 -0.987688 0.156434 -p -9.20942e-09 -0.951057 0.309017 -p -1.353e-08 -0.891007 0.453991 -p -1.75174e-08 -0.809017 0.587785 -p -2.10734e-08 -0.707107 0.707107 -p -2.41106e-08 -0.587785 0.809017 -p -2.65541e-08 -0.453991 0.891007 -p -2.83437e-08 -0.309017 0.951057 -p -2.94354e-08 -0.156434 0.987688 -p -2.98023e-08 0 1 -p -2.94354e-08 0.156434 0.987688 -p -2.83437e-08 0.309017 0.951057 -p -2.65541e-08 0.453991 0.891007 -p -2.41106e-08 0.587785 0.809017 -p -2.10734e-08 0.707107 0.707107 -p -1.75174e-08 0.809017 0.587785 -p -1.353e-08 0.891007 0.453991 -p -9.20942e-09 0.951057 0.309017 -p -4.66211e-09 0.987688 0.156434 -p 0 1 0 -p -0.156435 0.987688 0 -p -0.309017 0.951057 0 -p -0.453991 0.891007 0 -p -0.587785 0.809017 0 -p -0.707107 0.707107 0 -p -0.809017 0.587785 0 -p -0.891007 0.453991 0 -p -0.951057 0.309017 0 -p -0.987689 0.156434 0 -p -1 0 0 -p -0.987689 -0.156434 0 -p -0.951057 -0.309017 0 -p -0.891007 -0.453991 0 -p -0.809017 -0.587785 0 -p -0.707107 -0.707107 0 -p -0.587785 -0.809017 0 -p -0.453991 -0.891007 0 -p -0.309017 -0.951057 0 -p -0.156435 -0.987688 0 -p 0 -1 0 -p 0.156434 -0.987688 0 -p 0.309017 -0.951057 0 -p 0.453991 -0.891007 0 -p 0.587785 -0.809017 0 -p 0.707107 -0.707107 0 -p 0.809017 -0.587785 0 -p 0.891006 -0.453991 0 -p 0.951057 -0.309017 0 -p 0.987688 -0.156434 0 -p 1 0 0 -p 0.951057 0 -0.309017 -p 0.809018 0 -0.587786 -p 0.587786 0 -0.809017 -p 0.309017 0 -0.951057 -p 0 0 -1 -p -0.309017 0 -0.951057 -p -0.587785 0 -0.809017 -p -0.809017 0 -0.587785 -p -0.951057 0 -0.309017 -p -1 0 0 -p -0.951057 0 0.309017 -p -0.809017 0 0.587785 -p -0.587785 0 0.809017 -p -0.309017 0 0.951057 -p -2.98023e-08 0 1 -p 0.309017 0 0.951057 -p 0.587785 0 0.809017 -p 0.809017 0 0.587785 -p 0.951057 0 0.309017 -p 1 0 0 -p 0.987688 0.156434 0 -p 0.951057 0.309017 0 -p 0.891006 0.453991 0 -p 0.809017 0.587785 0 -p 0.707107 0.707107 0 -p 0.587785 0.809017 0 -p 0.453991 0.891007 0 -p 0.309017 0.951057 0 -p 0.156434 0.987688 0 -p 0 1 0 ;')
				else:
					print('is bind')
				# parent
				cmds.pointConstraint(stuff,ctrl,mo=False)
				# del con
				cmds.delete(ctrl,cn=True)
				# rename ctrl
				newName = cmds.rename(ctrlName+'_' + suffix + 'Ctrl_' + str(count))
				# append selection list
				ctrls.append(newName)	
				# select
				cmds.select(ctrls)
				#increment count
				count = count + 1
				
		ControlCreate.controllers = ctrls
		
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
		
		
		#scale of controls


class IkFkBuilder(object):
	
	handle = ''
	newCtrl = ''
	
	#creating class variables
	def __init__(self, prefix, joint1, joint2, joint3, twistAxis):
		self.prefix = prefix
		self.joint1 = joint1
		self.joint2 = joint2
		self.joint3 = joint3
		self.twistAxis = twistAxis
		IkFkBuilder.handle = ''
		IkFkBuilder.newCtrl = ''
		self.ControlCreate = ControlCreate()
	
	def to_String(self):
		print(self.prefix)
		print(self.joint1)
		print(self.joint2)
		print(self.joint3)
		print(self.twistAxis)
		print(IkFkBuilder.handle)
	
	
	#seems the joint chains are some how being parented under the position locators
	def makeLimb(self, limbtype):
		
		#decoloration of vars
		limbtype = limbtype
		prefix = self.prefix
		limb = ['limb_loc_1', 'limb_loc_2','limb_loc_3']
		nameSpace = str(limbtype) + "_"+ str(prefix)
		count = 1
		jntObject = []
		cmds.select(d=True)
		
		
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
		lastJnt = nameSpace + '_Jnt_3'
		
		#reorient joints
		cmds.joint (jntSelect, e =1, oj = "xyz", secondaryAxisOrient= "yup", ch =1, zso =1)
		cmds.joint(lastJnt, e =1,  oj='none', ch=1, zso=1)
		
	def softIK_proc(self, stretch = True , Primary = 'X'):
		#gets input values
		
		name = 'soft'
		ctrlName = self.prefix + "_ikCtrl_1"
		ikhName = IkFkBuilder.handle[0]
		stretch = stretch
		upAxis = self.twistAxis
		primaryAxis = Primary
		
		
		#primary axis options
		if( primaryAxis == 'X'):
			primaryAxis = 'X'
		if( primaryAxis == 'Y'):
			primaryAxis = 'Y'
		if( primaryAxis == 'Z'):
			primaryAxis = 'Z'
	#-----------------------------------------------------------------------------------------------------------------------------#   	
		#finds name for joints
		startJoint = cmds.listConnections( ikhName + ".startJoint" )
		endEffector = cmds.listConnections( ikhName + ".endEffector" )
		endJoint = cmds.listConnections( endEffector, d = False, s = True )
		
		#selects joint chain effected by IKH
		cmds.select( startJoint, hi = True )
		cmds.select( endJoint, hi = True, d = True )
		cmds.select( endEffector, d = True )
		cmds.select( endJoint, tgl = True )
		
		#lists the joints
		joints = []
		joints = cmds.ls( sl = True )
		n = len(joints)
		
		#gives position value for joints
		firstPos = cmds.xform( joints[0], q = True, piv = True, ws = True )
		lastPos = cmds.xform( joints[n - 1], q = True, piv = True, ws = True )
		fPoints  = firstPos[0:3]
		lPoints = lastPos[0:3]
		
		#up axis options
		if( upAxis == 'X'):
			upAxis = 'X'
			gPoint = ( 0, lPoints[1], lPoints[2] )
		if( upAxis == 'Y'):
			upAxis = 'Y'
			gPoint = (lPoints[0], 0, lPoints[2])
		if( upAxis == 'Z'):
			upAxis = 'Z'
			gPoint = ( lPoints[0], lPoints[1], 0)
		
	#-----------------------------------------------------------------------------------------------------------------------------#
		#find the dchain = sum of bone lengths
		i = 0
		dChain = 0
		while ( i < n - 1 ):
			a = cmds.xform( joints[i], q = True, piv = True, ws = True )
			b = cmds.xform( joints[ i + 1 ], q = True, piv = True, ws = True )
			x = b[0] - a[0]
			y = b[1] - a[1]
			z = b[2] - a[2]
			v = [x,y,z]
			dChain += mag(v)
			i += 1
	#-----------------------------------------------------------------------------------------------------------------------------#
		#get the distance from 0 to the ikh
		x = lPoints[0] - gPoint[0]
		y = lPoints[1] - gPoint[1]
		z = lPoints[2] - gPoint[2]
		v = [x,y,z]
		defPos = mag(v)
		if( ( upAxis == 'X' ) and ( lastPos[0] < 0 ) ):
			defPos = defPos * -1
		if( ( upAxis == 'Y' ) and ( lastPos[1] < 0 ) ):
			defPos = defPos * -1
		if( ( upAxis == 'Z' ) and ( lastPos[2] < 0 ) ):
			defPos = defPos * -1
	#-----------------------------------------------------------------------------------------------------------------------------#
		#create the distance node, otherwise know as x(distance between root and ik)
		cmds.spaceLocator( n = '%s_start_dist_loc' % name )
		cmds.xform( '%s_start_dist_loc' % name, t = fPoints, ws = True )
		cmds.spaceLocator( n = '%s_end_dist_loc' % name )
		cmds.xform( '%s_end_dist_loc' % name, t = lPoints, ws = True )
		
		cmds.select( ctrlName, '%s_end_dist_loc' % name, r = True )
		cmds.parentConstraint( w = 1, mo = True)
		# cmds.select( joints[0], '%s_start_dist_loc' % name, r = True )
		# cmds.parentConstraint( w = 1, mo = True)
		
		cmds.createNode( 'distanceBetween', n = '%s_x_distance' % name )
		cmds.connectAttr( '%s_start_dist_loc.translate' % name, '%s_x_distance.point1' % name )
		cmds.connectAttr( '%s_end_dist_loc.translate' % name, '%s_x_distance.point2' % name )
	#-----------------------------------------------------------------------------------------------------------------------------#
		#create the dSoft and softIK attributes on the controller
		cmds.addAttr( ctrlName, ln = 'dSoft', at = "double", min = 0.001, max = 2, dv = 0.001, k = True )
		cmds.addAttr( ctrlName, ln = 'softIK', at = "double", min = 0, max = 20, dv = 0, k = True )
		#make softIK drive dSoft
		cmds.setDrivenKeyframe( '%s.dSoft' % ctrlName, currentDriver = '%s.softIK' % ctrlName )
		cmds.setAttr( '%s.softIK' % ctrlName, 20 )
		cmds.setAttr( '%s.dSoft' % ctrlName, 2 )
		cmds.setDrivenKeyframe( '%s.dSoft' % ctrlName, currentDriver = '%s.softIK' % ctrlName )
		cmds.setAttr( '%s.softIK' % ctrlName, 0 )
		#lock and hide dSoft
		cmds.setAttr( '%s.dSoft' % ctrlName, lock = True, keyable = False, cb = False )
	#-----------------------------------------------------------------------------------------------------------------------------#   	
		#set up node network for soft IK
		cmds.createNode ('plusMinusAverage', n = '%s_da_pma' % name )
		cmds.createNode ('plusMinusAverage', n = '%s_x_minus_da_pma' % name )
		cmds.createNode ('multiplyDivide', n = '%s_negate_x_minus_md' % name )
		cmds.createNode ('multiplyDivide', n = '%s_divBy_dSoft_md' % name )
		cmds.createNode ('multiplyDivide', n = '%s_pow_e_md' % name )
		cmds.createNode ('plusMinusAverage', n = '%s_one_minus_pow_e_pma' % name )
		cmds.createNode ('multiplyDivide', n = '%s_times_dSoft_md' % name )
		cmds.createNode ('plusMinusAverage', n = '%s_plus_da_pma' % name )
		cmds.createNode ('condition', n = '%s_da_cond' % name )
		cmds.createNode ('plusMinusAverage', n = '%s_dist_diff_pma' % name )
		cmds.createNode ('plusMinusAverage', n = '%s_defaultPos_pma' % name )
		
		#set operations
		cmds.setAttr ('%s_da_pma.operation' % name, 2 )
		cmds.setAttr ('%s_x_minus_da_pma.operation' % name, 2 )
		cmds.setAttr ('%s_negate_x_minus_md.operation' % name, 1 )
		cmds.setAttr ('%s_divBy_dSoft_md.operation' % name, 2 )
		cmds.setAttr ('%s_pow_e_md.operation' % name, 3 )
		cmds.setAttr ('%s_one_minus_pow_e_pma.operation' % name, 2 )
		cmds.setAttr ('%s_times_dSoft_md.operation' % name, 1 )
		cmds.setAttr ('%s_plus_da_pma.operation' % name, 1 )
		cmds.setAttr ('%s_da_cond.operation' % name, 5 )
		cmds.setAttr ('%s_dist_diff_pma.operation' % name, 2 )
		cmds.setAttr ('%s_defaultPos_pma.operation' % name, 2 )
		if( ( upAxis == 'X' ) and ( defPos > 0 ) ):
			cmds.setAttr ('%s_defaultPos_pma.operation' % name, 1 )
		if( upAxis == 'Y'):
			cmds.setAttr ('%s_defaultPos_pma.operation' % name, 2 )
		if( ( upAxis == 'Z' ) and ( defPos < 0 ) ):
			cmds.setAttr ('%s_defaultPos_pma.operation' % name, 1 )
	
	#-----------------------------------------------------------------------------------------------------------------------------#   	
		#make connections
		cmds.setAttr( '%s_da_pma.input1D[0]' % name, dChain )
		cmds.connectAttr( '%s.dSoft' % ctrlName, '%s_da_pma.input1D[1]' % name )
		
		cmds.connectAttr( '%s_x_distance.distance' % name, '%s_x_minus_da_pma.input1D[0]' % name )
		cmds.connectAttr( '%s_da_pma.output1D' % name, '%s_x_minus_da_pma.input1D[1]' % name )
		
		cmds.connectAttr( '%s_x_minus_da_pma.output1D' % name, '%s_negate_x_minus_md.input1X' % name )
		cmds.setAttr( '%s_negate_x_minus_md.input2X' % name, -1 )
		
		cmds.connectAttr( '%s_negate_x_minus_md.outputX' % name, '%s_divBy_dSoft_md.input1X' % name )
		cmds.connectAttr( '%s.dSoft' % ctrlName, '%s_divBy_dSoft_md.input2X' % name )
		
		cmds.setAttr( '%s_pow_e_md.input1X' % name, 2.718281828 )
		cmds.connectAttr( '%s_divBy_dSoft_md.outputX' % name, '%s_pow_e_md.input2X' % name )
		
		cmds.setAttr( '%s_one_minus_pow_e_pma.input1D[0]' % name, 1 )
		cmds.connectAttr( '%s_pow_e_md.outputX' % name, '%s_one_minus_pow_e_pma.input1D[1]' % name )
		
		cmds.connectAttr('%s_one_minus_pow_e_pma.output1D' % name, '%s_times_dSoft_md.input1X' % name )
		cmds.connectAttr( '%s.dSoft' % ctrlName, '%s_times_dSoft_md.input2X' % name )
		
		cmds.connectAttr( '%s_times_dSoft_md.outputX' % name, '%s_plus_da_pma.input1D[0]' % name )
		cmds.connectAttr( '%s_da_pma.output1D' % name, '%s_plus_da_pma.input1D[1]' % name )
		
		cmds.connectAttr( '%s_da_pma.output1D' % name, '%s_da_cond.firstTerm' % name )
		cmds.connectAttr( '%s_x_distance.distance' % name, '%s_da_cond.secondTerm' % name )
		cmds.connectAttr( '%s_x_distance.distance' % name, '%s_da_cond.colorIfFalseR' % name )
		cmds.connectAttr( '%s_plus_da_pma.output1D' % name, '%s_da_cond.colorIfTrueR' % name )
		
		cmds.connectAttr( '%s_da_cond.outColorR' % name, '%s_dist_diff_pma.input1D[0]' % name )
		cmds.connectAttr( '%s_x_distance.distance' % name, '%s_dist_diff_pma.input1D[1]' % name )
		
		cmds.setAttr( '%s_defaultPos_pma.input1D[0]' % name, defPos )
		cmds.connectAttr( '%s_dist_diff_pma.output1D' % name, '%s_defaultPos_pma.input1D[1]' % name )
		
		cmds.connectAttr('%s_defaultPos_pma.output1D' % name, '%s.translate%s' % (ikhName, upAxis) )
	#-----------------------------------------------------------------------------------------------------------------------------#
		#if stretch exists, we need to do this...
		
		if( stretch == True ):
			#add attribute to switch between stretchy and non-stretchy
			cmds.addAttr( ctrlName, ln = 'stretchSwitch', at = "double", min = 0, max = 10, dv = 10, k = True )
			
			cmds.createNode ('multiplyDivide', n = '%s_soft_ratio_md' % name )
			cmds.createNode ('blendColors', n = '%s_stretch_blend' % name )
			cmds.createNode ('multDoubleLinear', n = '%s_stretch_switch_mdl' % name )
			
			cmds.setAttr ('%s_soft_ratio_md.operation' % name, 2 )
			cmds.setAttr ('%s_stretch_blend.color2R' % name, 1 )
			cmds.setAttr ('%s_stretch_blend.color1G' % name, defPos )
			cmds.setAttr ('%s_stretch_switch_mdl.input2' % name, 0.1 )
			
			cmds.connectAttr ( '%s.stretchSwitch' % ctrlName, '%s_stretch_switch_mdl.input1' % name )
			cmds.connectAttr ( '%s_stretch_switch_mdl.output' % name, '%s_stretch_blend.blender' % name )
			cmds.connectAttr( '%s_x_distance.distance' % name, '%s_soft_ratio_md.input1X' % name )
			cmds.connectAttr( '%s_da_cond.outColorR' % name, '%s_soft_ratio_md.input2X' % name )
			cmds.connectAttr( '%s_defaultPos_pma.output1D' % name, '%s_stretch_blend.color2G' % name )
			cmds.connectAttr( '%s_soft_ratio_md.outputX' % name, '%s_stretch_blend.color1R' % name )
			
			cmds.connectAttr('%s_stretch_blend.outputG' % name, '%s.translate%s' % (ikhName, upAxis), force = True )
			i = 0
			while ( i < n - 1 ):
				cmds.connectAttr( '%s_stretch_blend.outputR' % name, '%s.scale%s' % (joints[i], primaryAxis), force = True )
				i += 1
	
	def createIkjointChain(self):
		
		#class variables
		startJoint = self.joint1
		midJoint = self.joint2
		endJoint = self.joint3
		ctrlName = self.prefix
		
		
		#creates ikRPSolver
		handle = cmds.ikHandle(sj=startJoint, ee=endJoint, solver="ikRPsolver")
		IkFkBuilder.handle = handle
		ikGroup = cmds.group(handle[0], world=1)
	
		'''
		create a box control at end joint. 
		'''
		#select end joint
		sel = cmds.ls(endJoint)
		
		IkControls = ControlCreate()
		IkControls.createControl(sel, 'ik', ctrlName)
		ikCtrl = IkControls.controllers
		
		#pointConstraint ik to control
		cmds.pointConstraint(ikCtrl[0], ikGroup, mo=1)
		
		IkFkBuilder.newCtrl = ikCtrl
		# sel groups
		'''
		some math for finding pole vector control position
		'''
		#poleVector = startPoint + (unit( crossProduct(perpendicularVector, endVector ) ) * multVal)
		
		
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
		return IkFkBuilder.handle
		
	
	def createFKjointChain(self):
		
		#class Vars
		startJoint = self.joint1
		midJoint = self.joint2
		endJoint = self.joint3
		ctrlName = self.prefix
		
		#list of Vars
		sel = cmds.ls(startJoint,midJoint)
		#creates and names FK controls
		fkControls = ControlCreate()
		fkControls.createControl(sel, 'fk', ctrlName)
		fkCtrls = fkControls.controllers
		
		
		IkFkBuilder.newCtrl = fkCtrls
		
		#create constraints
		cmds.orientConstraint(fkCtrls[0],startJoint, mo=True)
		cmds.orientConstraint(fkCtrls[1],midJoint, mo=True)
		#cmds.orientConstraint(fkCtrls[2],endJoint, mo=True)
		cmds.pointConstraint(startJoint,fkCtrls[0], mo=True)
		cmds.pointConstraint(midJoint,fkCtrls[1], mo=True)
		#cmds.pointConstraint(endJoint,fkCtrls[2], mo=True)
		
		
		item01 = cmds.listRelatives(fkCtrls[0], p=True)
		item02 = cmds.listRelatives(fkCtrls[1], p=True)
		
		groups = [item01, item02]
		#parent fk Controls to each other
		#cmds.parent(groups[2],fkCtrls[1])
		cmds.parent(groups[1],fkCtrls[0])
		

#should increment this in the ikfkCreate class.
def mag( v ):
    return( math.sqrt( pow( v[0], 2) + pow( v[1], 2) + pow( v[2], 2)))

#possible way to source the code.
def findFile(path):
    	for dirname in sys.path:
        	possible = os.path.join(dirname, path)
        	if os.path.isfile(possible):
			return dirname
	return None

#@static
def deleteLocs():
	#create Locators
	varLoc1 = "limb_loc_1"
	varLoc2 = "limb_loc_2"
	varLoc3 = "limb_loc_3"
	
	cmds.delete(varLoc1)
	cmds.delete(varLoc2)
	cmds.delete(varLoc3)


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
	
	#empty vars
	bindChain = []
	ikChain = []
	fkChain = []
	
	#declare class vars
	ikObjects = IkFkBuilder(prefix = 'leg', joint1 = 'limb_loc_1', joint2 =  'limb_loc_2', joint3 =  'limb_loc_3', twistAxis = 'X')
	fkObjects = IkFkBuilder(prefix = 'leg', joint1 = 'limb_loc_1', joint2 =  'limb_loc_2', joint3 =  'limb_loc_3', twistAxis = 'X')
	bindJnts = IkFkBuilder(prefix = 'leg', joint1 = 'limb_loc_1', joint2 =  'limb_loc_2', joint3 =  'limb_loc_3', twistAxis = 'X')
	#does it really need a try statement? 
	try:
		fkObjects.makeLimb("fk")
		ikObjects.makeLimb("ik")
		bindJnts.makeLimb("bn")
		ikObjects.createIkjointChain()
		fkObjects.createFKjointChain()
		ikObjects.softIK_proc()
	except ValueError: 
		cmds.confirmDialog( title='Value Error', message='NameSpace duplicate, Please Rename prefix', button=['Okay'], cancelButton='Okay', dismissString='Okay' )
	
	print(fkObjects.newCtrl)
	#new Vars for each chain
	bindChain = bindJnts.joint1, bindJnts.joint2, bindJnts.joint3
	ikChain = ikObjects.joint1, ikObjects.joint2, ikObjects.joint3
	fkChain = fkObjects.joint1, fkObjects.joint2, fkObjects.joint3
	
	#create binds
	allJoints = BuildChain(bindChain = bindChain,ikChain = ikChain, fkChain = fkChain, prefix = 'leg')
	allJoints.orientBind()
	allJoints.createSwitchCtrl()

createLocs()

createObjects()

#deleteLocs()