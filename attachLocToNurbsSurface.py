import maya.cmds as cmds 

def attachLocToCurve(surfaceVec, SurfacePos, curveObject):
	
	curveShape = cmds.listRelatives(curveObject, c=True)
	
	for i in range(len(surfaceVec)):
		#information Nodes
		decomposeMatrix = cmds.createNode('decomposeMatrix', n = surfaceVec[i] + '_decomposeMatrix')
		nearestPointOnCurve = cmds.createNode('nearestPointOnCurve', n = surfaceVec[i] + '_npoc')
		pointOnCurveInfo = cmds.createNode( 'pointOnCurveInfo', n = surfaceVec[i] + '_posi' )
		#cross Product nodes
		ax_Z = cmds.createNode( 'vectorProduct', n = surfaceVec[i] + '_vectorProduct_ax_Z' )
		ax_X = cmds.createNode( 'vectorProduct', n = surfaceVec[i] + '_vectorProduct_ax_X' )
		#end product nodes
		fourByFourMatrix = cmds.createNode( 'fourByFourMatrix', n = surfaceVec[i] + '_fourByFourMatrix' )
		decompose4x4Matrix = cmds.createNode( 'decomposeMatrix', n = surfaceVec[i] + '_decompose4x4Matrix' )
		
		#set vectorProduct to cross product operation
		cmds.setAttr(ax_Z+".operation", 2)
		cmds.setAttr(ax_X+".operation", 2)
		#decompose matrix for surface vector
		cmds.connectAttr(surfaceVec[i]+".worldMatrix", decomposeMatrix+".inputMatrix", f=True)
		#closest point on surface connections
		cmds.connectAttr(curveShape[0]+".worldSpace", nearestPointOnCurve+".inputCurve",f=True)
		cmds.connectAttr(curveShape[0]+".worldSpace", pointOnCurveInfo+".inputCurve", f=True)
		cmds.connectAttr(decomposeMatrix+".outputTranslate", nearestPointOnCurve+".inPosition",f=True)
		cmds.connectAttr(nearestPointOnCurve+".parameter", pointOnCurveInfo+".parameter", f=True)

		#finding the cross product for XYZ
		cmds.connectAttr(pointOnCurveInfo+ ".normalizedTangent", ax_X + ".input1", f= True)
		cmds.connectAttr(pointOnCurveInfo+ ".normalizedNormal", ax_X + ".input2", f= True)
		cmds.connectAttr(pointOnCurveInfo+ ".normalizedNormal", ax_Z + ".input1", f= True)
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
		cmds.connectAttr(pointOnCurveInfo+ ".normalizedNormalX",fourByFourMatrix+".in10",f = True)
		cmds.connectAttr(pointOnCurveInfo+ ".normalizedNormalY",fourByFourMatrix+".in11",f = True)
		cmds.connectAttr(pointOnCurveInfo+ ".normalizedNormalZ",fourByFourMatrix+".in12",f = True)
		#position
		cmds.connectAttr(pointOnCurveInfo + ".positionX",fourByFourMatrix+".in30",f = True)
		cmds.connectAttr(pointOnCurveInfo + ".positionY",fourByFourMatrix+".in31",f = True)
		cmds.connectAttr(pointOnCurveInfo + ".positionZ",fourByFourMatrix+".in32",f = True)
		
		#at last, output into decompoeMatrix
		cmds.connectAttr(fourByFourMatrix+".output",decompose4x4Matrix+".inputMatrix",f = True)
		cmds.connectAttr(decompose4x4Matrix+".outputRotate",SurfacePos[i]+".rotate",f = True)
		cmds.connectAttr(decompose4x4Matrix+".outputTranslate",SurfacePos[i]+".translate",f = True)
		
if __name__ == "__main__":
	surfaceVec = cmds.ls("tomato") 
	surfacePos = cmds.ls("potato") 
	nurbsCurve = cmds.ls("curve1")
	attachLocToCurve(surfaceVec, surfacePos, nurbsCurve)