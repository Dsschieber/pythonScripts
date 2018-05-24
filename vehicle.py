import pymel.core as pm
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""Create a rolling wheel ctrl"""

def rollingWheel(forwardAxis="translateZ", rotationAxis="rotateX", centerPosObj = '', bottomPosObj = '', rollingObject = '', controller = '', suffix = "roll"):
	""" gets radius from bottom and center, 
		uses the translate of controller to move forward, 
		attaching rotation to rollingObject  

		bug: can only move in a single direction. 

	"""
	if not centerPosObj and bottomPosObj and rollingObject and controller:
		logger.info('Arguments not satisfied')
		return
	
	#create nodes
	piNode = pm.shadingNode('multiplyDivide', asUtility=True, n = suffix + '_pi_md')
	distanceNode = pm.shadingNode('multiplyDivide', asUtility=True, n = suffix + '_distance_md')
	fwdNode = pm.shadingNode('multiplyDivide', asUtility=True, n = suffix + '_fwd_md')
	degreeRotNode = pm.shadingNode('multiplyDivide', asUtility=True, n = suffix + '_degreeRot_md')
	distanceDimensionNode = pm.distanceDimension(sp=(centerPosObj.getTranslation()), ep=(bottomPosObj.getTranslation()))
	
	#set initial inputs
	degreeRotNode.setAttr('input2X', -360)
	piNode.setAttr('input2X', 3.14)
	distanceNode.setAttr('input2X', 2)
	fwdNode.setAttr('operation', 2)
	
	#connectInputs
	distanceDimensionNode.connectAttr('distance', distanceNode.input1X)
	distanceNode.connectAttr('outputX', piNode.input1X)
	piNode.connectAttr('outputX', fwdNode.input2X)
	fwdNode.connectAttr('outputX', degreeRotNode.input1X)
	controller.connectAttr(forwardAxis, fwdNode.input1X)
	degreeRotNode.connectAttr('outputX', rollingObject + '.' + rotationAxis)


	
if __name__ == "__main__":
	sel = pm.selected()
	rollingWheel(forwardAxis = 'translateX', rotationAxis = 'rotateZ', centerPosObj = sel[0], bottomPosObj = sel[1] , rollingObject = sel[2], controller = sel[3])
	