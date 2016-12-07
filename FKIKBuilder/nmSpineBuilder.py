'''

Auto Spine Set-Up

#Three Controls
#awesomeSpline


'''

#import shits
from maya import cmds, OpenMaya
import os, sys
import maya.cmds as cmds 
import maya.mel as mel
import pymel.core as pm
import math


class NM_buildSpine(object):
	#class Vars
	jointChain = ''
	ctrlJntChain = ''
	
	def __init__(self, jointNumber, prefix, strCurve, ctrlNumber):
		self.jointNumber = jointNumber
		self.prefix = prefix
		self.strCurve = strCurve
		self.ctrlNumber = ctrlNumber
		NM_buildSpine.jointChain = ''
		NM_buildSpine.ctrlJntChain = ''
		
	#builds the joint Chains
	def nm_ikCreate(self):
		strCurve = self.strCurve
		jointNumber = self.jointNumber
		ctrlNumber = self.ctrlNumber
		NM_buildSpine.jointChain = ""
		#ctrlName = ctrlName
		lStrJnt = []
		
		if not strCurve:
			cmds.ls(sl=True)[0]
		
		
		cmds.select(cl=True)
		name = ''
		iNum = jointNumber
		name = strCurve+'_ik'+'_jnt'
		
		for i in range(iNum):
			#creates joint chain
			strI = '%s' %i
			strJnt = cmds.joint(n=name+strI)
			lStrJnt.append(strJnt)
		
		#create ikhandle
		strCurveIk = cmds.ikHandle(sj=lStrJnt[0], ee=lStrJnt[-1], c=strCurve, n=strCurve+'_ik', sol='ikSplineSolver', ccv=False, rootOnCurve=True, parentCurve=False)[0] 
		
		#create ArcLen on curve
		gArcLen = cmds.arclen(strCurve)
		
		gAverage = gArcLen/(iNum-1)
		
		for i in range(iNum):
			if i > 0:
				cmds.setAttr(lStrJnt[i]+'.tx', gAverage)	
		NM_buildSpine.jointChain = lStrJnt
	'''
	targetCurve = strCurve # Curve to put clusters on
	curveCVs = Mc.ls('{0}.cv[:]'.format(targetCurve), fl = True) # Get all cvs from curve
	if curveCVs: # Check if we found any cvs
	    for cv in curveCVs:
	        print 'Creating {0}'.format(cv)
	        Mc.cluster(cv, name=targetCurve+'_cl') # Create cluster on a cv
	else:
	    Mc.warning('Found no cvs!')  
	'''
	def nm_ctrlOnCurve(self, ctrlSize):
		
		name = self.prefix
		bindNum = self.ctrlNumber	
		size = ctrlSize
		mirror = 0
		
		#joint LRA
		X = True
		Y = False
		Z = False
		
		
		bindBox = True
		attachBox = True
		bindShape = 3
		
		bindSeg = 8
		if ( bindShape > 1 ):
			bindDeg = 1
		if ( bindShape == 1 ):
			bindDeg = 3
		if ( bindShape == 3 ):
			bindSeg = 6
		if ( bindShape == 4 ):
			bindSeg = 4
	
	#=========================================================================================================================================================================#    
	#=========================================================================================================================================================================#   
		
		sel = cmds.ls( sl = True )
		sel = str(sel)[3:][:-2]
		cmds.pickWalk( d = 'down' )
		shape = cmds.ls( sl = True )
		shape = str(shape)[3:][:-2]
		#mirror names
		#-first half (right)
		#-middle
		#-second half (left)		
		#create the number of joints/ctrls along the selected curve
		
		half = bindNum / 2
		#if i is odd
		if( bindNum % 2 == 1 ):
			half = half - 0.5
		i = 0
	#=========================================================================================================================================================================#    
	#=========================================================================================================================================================================#    
		
		if( bindBox == 1 ):
		
			#create the bind joints/ctrls
			i = 0
			bindList = [ ]
			rl = half
			doggy = half
			while( i < bindNum ):
				if( mirror != 1 ):
					ctrl = i+1
					
				
				cmds.select( d = True )
				cmds.joint( p = (0,0,0), rad = 3, n = '{0}_curve_bind_{1}_joint'.format(name, ctrl) )
				cmds.select( d = True )
				
				bindList.append( '{0}_curve_bind_{1}_joint'.format (name, ctrl) )
				
				cmds.circle( n = '{0}_all_{1}_anim'.format (name, ctrl), r = 2 * size, nr = (X,Y,Z), d = bindDeg, s = bindSeg )
				cmds.delete( ch = True )
				groupSpecial()
				
				cmds.createNode( 'pointOnCurveInfo', n = '{0}_curve_bind_{1}_poc'.format (name, ctrl) )
				cmds.setAttr( '{0}_curve_bind_{1}_poc.turnOnPercentage'.format (name, ctrl), 1 )
				cmds.connectAttr( '{0}.worldSpace'.format(shape), '{0}_curve_bind_{1}_poc.inputCurve'.format (name, ctrl) )
				
				
				if( i == 0 ):
					cmds.setAttr( '{0}_curve_bind_{1}_poc.parameter'.format(name, ctrl), 0 )
				if( i == bindNum - 1 ):
					cmds.setAttr( '{0}_curve_bind_{1}_poc.parameter'.format(name, ctrl), 1 )
				else:
					ic = 100.0 / (bindNum-1)
					ic = ic/100.0
					ic = ic * i
					cmds.setAttr( '{0}_curve_bind_{1}_poc.parameter'.format(name, ctrl), ic )
					cmds.getAttr('{0}_curve_bind_{1}_poc.parameter'.format(name, ctrl))
	
				px = cmds.getAttr( '{0}_curve_bind_{1}_poc.positionX'.format (name, ctrl) )
				py = cmds.getAttr( '{0}_curve_bind_{1}_poc.positionY'.format (name, ctrl) )
				pz = cmds.getAttr( '{0}_curve_bind_{1}_poc.positionZ'.format (name, ctrl) )
				cmds.setAttr( '{0}_curve_bind_{1}_joint.tx'.format(name, ctrl), px )
				cmds.setAttr( '{0}_curve_bind_{1}_joint.ty'.format(name, ctrl), py )
				cmds.setAttr( '{0}_curve_bind_{1}_joint.tz'.format(name, ctrl), pz )
				cmds.setAttr( '{0}_all_{1}_anim_grp.tx'.format(name, ctrl), px )
				cmds.setAttr( '{0}_all_{1}_anim_grp.ty'.format(name, ctrl), py )
				cmds.setAttr( '{0}_all_{1}_anim_grp.tz'.format(name, ctrl), pz )
	
				cmds.select(  '{0}_curve_bind_{1}_joint'.format(name, ctrl), r = True )
				groupSpecial()
				
				cmds.connectAttr( '{0}_all_{1}_anim.translate'.format(name, ctrl), '{0}_curve_bind_{1}_joint_grp.translate'.format(name, ctrl) )
				cmds.connectAttr( '{0}_all_{1}_anim.rotate'.format(name, ctrl), '{0}_curve_bind_{1}_joint_grp.rotate'.format(name, ctrl) )
				cmds.delete( '{0}_curve_bind_{1}_poc'.format(name, ctrl) )
	
				if( rl > 0 ):
					doggy -= 1
				if( rl <= 0 ):
					doggy += 1
				if( bindNum % 2 != 1 and rl == 1):
					doggy = 1
					
				
				rl -= 1
				i += 1
				
				
				
			cmds.select( bindList, sel, r = True )
			cmds.skinCluster()
			NM_buildSpine.ctrlJntChain = bindList
			
		try:
			cmds.rename( 'c_{0}_0_anim'.format(name), 'c_{0}_anim'.format(name) )
			cmds.rename( 'c_{0}_0_anim_grp'.format(name), 'c_{0}_anim_grp'.format(name))
			cmds.rename( 'c_{0}_0_joint'.format(name), 'c_{0}_joint'.format(name))
			cmds.rename( 'c_{0}_0_joint_grp'.format(name), 'c_{0}_joint_grp'.format(name))
			cmds.rename( 'c_{0}_0_poc'.format(name), 'c_{0}_poc'.format(name))
		except:
			print("no mas")
			
		try:
			cmds.rename( 'c_{0}_all_0_anim'.format(name), 'c_{0}_all_anim'.format(name))
			cmds.rename( 'c_{0}_all_0_anim_grp'.format(name), 'c_{0}_all_anim_grp'.format(name))
			cmds.rename( 'c_{0}_curve_bind_0_joint'.format(name), 'c_{0}_curve_bind_joint'.format(name))
			cmds.rename( 'c_{0}_curve_bind_0_joint_grp'.format(name), 'c_{0}_curve_bind_joint_grp'.format(name))
			cmds.rename( 'c_{0}_0_joint_offset_grp'.format(name), 'c_{0}_joint_offset_grp'.format(name))
		except:
			print 'no Cs, dog.'
			
		if( attachBox == 0 and mirror == 0):
			cmds.select( '{0}_*_poc'.format(name) )
			cmds.delete( cmds.ls( sl = True) )
		if( attachBox == 0 and mirror == 1):
			cmds.select( '*_{0}_*_poc'.format(name) )
			cmds.delete( cmds.ls( sl = True) )
			
def groupSpecial():

	sel = []
	sel = cmds.ls( sl = True )
	selSize = len(sel)

	lastPos = cmds.xform( sel[selSize - 1], q = True, piv = True, ws = True )
	lPoints  = lastPos[0:3]

	cmds.group( n = sel[selSize - 1] + '_grp' )
	cmds.xform(  ws = True, piv = lPoints )	


sel = cmds.ls(sl=True)
y = NM_buildSpine(jointNumber = 10, prefix = "noNoMas", strCurve = sel[0], ctrlNumber = 4)
y.nm_ctrlOnCurve(ctrlSize = 1.0)
#construct joint ik chain
y.nm_ikCreate()
#x.nm_ikCreate(isControl = True)

#print(x.jointChain)
print(y.ctrlJntChain)
