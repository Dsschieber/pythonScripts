"""
Author @Doug Schieber
Email DougSchieberAnimation@gmail.com

---------- TO USE ----------
select a polygonal edge
UI will create facial controls based off edge.
includes options for facial controls construction including attaching joints to a nurbs surface or using a center locator for rotation restraints. 




----------------------------

----Functions----

curveFromVertPositions
first
second
third
getUParam
getDagPath
faceCtrlCreate
groupSpecial
attachToNurbsSurface
loadInTextField
createNurbsAttachSurface
createLocatorsUpCenter
clearTextField
facialControlUI
objectPrefix
runControlCreator

----Additions/Bugs----
-create bumper joints
-surface slide joints are in a random order. This is due to the vertex order, should change to go off of curve.cv (fixed)
-runControlCreator method should be broken into smaller parts (added dividers to determine where to make functions)
-different UI setup(DONE!)
	Note: switched over to PySide
-bindjoints need aimconstraints to maintain rotation. (IMPORTANT) This can be seen when parented to hierarchical controls. (FIXED) 
	Note: bind joints should be constrained and not directly parented. 
-sliderJoints need rotation fix. (possibly FIXED)
	Note: Changed to pointconstraint instead. 
-sliderjoints should be the only bind joints in the attach to nurbs surface. (FIXED)
-use local space so that script can attach to parent joint 
	Note: a parent constraint with maintain offset made in nodes
-UI does not load in maya 2017

@WIP
-rename methods	
-nurbs surface hit detection option to allow pulling off the surface
-infinite window on load. Old window needs to destroy itself. 
"""


from maya import cmds, OpenMaya
import pymel.core as pm
from functools import partial
import maya.mel as mel
import sys, os

try:
    from PySide import QtCore, QtUiTools
    from PySide import QtGui as widgets
    from shiboken import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtUiTools
    from PySide2 import QtWidgets as widgets
    from shiboken2 import wrapInstance

def loadUiWidget(uifilename, parent = None):
	loader = QtUiTools.QUiLoader()
	uiFile = QtCore.QFile(uifilename)
	uiFile.open(QtCore.QFile.ReadOnly)
	ui = loader.load(uiFile, parent)
	uiFile.close()
	return ui

def runFaceControlsUI():
    """Command within Maya to run this script"""
    faceControlCreate()
    #does not delete ui at the moment

class faceControlCreate(widgets.QMainWindow):
	
	
	def __init__(self):
		"""Gets maya top window"""
		
		#get directory of UI
		usrProfile = mel.eval('getenv("USERPROFILE")')
		mayaVersion = str(cmds.about(version=True))
		uiFile = (usrProfile+'/Documents/maya/')+mayaVersion+'/scripts/faceControlsMenu.ui' #) why python? 
		
		
		main_window = [o for o in widgets.qApp.topLevelWidgets() if o.objectName()=="MayaWindow"][0]	
		super(faceControlCreate, self).__init__(main_window)
		
		self.faceControlCreate = loadUiWidget(uiFile, main_window)		
		self.faceControlCreate.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		self.connectSignals()
		self.faceControlCreate.show()
	
	def connectSignals(self):
		""" signals for buttons """
		self.faceControlCreate.clearFields_btm.clicked.connect(lambda: self.clearTextField())
		self.faceControlCreate.centerLoc_btm.clicked.connect(lambda: self.loadInTextField(True))
		self.faceControlCreate.upVecLoc_btm.clicked.connect(lambda: self.loadInTextField(False))
		self.faceControlCreate.nurbsSurface_btm.clicked.connect(lambda: self.loadInTextField(False))
		self.faceControlCreate.uPatch_hs.valueChanged.connect(lambda: self.displayLCD())
		self.faceControlCreate.vPatch_hs.valueChanged.connect(lambda: self.displayLCD())
		self.faceControlCreate.createNurbsSurface_btm.clicked.connect(lambda: self.createNurbsAttachSurface())
		self.faceControlCreate.createLoc_btm.clicked.connect(lambda: self.createLocatorsUpCenter())
		self.faceControlCreate.createCtrl_btm.clicked.connect(lambda: self.runControlCreator())
		self.faceControlCreate.setup_btm.clicked.connect(lambda: self.setup())
		self.faceControlCreate.mesh_btm.clicked.connect(lambda: self.populateTextField("mesh"))
		self.faceControlCreate.ctrl_btm.clicked.connect(lambda: self.populateTextField("ctrl"))
		self.faceControlCreate.faces_btm.clicked.connect(lambda: self.populateTextField("faces", True))
	
	def displayLCD(self):
		self.faceControlCreate.uPatch_lcd.display(str(self.faceControlCreate.uPatch_hs.value()))
		self.faceControlCreate.vPatch_lcd.display(str(self.faceControlCreate.vPatch_hs.value()))

	def curveFromVertPositions(self, edges):	
		""" creates a curve from edge selection """
		getEdges= edges
		cmds.select(getEdges)
		mel.eval('polyToCurve -form 2 -degree 1;')
		curveObj=cmds.ls(sl=True)
		return curveObj 
		
		
	
	def first(self, center = '', fromCenter = False, step = 1):
		""" creates joints based on vertices positions or curve.cvs """
		vtx = cmds.ls(sl = 1, fl = 1)
		#is selection curve?
		jnt = []
		n=0
		newVtxList = []
		#loop rebuilds vtx list, encase of high topo
		for i in range(0, len(vtx), step):
			newVtxList.append(vtx[i])
		
		#get vtx pos, set jnt to pos
		for v in newVtxList:
			cmds.select(cl =1) 
			jnt.append( cmds.joint())
			pos = cmds.xform(v , q =1, ws =1, t =1)
			cmds.xform(jnt[n], ws =1, t =pos)
			if fromCenter:
				posC = cmds.xform(center, q =1, ws =1, t =1)
				cmds.select(cl =1)
				jntC = cmds.joint()
				cmds.xform(jntC, ws =1, t =posC)
				cmds.parent(jnt[n], jntC)
				cmds.joint (jntC, e =1, oj = "xyz", secondaryAxisOrient= "yup", ch =1, zso =1)
			n = n + 1
		return jnt
		        
	def second(self, upVector = '', fromCenter = False, objects = []):
		""" creates locators using an objects position in worldspace """
		sel = objects
		allLocs = []
		for s in sel :
			loc = cmds.spaceLocator()[0]
			pos = cmds.xform(s, q =1, ws =1, t =1)
			cmds.xform(loc, ws =1, t =pos)
			#aimconstraint
			if fromCenter:
				par =cmds.listRelatives(s, p =1 ) [0]
				cmds.aimConstraint(loc, par, mo=1, weight=1, aimVector=(1,0,0), upVector=(0,1,0), worldUpType = "object", worldUpObject = upVector)
			allLocs.append(loc)
		return allLocs
	
	def third(self, crv = '', positionObjects = []):
		""" get the locator position on curve then attach locator or object to curve """
		sel = positionObjects
		for s in sel :
			pos = cmds.xform (s ,q = 1 , ws = 1 , t = 1) 
			#unnecessary and does not work. 
			#cross Product nodes
			'''
			ax_Z = cmds.createNode( 'vectorProduct', n = str(s) + '_vectorProduct_ax_Z' )
			ax_X = cmds.createNode( 'vectorProduct', n = str(s) + '_vectorProduct_ax_X' )
			#end product nodes
			fourByFourMatrix = cmds.createNode( 'fourByFourMatrix', n = str(s) + '_fourByFourMatrix' )
			decompose4x4Matrix = cmds.createNode( 'decomposeMatrix', n = str(s) + '_decompose4x4Matrix' )
			'''
			u = self.getUParam(pos, crv)
			#name = s.replace("_LOC" , "_PCI")
			pci = cmds.createNode("pointOnCurveInfo" , n = str(s) + '_pci')
			cmds.connectAttr(crv + '.worldSpace' , pci + '.inputCurve')
			cmds.setAttr(pci + '.parameter' , u )
			cmds.connectAttr( pci + '.position' , s + '.t')
			'''
			#unnecessary and does not work. 
			#set vectorProduct to cross product operation
			cmds.setAttr(ax_Z+".operation", 2)
			cmds.setAttr(ax_X+".operation", 2)
			#finding the cross product for XYZ
			cmds.connectAttr(pci+ ".normalizedTangent", ax_X + ".input1", f= True)
			cmds.connectAttr(pci+ ".normalizedNormal", ax_X + ".input2", f= True)
			cmds.connectAttr(pci+ ".normalizedNormal", ax_Z + ".input1", f= True)
			cmds.connectAttr(ax_X + ".output", ax_Z + ".input2", f = True)
			#euler X
			cmds.connectAttr(ax_X + ".outputX",fourByFourMatrix+".in00",f = True)
			cmds.connectAttr(ax_X + ".outputY",fourByFourMatrix+".in01",f = True)
			cmds.connectAttr(ax_X + ".outputZ",fourByFourMatrix+".in02",f = True)
			#euler Z
			cmds.connectAttr(ax_Z + ".outputX",fourByFourMatrix+".in20",f = True)
			cmds.connectAttr(ax_Z + ".outputY",fourByFourMatrix+".in21",f = True)
			cmds.connectAttr(ax_Z + ".outputZ",fourByFourMatrix+".in22",f = True)
			#euler Y
			cmds.connectAttr(pci+ ".normalizedNormalX",fourByFourMatrix+".in10",f = True)
			cmds.connectAttr(pci+ ".normalizedNormalY",fourByFourMatrix+".in11",f = True)
			cmds.connectAttr(pci+ ".normalizedNormalZ",fourByFourMatrix+".in12",f = True)
			#position
			cmds.connectAttr(pci + ".positionX",fourByFourMatrix+".in30",f = True)
			cmds.connectAttr(pci + ".positionY",fourByFourMatrix+".in31",f = True)
			cmds.connectAttr(pci + ".positionZ",fourByFourMatrix+".in32",f = True)
			
			#at last, output into decomposeMatrix
			cmds.connectAttr(fourByFourMatrix+".output",decompose4x4Matrix+".inputMatrix",f = True)
			cmds.connectAttr(decompose4x4Matrix+".outputTranslate",s +".t",f = True)
			cmds.connectAttr(decompose4x4Matrix+".outputRotate",s + ".rotate",f = True)
			'''
	
	def getUParam(self, pnt = [], crv = None):
		
	    point = OpenMaya.MPoint(pnt[0],pnt[1],pnt[2])
	    curveFn = OpenMaya.MFnNurbsCurve(self.getDagPath(crv))
	    paramUtill=OpenMaya.MScriptUtil()
	    paramPtr=paramUtill.asDoublePtr()
	    isOnCurve = curveFn.isPointOnCurve(point)
	    if isOnCurve == True:
	        curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
	    else :
	        point = curveFn.closestPoint(point,paramPtr,0.001,OpenMaya.MSpace.kObject)
	        curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
	    
	    param = paramUtill.getDouble(paramPtr)  
	    return param
	    
	def getDagPath(self, objectName):
	    
	    if isinstance(objectName, list)==True:
	        oNodeList=[]
	        for o in objectName:
	            selectionList = OpenMaya.MSelectionList()
	            selectionList.add(o)
	            oNode = OpenMaya.MDagPath()
	            selectionList.getDagPath(0, oNode)
	            oNodeList.append(oNode)
	        return oNodeList
	    else:
	        selectionList = OpenMaya.MSelectionList()
	        selectionList.add(objectName)
	        oNode = OpenMaya.MDagPath()
	        selectionList.getDagPath(0, oNode)
	        return oNode
	
	
	def faceCtrlCreate(self, prefix = '', objects = [], controlSize = 1.0):
		""" creates controls from object position """
		ctrls = []
		for stuff in objects:
			# control
			ctrl = mel.eval('curve -d 1 -p 0 1 0 -p 0 0.987688 -0.156435 -p 0 0.951057 -0.309017 -p 0 0.891007 -0.453991 -p 0 0.809017 -0.587786 -p 0 0.707107 -0.707107 -p 0 0.587785 -0.809017 -p 0 0.453991 -0.891007 -p 0 0.309017 -0.951057 -p 0 0.156434 -0.987689 -p 0 0 -1 -p 0 -0.156434 -0.987689 -p 0 -0.309017 -0.951057 -p 0 -0.453991 -0.891007 -p 0 -0.587785 -0.809017 -p 0 -0.707107 -0.707107 -p 0 -0.809017 -0.587786 -p 0 -0.891007 -0.453991 -p 0 -0.951057 -0.309017 -p 0 -0.987688 -0.156435 -p 0 -1 0 -p -4.66211e-09 -0.987688 0.156434 -p -9.20942e-09 -0.951057 0.309017 -p -1.353e-08 -0.891007 0.453991 -p -1.75174e-08 -0.809017 0.587785 -p -2.10734e-08 -0.707107 0.707107 -p -2.41106e-08 -0.587785 0.809017 -p -2.65541e-08 -0.453991 0.891007 -p -2.83437e-08 -0.309017 0.951057 -p -2.94354e-08 -0.156434 0.987688 -p -2.98023e-08 0 1 -p -2.94354e-08 0.156434 0.987688 -p -2.83437e-08 0.309017 0.951057 -p -2.65541e-08 0.453991 0.891007 -p -2.41106e-08 0.587785 0.809017 -p -2.10734e-08 0.707107 0.707107 -p -1.75174e-08 0.809017 0.587785 -p -1.353e-08 0.891007 0.453991 -p -9.20942e-09 0.951057 0.309017 -p -4.66211e-09 0.987688 0.156434 -p 0 1 0 -p -0.156435 0.987688 0 -p -0.309017 0.951057 0 -p -0.453991 0.891007 0 -p -0.587785 0.809017 0 -p -0.707107 0.707107 0 -p -0.809017 0.587785 0 -p -0.891007 0.453991 0 -p -0.951057 0.309017 0 -p -0.987689 0.156434 0 -p -1 0 0 -p -0.987689 -0.156434 0 -p -0.951057 -0.309017 0 -p -0.891007 -0.453991 0 -p -0.809017 -0.587785 0 -p -0.707107 -0.707107 0 -p -0.587785 -0.809017 0 -p -0.453991 -0.891007 0 -p -0.309017 -0.951057 0 -p -0.156435 -0.987688 0 -p 0 -1 0 -p 0.156434 -0.987688 0 -p 0.309017 -0.951057 0 -p 0.453991 -0.891007 0 -p 0.587785 -0.809017 0 -p 0.707107 -0.707107 0 -p 0.809017 -0.587785 0 -p 0.891006 -0.453991 0 -p 0.951057 -0.309017 0 -p 0.987688 -0.156434 0 -p 1 0 0 -p 0.951057 0 -0.309017 -p 0.809018 0 -0.587786 -p 0.587786 0 -0.809017 -p 0.309017 0 -0.951057 -p 0 0 -1 -p -0.309017 0 -0.951057 -p -0.587785 0 -0.809017 -p -0.809017 0 -0.587785 -p -0.951057 0 -0.309017 -p -1 0 0 -p -0.951057 0 0.309017 -p -0.809017 0 0.587785 -p -0.587785 0 0.809017 -p -0.309017 0 0.951057 -p -2.98023e-08 0 1 -p 0.309017 0 0.951057 -p 0.587785 0 0.809017 -p 0.809017 0 0.587785 -p 0.951057 0 0.309017 -p 1 0 0 -p 0.987688 0.156434 0 -p 0.951057 0.309017 0 -p 0.891006 0.453991 0 -p 0.809017 0.587785 0 -p 0.707107 0.707107 0 -p 0.587785 0.809017 0 -p 0.453991 0.891007 0 -p 0.309017 0.951057 0 -p 0.156434 0.987688 0 -p 0 1 0 ;')
			cmds.parentConstraint(stuff,ctrl,mo=False)
			cmds.scale(controlSize, controlSize, controlSize, ctrl, scaleXYZ = True)
			cmds.delete(ctrl,cn=True)
			newName = cmds.rename(prefix+'_ctrl_#')
			ctrls.append(newName)
		return ctrls
	
	def groupSpecial(self, objectSelection = []):
		""" for grouping controllers so they have offset """
		# group list
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
	
	def attachToNurbsSurface(self, prefix = '', nurbSurface = '', surfaceVec = []):
		""" attaches joints to a nurbs surface using a surface vector for position.  """
		#nurbs surface to slide on
		nurbsSurface = cmds.listRelatives(nurbSurface, c=True)
		#point where joints will be attach to surface
		surfacePoint = []
		num = 0
		loc = []
		
		for i in range(len(surfaceVec)):
			loc.append(cmds.spaceLocator())
			pos = cmds.xform(surfaceVec[i], q =1, ws =1, t =1)
			cmds.xform(loc[i], ws =1, t =pos)
			locRN = cmds.rename(loc[i], prefix + "_surfaceSlide_LOC_" + str(num))
			surfacePoint.append(locRN)
			num = num + 1
		
		# ----------------------------------------------------------------------------------
		num = 0 # why is num here? 
		for i in range(len(surfaceVec)):
			#information Nodes
			decomposeMatrix = cmds.createNode('decomposeMatrix', n = surfaceVec[i] + '_decomposeMatrix')
			closestPointOnSurface = cmds.createNode('closestPointOnSurface', n = surfaceVec[i] + '_closestPointOnSurface')
			pointOnSurfaceInfo = cmds.createNode( 'pointOnSurfaceInfo', n = surfaceVec[i] + '_pointOnSurfaceInfo' )
			#cross Product nodes
			ax_Z = cmds.createNode( 'vectorProduct', n = surfaceVec[i] + 'vectorProduct_ax_Z' )
			ax_X = cmds.createNode( 'vectorProduct', n = surfaceVec[i] + 'vectorProduct_ax_X' )
			#end product nodes
			fourByFourMatrix = cmds.createNode( 'fourByFourMatrix', n = surfaceVec[i] + '_fourByFourMatrix' )
			decompose4x4Matrix = cmds.createNode( 'decomposeMatrix', n = surfaceVec[i] + '_decompose4x4Matrix' )
			#set vectorProduct to cross product operation
			cmds.setAttr(ax_Z+".operation", 2)
			cmds.setAttr(ax_X+".operation", 2)
			cmds.setAttr(ax_Z + ".input1X", 1)
			#decompose matrix for surface vector
			cmds.connectAttr(surfaceVec[i]+".worldMatrix[0]", decomposeMatrix+".inputMatrix", f=True)
			#closest point on surface connections
			cmds.connectAttr(nurbsSurface[0]+".worldSpace[0]", closestPointOnSurface+".inputSurface",f=True)
			cmds.connectAttr(decomposeMatrix+".outputTranslate", closestPointOnSurface+".inPosition",f=True)
			#point on Surface connections
			cmds.connectAttr(nurbsSurface[0]+".worldSpace[0]", pointOnSurfaceInfo+".inputSurface", f=True)
			cmds.connectAttr(closestPointOnSurface+".result.parameterV", pointOnSurfaceInfo+".parameterV", f = True)
			cmds.connectAttr(closestPointOnSurface+".result.parameterU", pointOnSurfaceInfo+".parameterU", f = True)
			#finding the cross product for XYZ
			cmds.connectAttr(pointOnSurfaceInfo+ ".result.normal", ax_Z + ".input2", f= True)
			cmds.connectAttr(pointOnSurfaceInfo+ ".result.normal", ax_X + ".input1", f= True)
			cmds.connectAttr(ax_Z + ".output", ax_X + ".input2", f = True)
			#fourByFourConnections
			cmds.connectAttr(ax_X + ".outputX",fourByFourMatrix+".in00",f = True)
			cmds.connectAttr(ax_X + ".outputY",fourByFourMatrix+".in01",f = True)
			cmds.connectAttr(ax_X + ".outputZ",fourByFourMatrix+".in02",f = True)
			
			cmds.connectAttr(ax_Z + ".outputX",fourByFourMatrix+".in20",f = True)
			cmds.connectAttr(ax_Z + ".outputY",fourByFourMatrix+".in21",f = True)
			cmds.connectAttr(ax_Z + ".outputZ",fourByFourMatrix+".in22",f = True)
			#.result.normal.normalZ
			cmds.connectAttr(pointOnSurfaceInfo+ ".result.normal.normalX",fourByFourMatrix+".in10",f = True)
			cmds.connectAttr(pointOnSurfaceInfo+ ".result.normal.normalY",fourByFourMatrix+".in11",f = True)
			cmds.connectAttr(pointOnSurfaceInfo+ ".result.normal.normalZ",fourByFourMatrix+".in12",f = True)
			#position
			cmds.connectAttr(pointOnSurfaceInfo + ".result.position.positionX",fourByFourMatrix+".in30",f = True)
			cmds.connectAttr(pointOnSurfaceInfo + ".result.position.positionY",fourByFourMatrix+".in31",f = True)
			cmds.connectAttr(pointOnSurfaceInfo + ".result.position.positionZ",fourByFourMatrix+".in32",f = True)
			
			#at last, output into decompoeMatrix
			cmds.connectAttr(fourByFourMatrix+".output",decompose4x4Matrix+".inputMatrix",f = True)
			cmds.connectAttr(decompose4x4Matrix+".outputRotate",surfacePoint[i]+".rotate",f = True)
			cmds.connectAttr(decompose4x4Matrix+".outputTranslate",surfacePoint[i]+".translate",f = True)
		
		return surfacePoint
	
	def loadInTextField(self, centerLocator):
		""" this function loads in the nurbs surface in to the GUI """ 
		# Sel
		sel = cmds.ls(sl=True)
		# check
		if (len(sel)==1):
			if (cmds.listRelatives(sel[0],s=True)):
				shapes = cmds.listRelatives(sel[0],s=True)
				types = []
				for stuff in shapes:
					type = cmds.objectType(stuff)
					types.append(type)
				if 'nurbsSurface' in types:
					#cmds.textFieldGrp('nurbsSurfaceTextField',e=True,tx=sel[0])
					self.faceControlCreate.nurbsSurface_le.setText(sel[0] )
					print('complete','Slide Nurbs Surface loaded.')
				elif 'locator' in types and centerLocator==True:
					#cmds.textFieldGrp('centerLocTextField',e=True,tx=sel[0])
					self.faceControlCreate.centerLoc_le.setText(sel[0] )
					print('complete','Center Locator loaded.')
				elif 'locator' in types and centerLocator==False:
					#cmds.textFieldGrp('upVecLocTextField',e=True,tx=sel[0])
					self.faceControlCreate.upVecLoc_le.setText(sel[0])
					print('complete','Up Vector Locator loaded.')
				else:
					print('error','Selection Error, need a Nurbs Surface or Locator to load in.')
	
	
	def createNurbsAttachSurface(self, *args): 
		""" creates a plain nurbs surface. Optionally you can use your own nurbs surface """
		prefix = str(self.faceControlCreate.prefix_le.text())
		uPatches = self.faceControlCreate.uPatch_hs.value()
		vPatches = self.faceControlCreate.vPatch_hs.value()
		nurbsObject = cmds.nurbsPlane( p=[0, 0, 0], ax=[0, 1, 0], w=1, lr=1, d=3, u=uPatches, v=vPatches, ch=1, n=prefix+'_attachSurface#')
		self.faceControlCreate.nurbsSurface_le.setText(nurbsObject[0])
		print('complete','Slide Nurbs Surface loaded.')

	
	def createLocatorsUpCenter(self, *args):
		""" creates an up vector locator and a center locator """
		prefix = str(self.faceControlCreate.prefix_le.text())
		centerLocator = cmds.spaceLocator( n=prefix+'_center_loc#' )
		upVecLocator = cmds.spaceLocator( n=prefix+'_upVec_loc#' )
		
		self.faceControlCreate.centerLoc_le.setText(centerLocator[0])
		self.faceControlCreate.upVecLoc_le.setText(upVecLocator[0])
		print('complete','Locators Loaded.')
	
	def clearTextField(self, *args):
		""" clears text fields in GUI """
		self.faceControlCreate.nurbsSurface_le.setText( "" )
		self.faceControlCreate.upVecLoc_le.setText("" )
		self.faceControlCreate.centerLoc_le.setText("" )
	
	def objectPrefix(self):
		""" checks for duplicate names """
		prefix = str(self.faceControlCreate.prefix_le.text())
		num = 0
		crvNumberPrecheck = []
		
		try:
			cmds.select(prefix + "_*" + "_nonDeform_grp")
			crvNumberPrecheck = cmds.ls( sl=True)
			print(crvNumberPrecheck)
			
		except ValueError:
			#so no error is thrown
			pass
			
		if (len(crvNumberPrecheck)< 0):
			prefix = prefix + '_0'
		else:
			for i in range(len(crvNumberPrecheck)):
				num = num + 1
			prefix = prefix + '_' + str(num)
		return prefix 
	
	def cleanUpControls(self, ctrls, ctrlJNTgrp):
		""" cleans up attrs """
		colorNum = 14
		
		for i in range(len(ctrls)):
			cmds.setAttr(ctrls[i]+'.sx', l=True, k=False, cb=False)
			cmds.setAttr(ctrls[i]+'.sy', l=True, k=False, cb=False)
			cmds.setAttr(ctrls[i]+'.sz', l=True, k=False, cb=False)
			cmds.setAttr(ctrls[i]+'.v', l=True, k=False, cb=False)
			cmds.parentConstraint(ctrls[i], ctrlJNTgrp[i])
			cmds.setAttr(ctrls[i]+".overrideEnabled",1)
			cmds.setAttr(ctrls[i]+".overrideColor",colorNum)
	
	def createControlJoints(self, lowRezCurve, prefix):
		""" creates joints to be skinned to curve """
		cmds.select(lowRezCurve + '.cv[0:4]')
		ctrlTmpJoints = self.first()
		num = len(ctrlTmpJoints)
		ctrlJNTs = []
		
		#rename control joints
		for each in ctrlTmpJoints:
			cmds.setAttr(each + '.v', 0)
			ctrlJNTs.append(cmds.rename(each, prefix + '_ctrlJNT_' + str(len(ctrlTmpJoints) - num)))
			num = num - 1
		return ctrlJNTs
	
	def createLowRezCurve(self, prefix, hiRezCurve):
		""" creates a 3rd degree cv curve """
		tempCrv = cmds.rebuildCurve(hiRezCurve, ch=1, rpo=0,rt=0,end=1, kr=0,kcp=0,kep=1,kt=0,s=2,d=3,tol=0.01)
		cmds.delete(tempCrv, ch=True)
		lowRezCurve = cmds.rename(tempCrv[0],prefix + "_loRez_crv")
		return lowRezCurve
	
	#possibly redundant
	def createBindJoints(self, prefix, tmpJNTs, findYourCenter):
		""" renames joints """
		bindJNTs = []
		num = len(tmpJNTs)
		#rebuild list for naming
		for each in tmpJNTs:
			tEmPbLaH = cmds.listRelatives(each, p=True)
			if findYourCenter:
				cmds.rename(tEmPbLaH, prefix + '_aimJNT_' + str(len(tmpJNTs) - num))
			bindJNTs.append(cmds.rename(each, prefix + '_bnJNT_' + str(len(tmpJNTs) - num)))
			num = num - 1
		return bindJNTs
	
	#redundant??
	def createPinnedLocs(self, prefix, locators):
		""" renames locs """
		pinnedLocs = []
		num = len(locators)
		
		for each in locators:
			pinnedLocs.append(cmds.rename(each, prefix + '_loc_' + str(len(locators) - num)))
			num = num - 1
		return pinnedLocs
	
	
	def runControlCreator(self, *args):
		""" main function """
		#--- main vars
		# ----------------------------------------------------------------------------------
		hierarchyGrp = []
		createSliderJoints = False
		findYourCenter = False
		controlScale = self.faceControlCreate.ctrlSize_dpb.value()
		upVecForCenter = str(self.faceControlCreate.upVecLoc_le.text())
		centerLocator =  str(self.faceControlCreate.centerLoc_le.text())
		nurbSurface = str(self.faceControlCreate.nurbsSurface_le.text())
		
		#checks if vars are empty then sets a booleen var
		if upVecForCenter != '' and centerLocator != '':
			findYourCenter = True
		if nurbSurface != '':
			createSliderJoints = True
		limitHiRexJoints = self.faceControlCreate.jointLimiting_sb.value()
		tmpJNTs = []
		
		#edge in selection
		edges = cmds.ls(sl=True)
		
		#convert selection to vertices
		vertices = cmds.polyListComponentConversion(edges, fe=True, tv=True)
		
		#prefix
		prefix = self.objectPrefix()
		
		
		#create a curve from edge
		curves = self.curveFromVertPositions(edges)
		hiRezCurve = cmds.rename( curves, prefix + "_hiRez_crv") #rename var to hiRezCurve
		hiRezCurveGrp = cmds.group(hiRezCurve, n=hiRezCurve+'_grp')
		
		cmds.delete(hiRezCurve, ch=True)
		cmds.select(hiRezCurve)
		cmds.SelectCurveCVsAll()
		
		#--- bind joints
		# ----------------------------------------------------------------------------------
		tmpJNTs = self.first(center = centerLocator, fromCenter = findYourCenter, step = limitHiRexJoints)
		bindJNTs = self.createBindJoints(prefix, tmpJNTs, findYourCenter)
		jntParent = cmds.listRelatives(bindJNTs, p=True)
		
		#--- locators 
		# ----------------------------------------------------------------------------------
		locators = self.second(upVector = upVecForCenter, fromCenter = findYourCenter, objects = bindJNTs)
		pinnedLocs = self.createPinnedLocs(prefix, locators)
		
		#pin locators to curve
		self.third(hiRezCurve, pinnedLocs)
		
		
		#--- low resolution curve
		lowRezCurve = self.createLowRezCurve(prefix, hiRezCurve)
		lowRezCurveGrp = cmds.group(lowRezCurve, n=lowRezCurve+'_grp')
		cmds.wire( hiRezCurve , w = lowRezCurve, gw= False, en=1.000000, ce=0.000000, li=0.000000, dds=[(0, 100)], n=prefix + '_lowRez_wire')
		
		
		#--- control joints
		ctrlJNTs = self.createControlJoints(lowRezCurve, prefix)
		
		#--- skin Control joints to lowRezCurve and clean up to group
		# ----------------------------------------------------------------------------------
		ctrlJNTgrp = self.groupSpecial(ctrlJNTs)
		hierarchyGrp.append(cmds.group(ctrlJNTgrp, n=prefix +'_ctrlJNTs_grp'))
		cmds.skinCluster(ctrlJNTs, lowRezCurve, dr=4.0, nw=1, mi=1, n = prefix + 'skinClstr')
		
		#--- create Controls for CtrlJnts with offset
		ctrls = self.faceCtrlCreate(prefix = prefix, objects = ctrlJNTgrp, controlSize = controlScale)
		ctrlNulls = self.groupSpecial(ctrls)
		hierarchyGrp.append(cmds.group(ctrlNulls, n=prefix+'_ctrl_grp'))
		
		#--- lock and hide controls, parent to ctrl jnts
		# ----------------------------------------------------------------------------------
		self.cleanUpControls(ctrls, ctrlJNTgrp)
		
		
		#--- group everything to where it will need to be grouped (for scaling and organization)
		# ----------------------------------------------------------------------------------
		if findYourCenter:
			hierarchyGrp.append(cmds.group(jntParent, n=prefix + 'joint_grp'))
			hierarchyGrp.append(cmds.group(pinnedLocs, n=prefix +'locator_grp'))
			scaleGrp = cmds.group(hierarchyGrp[0], hierarchyGrp[1], hierarchyGrp[2], upVecForCenter, centerLocator, n=prefix+'_scale_grp')
			nonDeformableGrp = cmds.group(hiRezCurveGrp, lowRezCurveGrp, hierarchyGrp[3], n = prefix + '_nonDeform_grp')
			centerPivotScaleGrp = cmds.group(centerLocator, n = prefix + '_scale_grp')
			#parent under center locator?
		
		else:
			if createSliderJoints == False:
				for i in range(len(bindJNTs)):
					#parentConstraint -mo -skipRotate x -skipRotate y -skipRotate z -weight 1;
					cmds.pointConstraint(pinnedLocs[i], bindJNTs[i])
			hierarchyGrp.append(cmds.group(pinnedLocs, n=prefix + '_locator_grp'))
			hierarchyGrp.append(cmds.group(bindJNTs, n=prefix + '_bindJnts_grp'))
			scaleGrp = cmds.group(hierarchyGrp[0], hierarchyGrp[1], hierarchyGrp[3], n=prefix+'_scale_grp')
			nonDeformableGrp = cmds.group(hiRezCurveGrp, lowRezCurveGrp, hierarchyGrp[2], n = prefix + '_nonDeform_grp')
			for each in bindJNTs:
				cmds.scaleConstraint(scaleGrp, each)		
		
		if createSliderJoints:
			#slider joints is actually locators now. 
			sliderJoints = self.attachToNurbsSurface(prefix, nurbSurface, pinnedLocs)
			for i in range(len(bindJNTs)):
				cmds.pointConstraint(sliderJoints[i], bindJNTs[i], mo=True)
			sliderJointsGrp = cmds.group(sliderJoints, n=prefix + '_sliderJNT_grp')
			cmds.parent(sliderJointsGrp, nonDeformableGrp )
		
		if (createSliderJoints == True and findYourCenter == True):
			for each in sliderJoints: 
				cmds.scaleConstraint(centerLocator, each)
				
		elif(createSliderJoints == True and findYourCenter == False):
			for each in sliderJoints: 
				cmds.scaleConstraint(scaleGrp, each)		
		print(hierarchyGrp)
	
	#--- this section was written by Raveen Rajadorai
	#--- which was based off the videos done by Harry Houghton had also made a video tutorial outlining the process (https://vimeo.com/94663329)
	#--- I take no credit for what was writtne below this point. I only added it to my UI

	def cleanNodes(self):
		for node in pm.listHistory(self.ctrl.controls[0], lv=0):
			print node
			if node.nodeType() == "transformGeometry":
				node.ihi.set(0)
			elif node.nodeType() == "deleteComponent":
				node.rename("{0}_DC".format(self.ctrl.controls[0]))
				node.ihi.set(0)
			elif node.nodeType() == "multMatrix":
				node.ihi.set(0)
	
	def transformGeometrySetup(self):
		tgNode = pm.createNode("transformGeometry", n="{0}_TG".format(self.ctrl.controls[0]))
		self.meshes.source.getShape().outMesh.connect(tgNode.inputGeometry)
		
		if self.faceControlCreate.includeMeshTrans_cb.isChecked():
			multMatNode = pm.createNode("multMatrix",n="{0}_MM".format(self.ctrl.controls[0]))
			self.meshes.source.worldMatrix.connect(multMatNode.matrixIn[0])
			self.ctrl.controls[0].worldInverseMatrix.connect(multMatNode.matrixIn[1])       
			multMatNode.matrixSum.connect(tgNode.transform)
			tgNode.outputGeometry.connect(self.deformingShape.inMesh)
		else:
			self.ctrl.controls[0].worldInverseMatrix.connect(tgNode.transform)        
			tgNode.outputGeometry.connect(self.deformingShape.inMesh)
	
	def setup(self,*args):
		self.ctrl = Controllers()
		self.meshes = Meshes()
		faceLineEdit = str(self.faceControlCreate.faces_le.text())
		faceSelection = faceLineEdit.split(",")
		self.deformingShape = ''
		
		self.ctrl.controls = pm.PyNode(str(self.faceControlCreate.ctrl_le.text()))
		self.meshes.source = pm.PyNode(str(self.faceControlCreate.mech_le.text()))
		self.meshes.target = self.meshes.source
		
		self.updateCtrlShape(self.ctrl.controls[0],self.meshes.target)
		self.transformGeometrySetup()
		self.deleteFaces(self.meshes.source,self.deformingShape,faceSelection)
		self.cleanNodes()
	
	def updateCtrlShape(self, controller,targetMesh):
		if not self.faceControlCreate.retainOG_cb.isChecked():
			pm.delete(self.ctrl.origShapes[controller])
		defShape = targetMesh.getShape()
		pm.parent(targetMesh.getShape(),controller,r=1,s=1)
		defShape.rename("{0}Shape".format(controller))
		self.deformingShape = defShape
		# Duplicated mesh's transform, don't need it anymore.
		pm.delete(targetMesh)  
	
	def deleteFaces(self,src, targ,faceSelection):
		srcDagPath = self.getDagPath(str(src))
		sourceMeshFaces = OpenMaya.MItMeshPolygon(srcDagPath)
		targetMeshFaceInds = [int(ind.rpartition(".")[-1].strip("f[").strip("]")) for ind in faceSelection]
		targetFaceIndList = []
		while not sourceMeshFaces.isDone():
			srcFaceInd = sourceMeshFaces.index()
			if srcFaceInd in targetMeshFaceInds:
				pass
			else:
				targetFaceIndList.append(srcFaceInd)
			sourceMeshFaces.next() #Iterate vert
		print pm.delete(targ.f[targetFaceIndList])
	
	def populateTextField(self, control,faces=False):
		print("working")
		# sel=pm.selected(fl=1)
		sel=pm.ls(sl=1,fl=1)
		if len(sel):
			# Cheap component error checking, will convert this to proper api calls soon.
			if faces:
				faceStrings = ''
				for s in sel:
					if ".f" in str(s):
						if s == sel[-1]:faceStrings += "{0}".format(str(s))
						else:faceStrings += "{0},".format(str(s))
					else: 
						pm.error("Please select faces!")
						continue
				self.faceControlCreate.faces_le.setText(str(faceStrings))
				#pm.textFieldButtonGrp( control,e=1,text=str(faceStrings))
			else:
				if control == "mesh":
					self.faceControlCreate.mech_le.setText(str(sel[0]))
				else:
					self.faceControlCreate.ctrl_le.setText(str(sel[0]))
		else:
			pm.error("No object selected. Please select an object!")
			

class Controllers(object):
	def __init__(self):
		self.controlsList = []
		self.origShapes = {}
	
	@property
	def controls(self):
		if self.controlsList is None:
			pm.error("No controls specified")
		else:
			return self.controlsList
	
	@controls.setter
	def controls(self, value):
		self.controlsList.append(value)
		self.origShapes[value] = value.getShapes()

	def clear(self):
		self.controlsList = []


class Meshes(object):
	def __init__(self):
		self.sourceMesh = None
		self.targetMesh = None
	
	@property
	def source(self):
		return self.sourceMesh
	
	@source.setter
	def source(self, value):
		self.sourceMesh = pm.PyNode(value)
	
	@property
	def target(self):
		return self.targetMesh
	
	@target.setter
	def target(self, source):
		dup = pm.duplicate(source)[0]
		# pm.select(dup,r=1)
		# pm.mel.eval("hyperShade -assign lambert1")
		
		for dAttr in ["displayBorders","displayEdges"]:
			dup.getShape().attr(dAttr).set(1)
	
		for attr in ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]:
			dup.attr(attr).unlock()
		self.targetMesh = dup
