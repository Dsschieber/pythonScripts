
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

'''

UI will be implemented later
prefix will also come later

instructions: select an edge and make some nice face controls

possible create a nurbs surface for sliding? 

'''


#edge is selected
edges = cmds.ls(sl=True)

#convert selection to vertices
vertices = cmds.polyListComponentConversion(edges, fe=True, tv=True)

#create a curve from edge
curves = curveFromVertPositions(edges)
curveObj = cmds.rename( curves, "curve_hiRez_crv")
cmds.select(vertices)
cmds.delete(curveObj, ch=True)

#limit the amount of joints for hiRez topo
limitHiRexJoints = 1
jointsObjects = []

#var determines if there will be a aim constraint based crv or a parent based. 
#center would best be used for eyes where a center can easily be obtained. 
findYourCenter = False
upVecForCenter = 'upVec'
centerLocator = 'obj_loc'
jointsObjects = first(center = centerLocator, fromCenter = findYourCenter, step = limitHiRexJoints)
jntParent = cmds.listRelatives(jointsObjects, p=True)
#rebuildCurve -ch 1 -rpo 0 -rt 0 -end 1 -kr 0 -kcp 0 -kep 1 -kt 0 -s 3 -d 3 -tol 0.01 "curve_hiRez_crv";

#attach to locs or attach to nulls? 
#provide second loc for up vector
locators = second(upVector = upVecForCenter, fromCenter = findYourCenter, objects = jointsObjects)
#sel = cmds.ls(sl=True)
#cmds.select(objects)
third(curveObj, locators)

#clean up, vars for groups would be nice
if (findYourCenter == False):
	for i in range(len(jointsObjects)):
		cmds.parent(jointsObjects[i], locators[i])
	cmds.group(locators, n='locator_grp')
	
else:
	#parent under center locator?
	cmds.group(jntParent, n='joint_grp')
	cmds.group(locators, n='locator_grp')
	print('parent not needed')

#create a lowRez Curve for controllers
tempCrv = cmds.rebuildCurve(curveObj, ch=1, rpo=0,rt=0,end=1, kr=0,kcp=0,kep=1,kt=0,s=2,d=3,tol=0.01)
cmds.delete(tempCrv, ch=True)
lowRezCurve = cmds.rename(tempCrv[0],"curve_loRez_crv")
cmds.wire( curveObj , w = lowRezCurve, gw= False, en=1.000000, ce=0.000000, li=0.000000, dds=[(0, 100)], n='lowRez_wire')

#get the low resolution curves cvs
cmds.select(lowRezCurve + '.cv[0:4]')
ctrlJoint = first()

#skin Control joints to lowRezCurve 

#create Controls for CtrlJnts with offset

#grp ctrls with an offset

#parent ctrl joints

#group everything to where it will need to be grouped (for scaling and organization)

#voila it is done