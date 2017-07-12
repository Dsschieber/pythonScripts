
#FIRST

from maya import cmds, OpenMaya
import maya.mel as mel
#for each vertex it will create a joint 


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
'''
def first(center = '', fromCenter = False):
	vtx = cmds.ls(sl = 1, fl = 1)
	jnt = []
	n = 0 
	for v in vtx:
		cmds.select(cl =1) 
		jnt.append( cmds.joint())
		pos = cmds.xform(v , q =1, ws =1, t =1)
		cmds.xform(jnt[n], ws =1, t =pos)
		if fromCenter == True:
			posC = cmds.xform(center, q =1, ws =1, t =1)
			cmds.select(cl =1)
			jntC = cmds.joint()
			cmds.xform(jntC, ws =1, t =posC)
			cmds.parent(jnt, jntC)
			cmds.joint (jntC, e =1, oj = "xyz", secondaryAxisOrient= "yup", ch =1, zso =1)
		n = n + 1
	return jnt
	        
      
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

def third(crv = '', positionObjects = []):
    sel = positionObjects
    print(sel)
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


edges = cmds.ls(sl=True)
vertices = cmds.polyListComponentConversion(edges, fe=True, tv=True)
curves = curveFromVertPositions(edges)
curveObj = cmds.rename( curves, "tempEdge")
cmds.select(vertices)
jointsObjects = []
jointsObjects = first()
#attach to locs or attach to nulls? 
locators = second(upVector = '', fromCenter = False, objects = jointsObjects)
#sel = cmds.ls(sl=True)
#cmds.select(objects)
third(curveObj, locators)
for i in range(len(jointsObjects)):
	cmds.parent(jointsObjects[i], locators[i])
groupObjects = groupSpecial(locators)