import pymel.core as pm
from maya import cmds, mel, OpenMaya
import logging
from math import sqrt, pow, pi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


side = ""
controlSuffix = "ctrl"
sdkNodeSuffix = "SDK"
constraintNodeSuffix = "CON"
positionNodeSuffix = "POS"
driverNodeSuffix = "DRIVER"


def alignSelectedNode():
	sel = cmds.ls(sl=1)
	nodeToAlign = sel[0]
	sel.pop(0)
	
	alignNodes(nodeToAlign, sel)
	
def alignNodes(nodeToAlign, listOfNodes):
	"""based on the selection, it will align the first selected nolde to the center of the rest of the
	selected nodes. Most of the time you will have 2 odes selected in which case
	the first and the second node will be aligned completely"""
	cmds.select(listOfNodes, r=1)
	cmds.select(nodeToAlign, add=1)
	cmds.delete(cmds.parentConstraint(mo=0, st="none", sr="none"))


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
	cmds.xform(locatorPV, ws=1, rotation=((rot.x/pi*180.0),
									(rot.y/pi*180.0),
									(rot.z/pi*180.0)))


'''
----------------------------------------------------------------------------------------
ribbon spline section

'''

def getDistance(objA, objB):
	""" Get the distance from two points """
	gObjA = pm.xform(objA, q=True, t=True, ws=True)
	gObjB = pm.xform(objB, q=True, t=True, ws=True)
	
	return sqrt(pow(gObjA[0]-gObjB[0],2)+pow(gObjA[1]-gObjB[1],2)+pow(gObjA[2]-gObjB[2],2))

def createNurbSurf(numJoints, name):
	""" From two selected objects will create a nurbs curve with follicle """
	
	front, end = pm.selected()
	distance = getDistance(front, end)
	nurbsSurf = pm.nurbsPlane(p = [0,0,0], ax =[0,1,0], w=1, lr=distance, d=3,u=1, v=numJoints, ch=1, n = name + '_Sur')
	
	vCoord = 1.0/numJoints
	follicleList = []
	
	# this section can also use CMuscleSurfAttach, 
	# found that muscle surface attach is less efficient
	for i in range(numJoints):
		fol = pm.createNode('transform', n= name + '_fol#', ss=True)
		folShape = pm.createNode('follicle', n=fol.name() + 'Shape', p=fol, ss=True)
		nurbsSurf[0].local >> folShape.inputSurface
		nurbsSurf[0].worldMatrix[0] >> folShape.inputWorldMatrix
		folShape.outRotate >> fol.rotate
		folShape.outTranslate >> fol.translate
		fol.inheritsTransform.set(False)
		folShape.parameterU.set(0.5)
		folShape.simulationMethod.set(0)
		
		curV = vCoord * (i + 1)
		nextV = vCoord * (i)
		midV = (curV + nextV) * 0.5
		logger.debug('The average of ' + str(curV) + ' and ' + str(nextV) + ' is ' + str(midV) + '. Setting follicle position to sum.')
		folShape.parameterV.set(midV)
		follicleList.append(fol)
	pm.group(follicleList, n = name + '_fol_GRP')
	return follicleList, nurbsSurf, front, end

def nurbsSurfaceOffset(first, second, nurbsSurf):
	"""takes selection and parentConstraints"""
	objPoint = pm.pointConstraint(first, second, nurbsSurf[0], mo=False, w=1)
	#aimConstraint -offset 0 0 0 -weight 1 -aimVector 0 0 1 -upVector 0 1 0 -worldUpType "scene";
	objAim = pm.aimConstraint(first, nurbsSurf[0], offset = [0,0,0], w=1, aimVector = [0,0,1], upVector = [0,1,0], worldUpType = "scene")
	pm.delete(objPoint, objAim)
	
def createSurfaceJoints(listPos, name):
	""" creates nurbs surface joints at follicle locations and orients joints """
	bindJoints = []
	for each in listPos:
		translation = each.getTranslation(w=True)
		joint = pm.joint(p = [translation[[0]],translation[[1]] ,translation[[2]]], n = name + '_J#')
		bindJoints.append(joint)
	for cJoint in bindJoints:
		pm.joint( cJoint, e=1, zeroScaleOrient=1, secondaryAxisOrient='yup', orientJoint='xyz')
		if max(bindJoints) == cJoint:
			pm.joint( cJoint, e=1, zeroScaleOrient=1, ch=1, orientJoint='none')
	for i in range(len(listPos)):
		bindJoints[i].setParent(w=True)
		pm.parentConstraint(listPos[i], bindJoints[i], mo=True)
	pm.group(bindJoints, n = name + '_bnJ_GRP')
	return bindJoints
	
def createControlJoints(front, mid, end, name, orientCtrl = False):
	""" creates control joints for ribbon spline """
	pm.select(cl=True)
	ctrlPos = [front, mid, end]
	ctrlJoint = []
	for each in ctrlPos:
		tempJoint = pm.joint(n = name + '_ctrlJ#' )
		ctrlJoint.append(tempJoint)
	for i in range(len(ctrlJoint)):
		parentC = pm.pointConstraint(ctrlPos[i], ctrlJoint[i], mo=False)
		pm.delete(parentC)
	if orientCtrl:
		for cJoint in ctrlJoint:
			pm.joint( cJoint, e=1, zeroScaleOrient=1, secondaryAxisOrient='yup', orientJoint='xyz')
			if cJoint == ctrlJoint[len(ctrlJoint) - 1]:
				pm.joint( cJoint, e=1, zeroScaleOrient=1, ch=1, orientJoint='none')
	for i in range(len(ctrlJoint)):
		ctrlJoint[i].setParent(w=True)
		ctrlJoint[i].radius.set(3)
	return ctrlJoint


def createRibbonSpline(side, base, numJoints = 5):
	""" creates a ribbon spline with control joints """
	conName = nameNode(base, side)
	follicleList, nurbsSurf, front, end = createNurbSurf(numJoints, conName)
	nurbsSurfaceOffset(front, end, nurbsSurf)
	bindJoints = createSurfaceJoints(follicleList, conName)
	mid = 0
	centerPos = []
	ctrlJoints = []
	if len(bindJoints) % 2 == 0:
	    centerPos = midLocPos(front, end)
	    ctrlJoints = createControlJoints(front, centerPos, end, conName, orientCtrl = True)
	    pm.delete(centerPos)
	else:
		total = len(bindJoints)
		sum = 0
		for i in range(len(bindJoints)):
			sum = (i + 1) + sum
		mid = sum / total - 1
		ctrlJoints = createControlJoints(front, bindJoints[mid], end, conName, orientCtrl = True)
	pm.skinCluster( ctrlJoints, nurbsSurf[0], bm=0, dr=2, mi=2)

def midLocPos(front, end):
	""" if their is no center joint a temporary locator is used for mid ctrl position """
	loc = pm.spaceLocator()
	logger.debug('Locator ' + loc + ' made.')
	tempP = pm.pointConstraint(front, end, loc, mo=False)
	pm.delete(tempP)
	return loc


def quickSpineCtrl(side, base):
	""" from control joint selection creates controls for spine, 
	this function will build a quick spine control network """
	ctrlJoints = pm.selected()
	conName = nameNode(base, side)
	print(ctrlJoints)
	ctrlBase = createControl(side, base + "Tip", "circleX", sdk=1, con=1)
	ctrlMid = createControl(side, base + "Mid", "circleX", sdk=1, con=1)
	ctrlEnd = createControl(side, base + "End", "circleX", sdk=1, con=1)

	print(ctrlBase, ctrlMid, ctrlEnd)
	locs = []
	tangentLocs = []

	for i in range(len(ctrlJoints)):
		if i == 0:
			tParent = pm.parentConstraint( ctrlJoints[i], ctrlBase[0], mo =False)
			tangentLocs.append(pm.spaceLocator(n = conName + "base_tangent"))
			locs.append(pm.spaceLocator(n= conName + "base_upVec"))
		elif i == 1:
			tParent = pm.parentConstraint( ctrlJoints[i], ctrlMid[0] , mo =False)
			locs.append(pm.spaceLocator(n= conName + "mid_upVec"))
		else:
			tParent = pm.parentConstraint( ctrlJoints[i], ctrlEnd[0] , mo =False)
			tangentLocs.append(pm.spaceLocator(n = conName + "end_tangent"))
			tanEndParent = pm.parentConstraint(ctrlEnd[0], ctrlMid[0], tangentLocs[1], mo = False)
			tanBaseParent = pm.parentConstraint(ctrlBase[0], ctrlMid[0], tangentLocs[0], mo = False)
			locs.append(pm.spaceLocator(n= conName + "end_upVec"))
			pm.delete(tanEndParent, tanBaseParent)
			pm.parent(tangentLocs[1], ctrlEnd[3] )
			pm.parent(tangentLocs[0], ctrlBase[3] )
		pm.delete(tParent)


	for i in range(len(ctrlJoints)):
		lParent = pm.parentConstraint(ctrlJoints[i], locs[i], mo=False)
		pm.delete(lParent)
		pm.parent(locs[i], ctrlJoints[i])
		locs[i].translateY.set(15.0)
		if i == 0:
			pm.parent(ctrlJoints[i], ctrlBase[3])
		elif i == 1:
			pm.parent(ctrlJoints[i], ctrlMid[3])
			pm.parent(locs[i], w=True)
		else:
			pm.parent(ctrlJoints[i], ctrlEnd[3])

	pm.pointConstraint(locs[0], locs[2], locs[1], mo=True)
	pm.pointConstraint(tangentLocs[0], tangentLocs[1], ctrlMid[1], mo=True)
	#aimConstraint -mo -weight 1 -aimVector 1 0 0 -upVector 0 1 0 -worldUpType "object" -worldUpObject testmid_upVec;
	pm.aimConstraint(tangentLocs[0], ctrlMid[1], weight=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType="object", worldUpObject=locs[1], mo=True)




def createCoordinatesSwitch(driversList=[], attrsList=[], drivenNode="", spaceNode="", side="left", constraintType="parent"):
	"""
	Arguments:
	
	driversList: list of driver nodes
	attrsList : list of nice names for the enum attribute
	driven node: the name of the node that wil receive the attribute for the switch
	spaceNode: the node that will receive the constraint itself. MOst f the time is "_CON" node and
				it ususally is a parent of the "drivenNode"
	"""
	worldCon = checkForWorldControl()
		
	#check if we have more than 1 objects with the same same
	drivenNodes = cmds.ls(drivenNode)
	if len(drivenNodes) == 1:
		#create a group node to store the created nodes
		grpNode = cmds.createNode("transform", n=drivenNode+"_SpaceSwitching_GRP")
		#create switching attribute
		cmds.addAttr(drivenNode, longName="parent", at="enum", en=":".join(attrsList))
		cmds.setAttr(drivenNode+".parent", k=1)
		
		driverConNodes = []
		for driver in driversList:
			#create 1 node per space that is aligned to the drivenNode, but parent Constrained to the driver space
			spaceControlNodes = createControl(side, drivenNode+"_"+driver, "null" , sdk=0, con=1)
			control = spaceControlNodes[-1]
			sCON = spaceControlNodes[1]
			sPOS = spaceControlNodes[0]
			cmds.delete(control)
			alignNodes(sPOS, [spaceNode])
			cmds.parent(sPOS, grpNode)
			
			cmds.parentConstraint(driver, sCON, mo=1, st="none", sr="none")
			
			driverConNodes.append(sCON)
		
		mainConstraint = ""
		if constraintType == "parent":
			mainConstraint = cmds.parentConstraint(driverConNodes, spaceNode, mo=0, st="none", sr="none")[0]
		if constraintType == "orient":
			mainConstraint = cmds.orientConstraint(driverConNodes, spaceNode, mo=0, skip="none")[0]
		
		c=0
		
		for driver in driverConNodes:
			i=0
			for dr in driversList:
				if c==i:
					cmds.setDrivenKeyframe(mainConstraint, at=driver+"W"+str(i), currentDriver=drivenNode+".parent", driverValue=i, value=1)
				else:
					cmds.setDrivenKeyframe(mainConstraint, at=driver+"W"+str(c), currentDriver=drivenNode+".parent", driverValue=i, value=0)
				i=i+1
			c=c+1
			






			
	
def placeJointInPipe():
	#get selection
	selectedCluster = cmds.cluster(rel=1)
	currentPivotPosition = cmds.xform(selectedCluster, q=1, os=1, rp=1)
	#create joint
	newJoint = cmds.createNode("joint", n="pipeJoint1")
	
	#align joint
	cmds.xform(newJoint, ws=1, t=(currentPivotPosition[0], currentPivotPosition[1], currentPivotPosition[2]))
	cmds.delete(selectedCluster)
	#end message
	print "Done"
	

def connectSelectedJoints(suffixes = ["_IK", "_FK"], multDivNode = "L_backLegIKSwitch_MD", revNode = "L_backLegIKSwitch_REV"):
	"""Use this to connect the FK IK chains"""
	con = None
	selectedJoints = cmds.ls(sl=1, type="joint")
	if len(selectedJoints) > 1:
		print selectedJoints
		if checkJoints(selectedJoints, suffixes[0]) and checkJoints(selectedJoints, suffixes[1]):
			for j in selectedJoints:
				con = cmds.parentConstraint(j+suffixes[0], j+suffixes[1], j, mo=1, st="none", sr="none")[0]
				cmds.connectAttr(multDivNode+".outputX", con+"."+j+suffixes[0]+"W0", f=1)
				cmds.connectAttr(revNode+".outputX", con+"."+j+suffixes[1]+"W1", f=1)
				cmds.connectAttr(multDivNode+".outputX", j+suffixes[0]+".v", f=1)
				cmds.connectAttr(revNode+".outputX", j+suffixes[1]+".v", f=1)
		else:
			print "There is either a duplicate or no corresponding joint"
	else:
		cmds.confirmDialog( title='Select joints', message='Please select your joints', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )

		
		
def checkJoints(jointsList, suffix="_IK"):
	"""Makes sure for each joint in the selected joints there is 1
	and only 1 corresponding joint with the given suffix"""
	for j in jointsList:
		drivenJntsList = cmds.ls(j+suffix)
		if len(drivenJntsList) > 1:
			print "There is more than 1 "+ j+suffix
			return 0
		if len(drivenJntsList) == 0:
			print "There is no "+ j+suffix
			return 0
		
	return 1








	
def createControl(side, base, shape, sdk=0, con=0):
	"""adds a control to the given joint"""
	cmds.select(clear=1)
	conName = ""
	sdkNode = ""
	conNode = ""
	posNode = ""
	
	#create name
	conName = nameNode(base, side)
	
	#create control
	mel.eval('source "wireShape.mel"; wireShape("'+shape+'");')
	cmds.rename(cmds.ls(sl=1)[0], conName+"_"+controlSuffix)
	ctrl = cmds.ls(sl=1)[0]
	if shape != "null" or shape!="joint" or shape!="locator":
		mel.eval("SelectCurveCVsAll")
		cmds.scale(50, 50, 50)
	#ctrl = cmds.createNode("transform", n=conName+"_"+controlSuffix)
	
	#check if I need to create sdk or con
	if sdk:
		sdkNode = cmds.createNode("transform", n=conName+"_"+sdkNodeSuffix)
		cmds.parent(ctrl, sdkNode)
	else:
		print "Skipping SDK"
	
	if con:
		conNode = cmds.createNode("transform", n=conName+"_"+constraintNodeSuffix)
		if sdk:
			cmds.parent(sdkNode, conNode)
		else:
			cmds.parent(ctrl, conNode)
	else:
		print "Skipping Constraint node"
		
	posNode = cmds.createNode("transform", n=conName+"_"+positionNodeSuffix)
	if con:
		cmds.parent(conNode, posNode)
	elif sdk:
		cmds.parent(sdkNode, posNode)
	else:
		cmds.parent(ctrl, posNode)
	
	
	nodesList = [posNode, conNode, sdkNode, ctrl]
	
	return nodesList








	
def rigSelectedJoints(side, base, shape="cube", sdk=0, con=0):
	sel = cmds.ls(sl=1)
	if len(sel) == 1:
		rigFKJoint(sel[0], side, base, shape, sdk,  con)
	elif len(sel)>1:
		i = 1
		for s in sel:
			rigFKJoint(s, side, base+str(i), shape, sdk,  con)
			i+=1
		
def rigFKJoint(joint, side, base, shape, sdk=0, con=0):
	controlNodes = createControl(side, base, shape, sdk, con)
	alignNodes(controlNodes[0], [joint])
	cmds.parentConstraint(controlNodes[-1], joint)
	
	return controlNodes
	
	
	
	
	
	
	
	
def nameNode(baseName, side, suffix=""):
	side = side.lower()
	sideShort = ""
	if side == "left":
		sideShort = "L_"
	elif side == "right":
		sideShort = "R_"
	elif side == "":
		sideShort = ""
	else:
		raise("please type either 'left' or 'right as the side string'")
	
	if suffix != "":
		suffix = "_"+suffix
		
	controlName = sideShort+baseName+suffix
	return controlName
	
	
	
	
	
	
	
def positionPoleVectorControl(startJoint, endJoint, poleVectorNode, distance):
	"""NOTE: If each joint in your chain has more than 1 joint, make sure the joint that will be part of the IK chain, 
	are the first children, otherwise you will get bad results."""
	#figure out all the joints between startJoint and endJoint
	
	jointChainList = []
	jointChainList.append(startJoint)
	j = 0
	currentJoint = startJoint
	while j==0:
		currentJointChildren = cmds.listRelatives(currentJoint, c=1, type="joint")
		if len(currentJointChildren) > 1:
			cmds.warning("whoo, the specified start joint has more than 1 children, please choose another start joint")
		
			
		nextJoint = currentJointChildren[0]
		if nextJoint == endJoint:
			j=1
		else:
			jointChainList.append(nextJoint)
		currentJoint = nextJoint
	
	jointChainList.append(endJoint)
	
	#get position in space of each joint so we can create the polygon
	coordinatesList = []
	for j in jointChainList:
		jCoord = cmds.xform(j, q=1, ws=1, rp=1)
		coord = tuple(jCoord)
		coordinatesList.append(coord)
	
	polyPlane = cmds.polyCreateFacet( p=coordinatesList )[0]
	alignNodes(poleVectorNode, jointChainList[1])
	
	cmds.delete(cmds.geometryConstraint(polyPlane, poleVectorNode))
	cmds.delete(cmds.normalConstraint(polyPlane, poleVectorNode, upVector=[1, 0, 0], aimVector=[0, 0, 1]))
	
	cmds.xform(poleVectorNode, objectSpace=1, relative=1, t=[distance, distance, 0])
	
	cmds.delete(polyPlane)






def checkForWorldControl():
	extraCon = checkForExtraControl()
	worldCon = "WORLD_CTRL"
	if not cmds.objExists("WORLD_CTRL"):
		worldCon = cmds.createNode("transform", n="WORLD_CTRL")
		cmds.parent(worldCon, extraCon)
	return worldCon

def checkForExtraControl():
	extrasConCon = "EXTRAS"
	if not cmds.objExists("EXTRAS"):
		extrasCon = cmds.createNode("transform", n="EXTRAS")
	
	return extrasConCon

def rigBackLeg(side, hip0, hip1, hip2, knee1, knee2, foot, footShellJnt, heel, heelTip, \
					frontToeIn1, frontToeIn2, frontToeIn3,\
					frontToe1, frontToe2, frontToe3,\
					frontToeBack1, frontToeBack2, frontToeBack3,\
					heelToe1, heelToe2):
					
	"""
	reload(mech);mech.rigBackLeg("right","R_hip1_J", "R_hip2_J", "R_hip3_J", "R_knee1_J", "R_shin_J", "R_foot_J", "R_footShell_J", "R_backAnkle_J","R_backAnkleTip_J",\
						"R_footInToe1_J", "R_footInToe2_J", "R_footInToe3_J","R_footMainToe1_J", "R_footMainToe2_J", "R_footMainToe3_J",\
						"R_footBackToe0_J", "R_footBackToe1_J", "R_footBackToe2_J", "R_backAnkleFoot_J", "R_backAnkleToe_J")
	"""
	
	extraCon = checkForExtraControl()
	suffixes = ["_IK", "_FK"]
	if side == "right":
		shortSide = "rt"
	elif side == "left":
		shortSide = "lf"
	#duplicate the leg chain to create the IK chain and FK chain
	for suf in suffixes:
		ikChainBuffer = cmds.duplicate(hip0, renameChildren=1)
		chain = []
		for ch in ikChainBuffer:
			if cmds.nodeType(ch) == "joint":
				newName = ch.replace("_J1", "_J"+suf)
				newName = cmds.rename(ch, newName)
				chain.append(newName)
		cmds.parent(chain[1], extraCon)
		cmds.delete(chain[0])
	
					
	
	#create the leg control that will have the switch attribute
	legControlNodes = createControl(side, "backLeg", "cube", sdk=0, con=0)
	legControl = legControlNodes[-1]
	legPOS = legControlNodes[0]
	
	cmds.addAttr(legControl, shortName="IK", attributeType="double", minValue=0, maxValue=10, defaultValue=10)
	cmds.setAttr(legControl+".IK", k=1)
	
	#create the multiplyDivide and the reverse node and connect it to the leg control
	mdNode = cmds.createNode("multiplyDivide", n=nameNode("backLeg", side, "MD"))
	rvNode = cmds.createNode("reverse", n=nameNode("backLeg", side, "REV"))
	cmds.setAttr(mdNode+".input2X", 0.1)
	cmds.connectAttr(legControl+".IK", mdNode+".input1X", f=1)
	
	cmds.connectAttr(mdNode+".outputX", rvNode+".inputX", f=1)
	
	
		
	
	
	#connect the hierarchies
	cmds.select(hip1, hi=1)
	connectSelectedJoints(suffixes = ["_IK", "_FK"], multDivNode = mdNode, revNode = rvNode)
	rigBackLegIK(side, hip1+"_IK", hip2+"_IK", knee1+"_IK", knee2+"_IK", foot+"_IK", footShellJnt+"_IK", heel+"_IK", heelTip+"_IK", \
					frontToeIn1+"_IK", frontToeIn2+"_IK", frontToeIn3+"_IK",\
					frontToe1+"_IK", frontToe2+"_IK", frontToe3+"_IK",\
					frontToeBack1+"_IK", frontToeBack2+"_IK", frontToeBack3+"_IK",\
					heelToe1+"_IK", heelToe2+"_IK")
	
	rigBackLegFK(side, [hip1+"_FK", hip2+"_FK", knee1+"_FK", knee2+"_FK", foot+"_FK", \
					footShellJnt+"_FK",heel+"_FK", heelTip+"_FK", \
					frontToeIn1+"_FK", frontToeIn2+"_FK", frontToeIn3+"_FK",\
					frontToe1+"_FK",frontToe2+"_FK", frontToe3+"_FK",\
					frontToeBack1+"_FK",frontToeBack2+"_FK", frontToeBack3+"_FK",\
					heelToe1+"_FK", heelToe2+"_FK"])
	
	
	#visibility Switch for controls based on what we have selected IK or FK
	
	#IK visibility
	ikNodes = ["mch_"+shortSide+"_foot_ik_POS", "mch_"+shortSide+"_hip_ik_POS", "mch_"+shortSide+"_legPV_POS", "mch_"+shortSide+"_helperJoint1_J"]
	fkNodes = ["mch_"+shortSide+"_hip2_fk_ctrl"]
	for n in ikNodes:
		cmds.connectAttr(mdNode+".outputX", n+".v", f=1)
		
	#create the first hip control
	hip0ControlNodes = createControl(side, "hip0", "circleY", sdk=1, con=1)
	hip0Control = hip0ControlNodes[-1]
	hip0SDK = hip0ControlNodes[2]
	hip0CON = hip0ControlNodes[1]
	hip0POS = hip0ControlNodes[0]
	
	alignNodes(hip0POS, [hip0])
	cmds.parentConstraint(hip0Control, hip0, mo=0, st="none", sr="none")
	
	cmds.parent(fkNodes[0], hip0Control)
	cmds.parent(ikNodes[1], hip0Control)
	cmds.parent(ikNodes[3], hip0Control)
	#rig the IK control so it always aims at a node in order to always follow the IK leg
	
	print "Done"
	
def rigBackLegIK(side, hip1, hip2, knee1, knee2, foot, footShellJnt, heel, heelTip, \
					frontToeIn1, frontToeIn2, frontToeIn3,\
					frontToe1, frontToe2, frontToe3,\
					frontToeBack1, frontToeBack2, frontToeBack3,\
					heelToe1, heelToe2):
	"""
	mech.rigBackLegIK("right", "R_hip2_J", "R_hip3_J", "R_knee1", "R_shin", "R_foot", "R_footShell_J", "R_backAnkle","R_backAnkleTip",
						"R_footInToe1", "R_footInToe2", "R_footInToe3","R_footMainToe1", "R_footMainToe2", "R_footMainToe3",\
						"R_footBackToe1", "R_footBackToe2", "R_footBackToe3", "R_backAnkleFoot", "R_backAnkleToe")
	"""
	extraCon = checkForExtraControl()
	worldCon = checkForWorldControl()
		
	#create foot control
	footControlNodes = createControl(side, "foot_ik", "circleY", sdk=1, con=1)
	footControl = footControlNodes[-1]
	footSDK = footControlNodes[2]
	footCON = footControlNodes[1]
	footPOS = footControlNodes[0]
	
	alignNodes(footPOS, [foot])
	cmds.setAttr(footPOS+".rx", 0)
	cmds.setAttr(footPOS+".ry", 0)
	cmds.setAttr(footPOS+".rz", 0)
	
	#create the hip control
	hipControlNodes = createControl(side, "hip_ik", "cross", sdk=1, con=1)
	hipControl = hipControlNodes[-1]
	hipSDK = hipControlNodes[2]
	hipCON = hipControlNodes[1]
	hipPOS = hipControlNodes[0]
	
	alignNodes(hipPOS, [hip1])
	cmds.setAttr(hipPOS+".rx", 0)
	cmds.setAttr(hipPOS+".ry", 0)
	cmds.setAttr(hipPOS+".rz", 0)
	
	cmds.pointConstraint(hipControl, hip1)
		
	#create heel roll control and parent it to the foot control
	heelRollNodes = createControl(side, "heelRoll", "null", sdk=1, con=0)
	heelRollControl = heelRollNodes[-1]
	heelRollSDK = heelRollNodes[2]
	heelRollPOS = heelRollNodes[0]
	
	alignNodes(heelRollPOS, [heelTip])
	cmds.parent(heelRollPOS, footControl)
	
	#create foot roll control and parent it under the heel roll control
	footRollNodes = createControl(side, "footRoll", "null",sdk=1, con=0)
	footRollControl = footRollNodes[-1]
	footRollSDK = footRollNodes[2]
	footRollPOS = footRollNodes[0]
	
	
	alignNodes(footRollPOS, [footControl])
	cmds.parent(footRollPOS, heelRollControl)

	#Create ikHandleHelper node align it to knee2 and parent it under foot roll control
	legIKHelperNodes = createControl(side, "legIKHelper", "null" ,sdk=1, con=1)
	legIKHelperControl = legIKHelperNodes[-1]
	legIKHelperSDK = legIKHelperNodes[2]
	legIKHelperCON = legIKHelperNodes[1]
	legIKHelperPOS = legIKHelperNodes[0]
	
	alignNodes(legIKHelperPOS, [knee2])
	cmds.parent(legIKHelperPOS, footRollControl)

	#create pushOnOff_SDK and pushOnOff_POS groups
	#align push nodes to the knee2 and parent pushOnOff_POS under ikHandleHelper
	pushOnOffNodes = createControl(side, "pushOnOff","null", sdk=1, con=1)
	pushOnOffControl = pushOnOffNodes[-1]
	pushOnOffSDK = pushOnOffNodes[2]
	pushOnOffCON = pushOnOffNodes[1]
	pushOnOffPOS = pushOnOffNodes[0]
	
	alignNodes(pushOnOffPOS, [knee2])
	cmds.parent(pushOnOffPOS, legIKHelperControl)

	#add footAttributes
	attributesToAdd = {"footRoll":[-10, 10], \
						"sideRoll": [-10, 10],\
						"legPress":[0, 10],\
						"footPress":[0, 10],\
						"legTwist":None,\
						"thighTwist": None,\
						"footRigidity":[0, 10],\
						"footShellShinSpace":[0, 10]}
	
	for attr in attributesToAdd:
		if attributesToAdd[attr] is not None:
			minValue = attributesToAdd[attr][0]
			maxValue = attributesToAdd[attr][1]
			cmds.addAttr(footControl, shortName=attr, attributeType="double", minValue=minValue, maxValue=maxValue, defaultValue=0)
			cmds.setAttr(footControl+"."+attr, k=1)
		else:
			cmds.addAttr(footControl, shortName=attr, attributeType="double", defaultValue=0)
			cmds.setAttr(footControl+"."+attr, k=1)
			
	cmds.addAttr(footControl, shortName="lasersVis", attributeType="bool", defaultValue=1)
	cmds.setAttr(footControl+".lasersVis", k=1, cb=1)
	

	
	
	#create pole vector control and laser
	thighIKPVNodes = createControl(side, "thighPV", "cross",sdk=1, con=1)
	thighIKPVControl = thighIKPVNodes[-1]
	thighIKPVSDK = thighIKPVNodes[2]
	thighIKPVCON = thighIKPVNodes[1]
	thighIKPVPOS = thighIKPVNodes[0]
	
	positionPoleVectorControl(hip1, knee1, thighIKPVPOS, 100)
	midIKJCoord = tuple(cmds.xform(hip2, q=1, ws=1, rp=1))
	
	thighIKLaser = cmds.annotate(thighIKPVControl, p=midIKJCoord)
	cmds.parent(thighIKLaser, hip2)
	
	#create thigh IK and parent it under pushOnOff control
	thighIKHandleNodes = cmds.ikHandle(solver="ikRPsolver", sj=hip1, ee=knee1, n=nameNode("thigh", "left", "IK"))
	thighIKHandle = thighIKHandleNodes[0]
	cmds.parent(thighIKHandle, pushOnOffControl)
	cmds.parent(thighIKPVPOS, heelRollControl)
	

	#connect the pole vector control and laser
	cmds.poleVectorConstraint(thighIKPVControl, thighIKHandle)
	cmds.connectAttr(footControl+".lasersVis", thighIKLaser+".v")

	#--------create the leg ik
	#create the helper joints joint1 at the hip, joint 2 between knee1 and knee1 and joint 2 at the foot
	helperIKJnt1 = cmds.createNode("joint", n=nameNode("helperJoint1", side, "J"))
	helperIKJnt2 = cmds.createNode("joint", n=nameNode("helperJoint2", side, "J"))
	helperIKJnt3 = cmds.createNode("joint", n=nameNode("helperJoint3", side, "J"))
	
	cmds.delete(cmds.parentConstraint(hip2, helperIKJnt1, mo=0, st="none", sr="none"))
	cmds.delete(cmds.parentConstraint(knee1, knee2, helperIKJnt2, mo=0, st="none", sr="none"))
	cmds.delete(cmds.parentConstraint(foot, helperIKJnt3, mo=0, st="none", sr="none"))
	
	cmds.parent(helperIKJnt3, helperIKJnt2)
	cmds.parent(helperIKJnt2, helperIKJnt1)
	cmds.parent(helperIKJnt1, extraCon)
	
	cmds.makeIdentity(helperIKJnt1, a=1, t=1, r=1, jo=1)
	cmds.makeIdentity(helperIKJnt2, a=1, t=1, r=1, jo=1)
	cmds.joint(helperIKJnt1, e=1, orientJoint="xzy", secondaryAxisOrient="zup")
	cmds.joint(helperIKJnt2, e=1, orientJoint="xyz", secondaryAxisOrient="yup")
	cmds.makeIdentity(helperIKJnt3, a=1, t=1, r=1, jo=1)
	
	#setup pole vector
	legIKPVNodes = createControl(side, "legPV", "cross",sdk=1, con=1)
	legIKPVControl = legIKPVNodes[-1]
	legIKPVSDK = legIKPVNodes[2]
	legIKPVCON = legIKPVNodes[1]
	legIKPVPOS = legIKPVNodes[0]
	
	positionPoleVectorControl(helperIKJnt1, helperIKJnt3, legIKPVPOS, 500)
	midIKJCoord = tuple(cmds.xform(helperIKJnt2, q=1, ws=1, rp=1))
	
	legIKLaser = cmds.annotate(legIKPVControl, p=midIKJCoord)
	cmds.parent(legIKLaser, helperIKJnt3)
	
	#create Leg IK and parent under footRoll control
	legIKHandleNodes = cmds.ikHandle(solver="ikRPsolver", sj=helperIKJnt1, ee=helperIKJnt3, n=nameNode("leg", "left", "IK"))
	legIKHandle = legIKHandleNodes[0]
	cmds.setAttr(legIKHandle+".v", 0, l=1)
	cmds.parent(legIKHandle, footRollControl)
	
	#connect pole vector
	cmds.poleVectorConstraint(legIKPVControl, legIKHandle)
	cmds.connectAttr(footControl+".lasersVis", legIKLaser+".v")
	
	#create a piston group node
	pistonNodes = createControl(side, "piston", "null",sdk=1, con=1)
	pistonFeetControl = pistonNodes[-1]
	pistonFeetSDK = pistonNodes[2]
	pistonFeetCON = pistonNodes[1]
	pistonFeetPOS = pistonNodes[0]
	
	alignNodes(pistonFeetPOS, knee2)
	cmds.delete(cmds.pointConstraint(foot, pistonFeetPOS, skip="none", mo=0))
	cmds.parent(pistonFeetPOS, heelRollControl)
	
	#create world up node for the shin aim constraint
	shinWorldUpNodes = createControl(side, "shinWorldUp", "null", sdk=0, con=0)
	shinWorldUpControl = shinWorldUpNodes[-1]
	shinWorldUpPOS = shinWorldUpNodes[0]
	alignNodes(shinWorldUpPOS, footControl)
	cmds.setAttr(shinWorldUpPOS+".tz", 100)
	cmds.parent(shinWorldUpPOS, heelRollControl)
	
	aimVec = [1, 0, 0]
	worldUpVec = [0, 1, 0]
	if side=="right":
		aimVec = [-1, 0, 0]
	cmds.aimConstraint(pistonFeetControl, knee2, aimVector=aimVec, upVector=worldUpVec, worldUpObject=shinWorldUpControl, worldUpType="object", mo=1)
	cmds.aimConstraint(pistonFeetControl, knee1, aimVector=aimVec, upVector=worldUpVec, worldUpObject=shinWorldUpControl, worldUpType="object", mo=1)
	cmds.parentConstraint(pistonFeetControl, foot, mo=1, st="none", sr="none")
	#-------- setup foot rigidity
	#duplicate the second joint in the leg IK helper chain and parent it under footRoll control kneeRigidNode
	kneeRigidNode = cmds.duplicate(helperIKJnt2, parentOnly=1)[0]
	cmds.parent(kneeRigidNode, footRollControl)
	
	ikHelperConNodes = createControl(side, "ikHelper", "sphere",sdk=1, con=1)
	ikHelperControl = ikHelperConNodes[-1]
	ikHelperSDK = ikHelperConNodes[2]
	ikHelperCON = ikHelperConNodes[1]
	ikHelperPOS = ikHelperConNodes[0]
	
	alignNodes(ikHelperPOS, helperIKJnt2)
	
	cmds.parent(ikHelperPOS, footRollControl)
	cmds.parent(pushOnOffPOS, ikHelperControl)
	
	#point constraint the ikHelper control to the kneeRigidNode and the second joint in the ikHelper chain
	footRigPointCon = cmds.pointConstraint(kneeRigidNode, helperIKJnt2, ikHelperCON, mo=1, skip="none")[0]
	
	#connect the footRigidity attribute to the point constraint
	footRigidMD = cmds.createNode("multiplyDivide", n=nameNode("footRigidity", side, "MD"))
	footRigidREV = cmds.createNode("reverse", n=nameNode("footRigidity", side, "REV"))
	
	cmds.connectAttr(footControl+".footRigidity", footRigidMD+".input1X", f=1)
	cmds.connectAttr(footRigidMD+".outputX", footRigidREV+".inputX", f=1)
	cmds.connectAttr(footRigidMD+".outputX", footRigPointCon+"."+kneeRigidNode+"W0")
	cmds.connectAttr(footRigidREV+".outputX", footRigPointCon+"."+helperIKJnt2+"W1")
	cmds.setAttr(footRigidMD+".input2X", 0.1)

	#connect all fot attributes: footRoll, thighTwist, LegTwist, sideRoll, legPress, footPress
	#footRoll
	cmds.setDrivenKeyframe(footRollSDK, at="rx", currentDriver=footControl+".footRoll", driverValue=0, value=0)
	cmds.setDrivenKeyframe(footRollSDK, at="rx", currentDriver=footControl+".footRoll", driverValue=10, value=30)
	cmds.setDrivenKeyframe(footRollSDK, at="rx", currentDriver=footControl+".footRoll", driverValue=-10, value=-15)
	
	#sideRoll
	cmds.setDrivenKeyframe(footRollSDK, at="rz", currentDriver=footControl+".sideRoll", driverValue=0, value=0)
	cmds.setDrivenKeyframe(footRollSDK, at="rz", currentDriver=footControl+".sideRoll", driverValue=10, value=30)
	cmds.setDrivenKeyframe(footRollSDK, at="rz", currentDriver=footControl+".sideRoll", driverValue=-10, value=-15)
	
	#thighTwist and leg Twist
	cmds.connectAttr(footControl+".thighTwist", thighIKHandle+".twist", f=1)
	cmds.connectAttr(footControl+".legTwist", legIKHandle+".twist", f=1)
	
	#--------press attributes
	pushDirection = 1
	if side=="right":
		pushDirection = -1
	cmds.setDrivenKeyframe(pushOnOffSDK, at="tx", currentDriver=footControl+".legPress", driverValue=0, value=0)
	cmds.setDrivenKeyframe(pushOnOffSDK, at="tx", currentDriver=footControl+".legPress", driverValue=10, value=30*pushDirection)
	#foot push
	cmds.setDrivenKeyframe(pistonFeetSDK, at="tx", currentDriver=footControl+".footPress", driverValue=0, value=0)
	cmds.setDrivenKeyframe(pistonFeetSDK, at="tx", currentDriver=footControl+".footPress", driverValue=10, value=30*pushDirection)
	
	
	
	

	#-------- foot shell
	#create footShell control set
	footShellNodes = createControl(side, "footShell","cube", sdk=1, con=1)
	footShellControl = footShellNodes[-1]
	footShellSDK = footShellNodes[2]
	footShellCON = footShellNodes[1]
	footShellPOS = footShellNodes[0]
	
	alignNodes(footShellPOS, [footShellJnt])
	cmds.parent(footShellPOS, footControl)
	cmds.parentConstraint(footShellControl, footShellJnt, mo=0, st="none", sr="none")

	#set driven key footControl.footRoll 0 -> footShellSDK 0, footControl.footRoll 10 -> footShellSDK -3.5
	cmds.setDrivenKeyframe(footShellSDK, at="rx", currentDriver=footControl+".footRoll", driverValue=0, value=0)
	cmds.setDrivenKeyframe(footShellSDK, at="rx", currentDriver=footControl+".footRoll", driverValue=10, value=-3.5)
	
	#blend shell between foot and shin
	parentCon = cmds.parentConstraint(knee2, foot, footShellCON, mo=1, st="none", sr="none")[0]
	cmds.setDrivenKeyframe(parentCon, at=knee2+"W0", currentDriver=footControl+".footShellShinSpace", driverValue=0, value=0)
	cmds.setDrivenKeyframe(parentCon, at=foot+"W1", currentDriver=footControl+".footShellShinSpace", driverValue=0, value=1)
	
	cmds.setDrivenKeyframe(parentCon, at=knee2+"W0", currentDriver=footControl+".footShellShinSpace", driverValue=10, value=1)
	cmds.setDrivenKeyframe(parentCon, at=foot+"W1", currentDriver=footControl+".footShellShinSpace", driverValue=10, value=0)
	
	#--------- back claw
	#create backClaw control set and parent it under heel Roll control
	backClawNodes = createControl(side, "ankleClaw","cube", sdk=1, con=1)
	backClawControl = backClawNodes[-1]
	backClawSDK = backClawNodes[2]
	backClawCON = backClawNodes[1]
	backClawPOS = backClawNodes[0]
	
	alignNodes(backClawPOS, [heel])
	cmds.parentConstraint(backClawControl, heel, mo=0, st="none", sr="none")

	#point contraint the back claw CON to the shin joint
	
	#blend between shin and world by creating 2 helper nodes to blend between
	ankleLocal = cmds.createNode("transform", n=backClawControl+"_Local")
	ankleWorld = cmds.createNode("transform", n=backClawControl+"_World")
	
	alignNodes(ankleLocal, [backClawControl])
	alignNodes(ankleWorld, [backClawControl])
	
	cmds.parent(ankleLocal, extraCon)
	cmds.parent(ankleWorld, extraCon)
	cmds.parent(backClawPOS, heelRollControl)
	
	cmds.parentConstraint(worldCon, ankleWorld, mo=1, st="none", sr="none")
	cmds.parentConstraint(knee2, ankleLocal, mo=1, st="none", sr="none")
	
	#local world blend of the back claw
	cmds.addAttr(backClawControl, shortName="worldSpace", attributeType="double", minValue=0, maxValue=10, defaultValue=0)
	cmds.setAttr(backClawControl+".worldSpace", k=1, cb=1)
	
	parentCon = cmds.orientConstraint(ankleLocal, ankleWorld, backClawCON, mo=1, skip="none")[0]
	cmds.setDrivenKeyframe(parentCon, at=ankleLocal+"W0", currentDriver=backClawControl+".worldSpace", driverValue=0, value=1)
	cmds.setDrivenKeyframe(parentCon, at=ankleWorld+"W1", currentDriver=backClawControl+".worldSpace", driverValue=0, value=0)
	
	cmds.setDrivenKeyframe(parentCon, at=ankleLocal+"W0", currentDriver=backClawControl+".worldSpace", driverValue=10, value=0)
	cmds.setDrivenKeyframe(parentCon, at=ankleWorld+"W1", currentDriver=backClawControl+".worldSpace", driverValue=10, value=1)
	
	cmds.parentConstraint(knee2, backClawPOS, mo=1, st="none", sr="none")
	
	#---------rig toes
	toesDict = {"inToe_ik":[frontToeIn1, frontToeIn2, frontToeIn3],\
				"midToe_ik": [frontToe1, frontToe2, frontToe3],\
				"backToe_ik":[frontToeBack1, frontToeBack2, frontToeBack3]}
	for toe in toesDict.keys():
		toe1 = toesDict[toe][0]
		toe2 = toesDict[toe][1]
		toe3 = toesDict[toe][2]
		
		toeIKHandleNodes = cmds.ikHandle(solver="ikSCsolver", sj=toe1, ee=toe3, n=nameNode(toe, "left", "IK"))
		toeIKHandle = toeIKHandleNodes[0]
		
		toeNodes = createControl(side, toe,"orient", sdk=1, con=1)
		toeControl = toeNodes[-1]
		toeSDK = toeNodes[2]
		toeCON = toeNodes[1]
		toePOS = toeNodes[0]
		
		alignNodes(toePOS, [toe3])
		#align toe control so Y is perpentucular to the ground
		helperNode = cmds.createNode("transform", n="__TO_DELETE__")
		cmds.delete(cmds.pointConstraint(toe3, helperNode, mo=0, skip="none"))
		cmds.setAttr(helperNode+".ty", 1000)
		
		tipToeJoint = cmds.listRelatives(toe3)[0]
		
		cmds.delete(cmds.aimConstraint(helperNode, toePOS, aimVector=[0, 1, 0], upVector=[0,0,1], worldUpType="object",worldUpObject=tipToeJoint, mo=0))
		
		cmds.parent(toeIKHandle, toeControl)
		cmds.orientConstraint(toeControl, toe3, mo=1, skip="none")
		
		cmds.parent(toePOS, heelRollControl)
		cmds.delete(helperNode)
		
	#------rig back toe on the ankle claw
	backTCons1 = rigFKJoint(heelToe1, side, heelToe1, "cube", sdk=1, con=1)
	backTCons2 = rigFKJoint(heelToe2, side, heelToe2, "cube", sdk=1, con=1)
	
	cmds.parent(backTCons2[0], backTCons1[-1])
	cmds.parent(backTCons1[0], backClawControl)
	
	cmds.select(footControl, r=1)
	print "done"
	
def rigBackLegFK(side, mainLegJoints=["hip1", "hip2", "knee1", "knee2", "foot", "footShellJnt", "heel", \
					"frontToeIn1", "frontToeIn2", "frontToeIn3",\
					"frontToe1", "frontToe2", "frontToe3",\
					"frontToeBack1", "frontToeBack2", "frontToeBack3",\
					"heelToe1", "heelToe2"]):
	
	shortside = ""
	if side == "right":
		shortSide = "rt"
	elif side == "left":
		shortSide = "lf"
	i = 0
	lastControl = ""
	parent = ""
	jointsLegNewNames = []
	for jnt in mainLegJoints:
		print jnt
		
		#get the base name of the joint
		base = jnt.split("_")[1]+"_fk"
		
		#make the full name
		print shortSide
		newJointName = nameNode(base,side, "ctrl")
		#rename joint
		
		
		#add shape node
		mel.eval('source "wireShape.mel"; wireShape("circleX");')
		ctrl = cmds.ls(sl=1)[0]
		mel.eval("SelectCurveCVsAll")
		cmds.scale(50, 50, 50)
		shapeName = cmds.listRelatives(ctrl, s=1, fullPath=1)[0]
		cmds.select(jnt, r=1)
		cmds.parent(shapeName, shape=1, add=1)
		
		cmds.rename(jnt, newJointName)
		jointsLegNewNames.append(newJointName)
		cmds.delete(ctrl)
	
	if side == "right":
		shortSide = "R_"
	elif side == "left":
		shortSide = "L_"
		
	#rig the pistons in the back of the knee
	inPipe = shortSide+"pipe7_J_FK"
	inPipeEnd = shortSide+"pipe7a_J_FK"
	outPipe = shortSide+"pipe8_J_FK"
	outPipeEnd = shortSide+"pipe8a_J_FK"
	
	
	
	backKneePipes = {inPipe:inPipeEnd,outPipe:outPipeEnd}
	for pipe in backKneePipes:
		pipeStart = pipe
		pipeEnd = backKneePipes[pipe]
		#create an ikHandle on the pipe and parent it under the claw control
		pipeIK = cmds.ikHandle(solver="ikSCsolver", sj=pipeStart, ee=pipeEnd, n=nameNode(pipe, side, "IK"))[0]
		
		#figure out the name of the claw control
		base = mainLegJoints[6].split("_")[1]+"_fk"
		clawControl = nameNode(base, side, "ctrl")
		cmds.parent(pipeIK, clawControl)
	
	print "Done"

def createGroupsOnSelectedControls():
	controls = cmds.ls(sl=1)
	for c in controls:		
		createGroupNodesOnSelectedControl(c)
	
def createGroupNodesOnSelectedControl(control, sdk=True, con=True, driver=True):
	"""adds a control to the given joint"""
	conName = control
	sdkNode = ""
	conNode = ""
	posNode = ""
	driverNode = ""
	
	#check if I need to create sdk or con
	if sdk:
		sdkNode = cmds.createNode("transform", n=conName+"_"+sdkNodeSuffix)
		cmds.delete(cmds.parentConstraint(conName, sdkNode, mo=0))
		cmds.parent(conName, sdkNode)
	else:
		print "Skipping SDK"
	
	if con:
		conNode = cmds.createNode("transform", n=conName+"_"+constraintNodeSuffix)
		cmds.delete(cmds.parentConstraint(control, conNode, mo=0))
		if sdk:
			cmds.parent(sdkNode, conNode)
		else:
			cmds.parent(conName, conNode)
	else:
		print "Skipping Constraint node"
		
	posNode = cmds.createNode("transform", n=conName+"_"+positionNodeSuffix)
	cmds.delete(cmds.parentConstraint(control, posNode))
	if con:
		cmds.parent(conNode, posNode)
	elif sdk:
		cmds.parent(sdkNode, posNode)
	else:
		cmds.parent(conName, posNode)
	
	if driver:
		driverNode = cmds.createNode("transform", n=conName+"_"+driverNodeSuffix)
		cmds.delete(cmds.parentConstraint(control, driverNode, mo=0))
		cmds.parent(driverNode, posNode)
	else:
		print "Skipping SDK"
		
	
	
	nodesList = [posNode, conNode, sdkNode, driverNode, conName]
	
	return nodesList

def connectXformAttrs(driver, driven):
	cmds.connectAttr(driver+".t", driven+".t")
	cmds.connectAttr(driver+".r", driven+".r")
	cmds.connectAttr(driver+".s", driven+".s")

def connectXformOnSelection():
	"""select the driver, then the driven and it will connect the translate, rotate and scale attriutes"""
	sel = cmds.ls(sl=1)
	if len(sel) == 2:
		connectXformAttrs(sel[0], sel[1])
	else:
		raise TypeError("Please only select 2 objects")