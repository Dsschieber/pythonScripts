""" 
baking tools script.

functions
-bakeJointsToWorld
-selectJointsFromGeometry


"""

import pymel.core as pm
from maya import cmds
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def bakeJointsToWorld():
	"""

	takes a selection of joints, creates a joint,
	bakes that joint to worldPos of selection, then parents selection under bakedJoints. 
	This is good if your fbx joints are losing their local space.

	"""

	selObj = cmds.ls(sl=True)

	#Check if an object is selected
	if selObj == []:
		cmds.confirmDialog(t='Warning!',message='Please Select min. one Child Object',ds='ok',icn='information')



	bakeList = []
	for n in selObj:
		
		#check if selected object is a child of an object			
		par = cmds.listRelatives(n,parent=True)
		if par == None:
			cmds.confirmDialog(t='Warning!',message='%s has no Parent Object' %n ,ds='ok',icn='information')
			
		else:
			#duplicate object 
									
			duplObj = cmds.duplicate(n,name=n+'_bakedToWorld',rc=True,rr=True)
			
			childrenTd = cmds.listRelatives(duplObj,c=True,pa=True)
			if childrenTd > 0:
				for c in childrenTd[1:]:
					cmds.delete(c)

			toBake = cmds.parent(duplObj,w=True)
			bakeList.append(toBake)
			cmds.parentConstraint(n,toBake,mo=False)
			cmds.scaleConstraint(n,toBake,mo=False)
			
			

	#get Start and End Frame of Time Slider
	startFrame = cmds.playbackOptions(q=True,minTime=True)
	endFrame = cmds.playbackOptions(q=True,maxTime=True)

	# bake Animation and delete Constraints

	for i in bakeList:
		cmds.bakeResults(i, t=(startFrame,endFrame))
		cmds.delete(i[0] + '*Constraint*')
	for i in range(len(selObj)):
		cmds.parent( selObj[i], bakeList[i])

def selectJointsFromGeometry():
	""" 
	this function takes a selection of skinned geometry 
	and will select the joints that are skinned to it. 
	"""

	skinnedObject = pm.ls(sl=True)
	uniqueJointList = []

	#when there is more than one skin connection it will throw an error (example skinned blendshape)
	for s in skinnedObject:
		toNode = pm.PyNode(s)
		objectConnections = pm.listHistory(toNode, exactType ="skinCluster")
		if objectConnections == []:
			logger.info(s + " does not have a skinCluster. Script will now cancel.")
			return
		objectJoints = objectConnections[0].getWeightedInfluence()
		for x in objectJoints:
			if not x in uniqueJointList:
				uniqueJointList.append(x)
	
	pm.select(uniqueJointList)

if __name__ == "__main__":
	selectJointsFromGeometry()
