import pymel.core as pm
from maya import cmds
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def getObjectJoints():
	"""returns list of joints on skinned geometry"""
	skinnedObject = pm.ls(sl=True)
	#when there is more than one skin connection it will throw an error (example skinned blendshape)
	objectConnections = pm.listHistory(skinnedObject[0], exactType ="skinCluster")
	objectJoints = objectConnections[0].getWeightedInfluence()
	return objectJoints
	
def copySkin2Object():
	"""copies skincluster from skinned geometry to another object with no skin"""
	geomObjects = pm.ls(sl=True)
	skinnedObjectJoints = getObjectJoints()
	logger.debug(skinnedObjectJoints)
	skinClusterCopied = pm.skinCluster(geomObjects[1], skinnedObjectJoints)