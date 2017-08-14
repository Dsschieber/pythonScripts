'''
Author @Doug Schieber
Email DougSchieberAnimation@gmail.com


Functions
-Takes edge information and creates an edge with joints and controls attached

Future Additions
-attach to nurbs surface
-use center locator pivot
-create upVec and centerLocator
-attach objects to parent (say a jaw joint or etc)

'''


from maya import cmds, OpenMaya
import maya.mel as mel


'''
creates a curve from edge selection

'''
def curveFromVertPositions(edges):
	
	getEdges= edges
	cmds.select(getEdges)
	mel.eval('polyToCurve -form 2 -degree 1;')
	curveObj=cmds.ls(sl=True)
	return curveObj 
	
'''
change for loop to range, add a step to do every other jnt to reduce joint amount? 
set radius on jnts? 

creates joints based on vertices positions
'''
def first(center = '', fromCenter = False, step = 1):
	vtx = cmds.ls(sl = 1, fl = 1)
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
		if fromCenter == True:
			posC = cmds.xform(center, q =1, ws =1, t =1)
			cmds.select(cl =1)
			jntC = cmds.joint()
			cmds.xform(jntC, ws =1, t =posC)
			cmds.parent(jnt[n], jntC)
			cmds.joint (jntC, e =1, oj = "xyz", secondaryAxisOrient= "yup", ch =1, zso =1)
		n = n + 1
	return jnt
	        
'''
creates locators using an objects position in worldspace

'''
def second(upVector = '', fromCenter = False, objects = []):
	
	sel = objects
	allLocs = []
	for s in sel :
		loc = cmds.spaceLocator()[0]
		pos = cmds.xform(s, q =1, ws =1, t =1)
		cmds.xform(loc, ws =1, t =pos)
		#aimconstraint
		if fromCenter == True:
			par =cmds.listRelatives(s, p =1 ) [0]
			cmds.aimConstraint(loc, par, mo=1, weight=1, aimVector=(1,0,0), upVector=(0,1,0), worldUpType = "object", worldUpObject = upVector)
		allLocs.append(loc)
	return allLocs

'''
get the locator position on curve then attach locator or object to curve

'''


def third(crv = '', positionObjects = []):
    sel = positionObjects
    for s in sel :
        pos = cmds.xform (s ,q = 1 , ws = 1 , t = 1)
        u = getUParam(pos, crv)
        name = s.replace("_LOC" , "_PCI")
        pci = cmds.createNode("pointOnCurveInfo" , n = name)
        cmds.connectAttr(crv + '.worldSpace' , pci + '.inputCurve')
        cmds.setAttr(pci + '.parameter' , u )
        cmds.connectAttr( pci + '.position' , s + '.t')

def getUParam( pnt = [], crv = None):
	
    point = OpenMaya.MPoint(pnt[0],pnt[1],pnt[2])
    #curveFn = OpenMaya.MFnNurbsCurve(getDagPath(crv))
    curveFn = OpenMaya.MFnNurbsCurve(getDagPath(crv))
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
    
def getDagPath( objectName):
    
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
'''
creates controls from object position


'''

def faceCtrlCreate(prefix = '', objects = [], controlSize = 1.0):
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


'''
for grouping controllers so they have offset

'''


def groupSpecial(objectSelection = []):
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

#add prefix argument
def attachToNurbsSurface(prefix = '', nurbSurface = '', surfaceVec = []):
	#nurbs surface to slide on
	nurbsSurface = cmds.listRelatives(nurbSurface, c=True)
	#point where joints will be attach to surface
	surfacePoint = []
	num = 0
	jnt = []
	for i in range(len(surfaceVec)):
		jnt.append(cmds.joint())
		cmds.parent(jnt[i], w = True)
		pos = cmds.xform(surfaceVec[i], q =1, ws =1, t =1)
		cmds.xform(jnt[i], ws =1, t =pos)
		jntRN = cmds.rename(jnt[i], prefix + "_surfaceSlide_bn_JNT_" + str(num))
		surfacePoint.append(jntRN)
		num = num + 1
	
	num = 0
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

'''

UI will be implemented later

instructions: select an edge and make some nice face controls

Everything below should be broken up into functions for organization. 


'''
def loadInTextField(centerLocator):
	'''
	this function loads in the nurbs surface
	'''
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
				cmds.textFieldGrp('nurbsSurfaceTextField',e=True,tx=sel[0])
				print('complete','Slide Nurbs Surface loaded.')
			elif 'locator' in types and centerLocator==True:
				cmds.textFieldGrp('centerLocTextField',e=True,tx=sel[0])
				print('complete','Center Locator loaded.')
			elif 'locator' in types and centerLocator==False:
				cmds.textFieldGrp('upVecLocTextField',e=True,tx=sel[0])
				print('complete','Up Vector Locator loaded.')
			else:
				print('error','Selection Error, need a Nurbs Surface or Locator to load in.')

def createNurbsAttachSurface(*args):
	prefix = cmds.textFieldGrp("prefixTextField", query = True, text = True)
	uPatches = cmds.intSliderGrp ( "uvFieldNameU", query = True, value = True)
	vPatches = cmds.intSliderGrp ( "uvFieldNameV", query = True, value = True)
	nurbsObject = cmds.nurbsPlane( p=[0, 0, 0], ax=[0, 1, 0], w=1, lr=1, d=3, u=uPatches, v=vPatches, ch=1, n=prefix+'_attachSurface#')
	cmds.textFieldGrp('nurbsSurfaceTextField',e=True,tx=nurbsObject[0])
	print('complete','Slide Nurbs Surface loaded.')

def createLocatorsUpCenter(*args):
	prefix = cmds.textFieldGrp("prefixTextField", query = True, text = True)
	centerLocator = cmds.spaceLocator( n=prefix+'_center_loc#' )
	upVecLocator = cmds.spaceLocator( n=prefix+'_upVec_loc#' )
	
	cmds.textFieldGrp('centerLocTextField',e=True,tx=centerLocator[0])
	cmds.textFieldGrp('upVecLocTextField',e=True,tx=upVecLocator[0])
	print('complete','Locators Loaded.')

def clearTextField(*args):
	cmds.textFieldGrp('nurbsSurfaceTextField',e=True,tx='')
	cmds.textFieldGrp('centerLocTextField',e=True,tx='')
	cmds.textFieldGrp('upVecLocTextField',e=True,tx='')

def facialControlUI():
	#create Window
	faceCtrlWindowName = "faceCtrlWindowUI"
	if (cmds.window(faceCtrlWindowName, exists=True )):
		cmds.deleteUI( faceCtrlWindowName)
	faceCtrlWindow = cmds.window(faceCtrlWindowName, title="Face Controls Creator Menu", maximizeButton=True, sizeable=True)
	
	#load In Locators and Nurbs
	cmds.columnLayout('mainCol')
	cmds.tabLayout("tabLayoutName01", p = 'mainCol')
	cmds.columnLayout("columnLayoutName01", adjustableColumn = True, p='tabLayoutName01')
	cmds.tabLayout("tabLayoutName01", e=True, tl=[('columnLayoutName01','GEN')])
	cmds.frameLayout(  "nurbsLayoutName01", label = "Nurbs Surface Editor", collapsable = True, parent = "columnLayoutName01")
	
	cmds.text(l='', h = 10, p="nurbsLayoutName01")
	cmds.textFieldGrp( "nurbsSurfaceTextField", l = "Loaded Nurbs Surface:    ", ed = False, parent = "nurbsLayoutName01")
	cmds.text(l='', h = 10, p="nurbsLayoutName01")
	cmds.intSliderGrp ( "uvFieldNameU", label = "    U Patches:", field = True, fieldMinValue = 0, fieldMaxValue = 10, minValue = 1, maxValue = 10, columnWidth3 = [80, 50, 50], columnAlign3 = ["left", "both", "left"], value = 1, parent = "nurbsLayoutName01")
	cmds.intSliderGrp ( "uvFieldNameV", label = "    V Patches:", field = True, fieldMinValue = 0, fieldMaxValue = 10, minValue = 1, maxValue = 10, columnWidth3 = [80, 50, 50], columnAlign3 = ["left", "both", "left"], value = 1, parent = "nurbsLayoutName01")
	cmds.separator(h = 20, p="nurbsLayoutName01")
	
	
	cmds.rowLayout( "nurbsButtonGridLayout", numberOfColumns=5, columnWidth5=[20, 120, 80, 120, 20], p = "nurbsLayoutName01")
	cmds.separator( p= "nurbsButtonGridLayout", h = 80)
	cmds.button(l = 'Load Nurbs Surface', c= loadInTextField, parent = "nurbsButtonGridLayout", h = 60)
	cmds.separator( p= "nurbsButtonGridLayout", h = 80)
	cmds.button( l = 'Create Nurbs Surface', c= createNurbsAttachSurface, parent = "nurbsButtonGridLayout", h = 60)
	cmds.separator( p= "nurbsButtonGridLayout", h = 80)
	cmds.text(l='', h = 10, p="nurbsLayoutName01")
	
	cmds.frameLayout ("locsLayoutName01", label = "Locator Objects", collapsable = True, parent = "columnLayoutName01")
	
	cmds.text(l='', h = 10, p="locsLayoutName01")
	cmds.textFieldGrp( "centerLocTextField", l = "Loaded Center Object:     ", ed = False, parent = "locsLayoutName01")
	cmds.rowLayout( "centerButtonRowLayout", numberOfColumns=3, columnWidth3=[130, 120, 120], p = "locsLayoutName01")
	cmds.text(l='', h = 10, p="centerButtonRowLayout")
	cmds.text(l='', h = 10, p="centerButtonRowLayout")
	cmds.button( l = 'Load Center Locator', c= "loadInTextField(True)", parent = "centerButtonRowLayout", h=30, w = 120 )
	
	cmds.separator( p= "locsLayoutName01", h = 10)
	
	
	cmds.textFieldGrp( "upVecLocTextField", l = "Loaded UpVec Object:     ", ed = False, parent = "locsLayoutName01")
	
	cmds.rowLayout( "upVecButtonRowLayout", numberOfColumns=3, columnWidth3=[130, 120, 120], p = "locsLayoutName01")
	cmds.text(l='', h = 10, p="upVecButtonRowLayout")
	cmds.text(l='', h = 10, p="upVecButtonRowLayout")
	cmds.button(l = 'Load UpVec Locator', c= "loadInTextField(False)", parent = "upVecButtonRowLayout", h=30, w = 120)
	
	cmds.separator( p= "locsLayoutName01", h = 10)
	
	cmds.button(l = 'Create UpVec and Center Locator', c= createLocatorsUpCenter, parent = "locsLayoutName01")
	cmds.text(l='', h = 10, p="locsLayoutName01")
	
	
	cmds.frameLayout("sizeLayout01", label = "Extras", collapsable = True, parent = "columnLayoutName01")
	cmds.gridLayout( "ctrlSizeLayout01", nr=1, cw = 103, p = 'sizeLayout01')
	cmds.text(l='Controller Size:', h = 20, p="ctrlSizeLayout01")
	cmds.floatField("floatFieldName", minValue = 0.0, maxValue = 100.0, precision = 2, value = 1.0, parent = "ctrlSizeLayout01")
	
	cmds.intSliderGrp ( "intFieldName", label = "       Joint Limiter:", field = True, fieldMinValue = 0, fieldMaxValue = 10, minValue = 1, maxValue = 10, columnWidth3 = [100, 50, 50], columnAlign3 = ["left", "both", "left"], value = 1, parent = "sizeLayout01")
	cmds.text(l='', h = 10, p="sizeLayout01")
	
	cmds.separator(p='columnLayoutName01')
	cmds.text(l='', h = 10, p="columnLayoutName01")
	cmds.textFieldGrp( "prefixTextField", l = "Prefix:     ", cw2 = [100, 250], parent = "columnLayoutName01")
	cmds.text(l='', h = 10, p="columnLayoutName01")
	cmds.button(l = 'Clear Fields', c = clearTextField, p = "columnLayoutName01")
	cmds.button(l = 'Select a Polygon Edge to create controls', c = runControlCreator, p = "columnLayoutName01")
	
	#show Window
	cmds.showWindow(faceCtrlWindowName)
	
	# This is a workaround to get MEL global variable value in Python
	gMainWindow = mel.eval('$tmpVar=$gMainWindow')
	cmds.window( faceCtrlWindowName, edit=True)

'''
check for duplicate names

'''

def objectPrefix():
	prefix = cmds.textFieldGrp("prefixTextField", query = True, text = True)
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

def runControlCreator(*args):
		
	#hierarchy groups
	hierarchyGrp = []
	createSliderJoints = False
	findYourCenter = False
	controlScale = cmds.floatField( "floatFieldName", query = True, value = True)
	#why does maya hate unicode?
	upVecForCenter = cmds.textFieldGrp("upVecLocTextField", query = True, text = True)
	centerLocator = cmds.textFieldGrp("centerLocTextField", query = True, text = True)
	nurbSurface = cmds.textFieldGrp("nurbsSurfaceTextField", query = True, text = True)
	if upVecForCenter != '' and centerLocator != '':
		findYourCenter = True
	if nurbSurface != '':
		createSliderJoints = True
	#limit the amount of joints for hiRez topo
	limitHiRexJoints = cmds.intSliderGrp ( "intFieldName", query = True, value = True)
	tmpJNTs = []
	
	#edge is selected
	edges = cmds.ls(sl=True)
	
	#convert selection to vertices
	vertices = cmds.polyListComponentConversion(edges, fe=True, tv=True)
	
	#prefix
	prefix = objectPrefix()
	
	#create a curve from edge
	curves = curveFromVertPositions(edges)
	curveObj = cmds.rename( curves, prefix + "_hiRez_crv")
	hiRezCurveGrp = cmds.group(curveObj, n=curveObj+'_grp')
	cmds.select(vertices)
	cmds.delete(curveObj, ch=True)
	
	
	#var determines if there will be a aim constraint based crv or a parent based. 
	#center would best be used for eyes where a center can easily be obtained. 
	tmpJNTs = first(center = centerLocator, fromCenter = findYourCenter, step = limitHiRexJoints)
	bindJNTs = []
	num = len(tmpJNTs)
	rnTempJnts = []
	
	#rebuild list for naming
	for each in tmpJNTs:
		tEmPbLaH = cmds.listRelatives(each, p=True)
		if (findYourCenter == True):
			cmds.rename(tEmPbLaH, prefix + '_aimJNT_' + str(len(tmpJNTs) - num))
		bindJNTs.append(cmds.rename(each, prefix + '_bnJNT_' + str(len(tmpJNTs) - num)))
		num = num - 1
	
	jntParent = cmds.listRelatives(bindJNTs, p=True)
	
	#attach to locs or attach to nulls? 
	#provide second loc for up vector
	locators = second(upVector = upVecForCenter, fromCenter = findYourCenter, objects = bindJNTs)
	pinnedLocs = []
	num = len(locators)
	
	for each in locators:
		pinnedLocs.append(cmds.rename(each, prefix + '_loc_' + str(len(locators) - num)))
		num = num - 1
	#sel = cmds.ls(sl=True)
	#cmds.select(objects)
	third(curveObj, pinnedLocs)
	
	#clean up, vars for groups would be nice
	if (findYourCenter == False):
		for i in range(len(bindJNTs)):
			cmds.parent(bindJNTs[i], pinnedLocs[i])
		hierarchyGrp.append(cmds.group(pinnedLocs, n=prefix + 'locator_grp'))
		
	else:
		#parent under center locator?
		hierarchyGrp.append(cmds.group(jntParent, n=prefix + 'joint_grp'))
		hierarchyGrp.append(cmds.group(pinnedLocs, n=prefix +'locator_grp'))
		print('parent not needed')
	
	#create a lowRez Curve for controllers
	tempCrv = cmds.rebuildCurve(curveObj, ch=1, rpo=0,rt=0,end=1, kr=0,kcp=0,kep=1,kt=0,s=2,d=3,tol=0.01)
	cmds.delete(tempCrv, ch=True)
	lowRezCurve = cmds.rename(tempCrv[0],prefix + "curve_loRez_crv")
	lowRezCurveGrp = cmds.group(lowRezCurve, n=lowRezCurve+'_grp')
	cmds.wire( curveObj , w = lowRezCurve, gw= False, en=1.000000, ce=0.000000, li=0.000000, dds=[(0, 100)], n=prefix + 'lowRez_wire')
	
	#get the low resolution curves cvs
	cmds.select(lowRezCurve + '.cv[0:4]')
	ctrlTmpJoints = first()
	num = len(ctrlTmpJoints)
	ctrlJNTs = []
	
	#rename control joints
	for each in ctrlTmpJoints:
		ctrlJNTs.append(cmds.rename(each, prefix + '_ctrlJNT_' + str(len(ctrlTmpJoints) - num)))
		num = num - 1
	
	#skin Control joints to lowRezCurve 
	ctrlJNTgrp = groupSpecial(ctrlJNTs)
	hierarchyGrp.append(cmds.group(ctrlJNTgrp, n=prefix +'_ctrlJNTs_grp'))
	cmds.skinCluster(ctrlJNTs, lowRezCurve, dr=4.0, nw=1, mi=1, n = prefix + 'skinClstr')
	
	#create Controls for CtrlJnts with offset
	ctrls = faceCtrlCreate(prefix = prefix, objects = ctrlJNTgrp, controlSize = controlScale)
	ctrlNulls = groupSpecial(ctrls)
	hierarchyGrp.append(cmds.group(ctrlNulls, n=prefix+'_ctrl_grp'))
	#color variable
	colorNum = 14
	
	#lock and hide controls, parent to ctrl jnts
	for i in range(len(ctrls)):
		cmds.setAttr(ctrls[i]+'.sx', l=True, k=False, cb=False)
		cmds.setAttr(ctrls[i]+'.sy', l=True, k=False, cb=False)
		cmds.setAttr(ctrls[i]+'.sz', l=True, k=False, cb=False)
		cmds.setAttr(ctrls[i]+'.v', l=True, k=False, cb=False)
		cmds.parentConstraint(ctrls[i], ctrlJNTgrp[i])
		cmds.setAttr(ctrls[i]+".overrideEnabled",1)
		cmds.setAttr(ctrls[i]+".overrideColor",colorNum)
	
	
	#group everything to where it will need to be grouped (for scaling and organization)
	if (findYourCenter == False):
		scaleGrp = cmds.group(hierarchyGrp[1], hierarchyGrp[2], n=prefix+'_scale_grp')
		nonDeformableGrp = cmds.group(hiRezCurveGrp, lowRezCurveGrp, hierarchyGrp[0], n = prefix + '_nonDeform_grp')
		for each in bindJNTs:
			cmds.scaleConstraint(scaleGrp, each)
	else:
		cmds.parent(hierarchyGrp[0], hierarchyGrp[2], hierarchyGrp[3], upVecForCenter, centerLocator)
		nonDeformableGrp = cmds.group(hiRezCurveGrp, lowRezCurveGrp, hierarchyGrp[1], n = prefix + '_nonDeform_grp')
		centerPivotScaleGrp = cmds.group(centerLocator, n = prefix + '_scale_grp')
		
	
	if (createSliderJoints == True):
		sliderJoints = attachToNurbsSurface(prefix, nurbSurface, bindJNTs)
		sliderJointsGrp = cmds.group(sliderJoints, n='prefix_sliderJNT_grp')
		cmds.parent(sliderJointsGrp, nonDeformableGrp )
	
	if (createSliderJoints == True and findYourCenter == True):
		for each in sliderJoints: 
			cmds.scaleConstraint(centerLocator, each)
			
	elif(createSliderJoints == True and findYourCenter == False):
		for each in sliderJoints: 
			cmds.scaleConstraint(scaleGrp, each)		
	#voila it is done