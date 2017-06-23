import maya.cmds as cmds
import maya.mel as mel

def altRivet():
	sel = cmds.ls(sl=True, fl=True)
	for N in sel: 
		obj = N
		jack=obj.split(".")[0]
	cmds.select(sel)
	obj=cmds.ls(sl=True, fl=True)
	for e in obj: 
		lofta = cmds.loft( obj, ch=1, u=True, c=False, ar=False, d=3, ss=True, rn=False, po=False, rsn=True)
		renamE = cmds.rename(lofta[1], "Riv_Loft")
		infoNode =cmds.pointOnSurface(lofta[0], ch=True, u=0.55, v=0.33)
		infoSetAtt=cmds.setAttr(infoNode+".turnOnPercentage",1)
		infoNodeRen=cmds.rename(infoNode, renamE+"pointOnSurfaceUI")
		conPos = cmds.connectAttr(renamE+".outputSurface", infoNodeRen+".inputSurface", f=True)
		matrixFourNode= cmds.shadingNode("fourByFourMatrix", asUtility=True, n=renamE+"_matrixFourNode")
		
		connNorX=cmds.connectAttr(infoNodeRen+".normalizedNormalX",matrixFourNode+".in00",f=True)
		connNorY=cmds.connectAttr(infoNodeRen+".normalizedNormalY",matrixFourNode+".in01",f=True)
		connNorZ=cmds.connectAttr(infoNodeRen+".normalizedNormalZ",matrixFourNode+".in02",f=True)
		
		connTanUX=cmds.connectAttr(infoNodeRen+".normalizedTangentUX",matrixFourNode+".in10",f=True)
		connTanUY=cmds.connectAttr(infoNodeRen+".normalizedTangentUY",matrixFourNode+".in11",f=True)
		connTanUZ=cmds.connectAttr(infoNodeRen+".normalizedTangentUZ",matrixFourNode+".in12",f=True)
		
		connTanVX=cmds.connectAttr(infoNodeRen+".normalizedTangentVX",matrixFourNode+".in20",f=True)
		connTanVY=cmds.connectAttr(infoNodeRen+".normalizedTangentVY",matrixFourNode+".in21",f=True)
		connTanVZ=cmds.connectAttr(infoNodeRen+".normalizedTangentVZ",matrixFourNode+".in22",f=True)
		
		connPosX =cmds.connectAttr(infoNodeRen+".positionX", matrixFourNode+".in30", f=True)
		connPosY =cmds.connectAttr(infoNodeRen+".positionY", matrixFourNode+".in31", f=True)
		connPosZ =cmds.connectAttr(infoNodeRen+".positionZ", matrixFourNode+".in32", f=True)
		
		matrixDecompNode = cmds.shadingNode("decomposeMatrix", asUtility=True, n=renamE+"_matrixDecompose")
		connDeMat = cmds.connectAttr(matrixFourNode+".output", matrixDecompNode+".inputMatrix", f=True)
		matrixGrp = cmds.group(em=True, n="matrixRivet")
		matrixGrpTrn = cmds.connectAttr(matrixDecompNode+".outputTranslate", matrixGrp+".translate", f=True)
		matrixGrpRot = cmds.connectAttr(matrixDecompNode+".outputRotate", matrixGrp+".rotate", f=True)
		
		for u in matrixGrp:
			mel.eval('curve -d 1 -p 0 1 0 -p 0 0.987688 -0.156435 -p 0 0.951057 -0.309017 -p 0 0.891007 -0.453991 -p 0 0.809017 -0.587786 -p 0 0.707107 -0.707107 -p 0 0.587785 -0.809017 -p 0 0.453991 -0.891007 -p 0 0.309017 -0.951057 -p 0 0.156434 -0.987689 -p 0 0 -1 -p 0 -0.156434 -0.987689 -p 0 -0.309017 -0.951057 -p 0 -0.453991 -0.891007 -p 0 -0.587785 -0.809017 -p 0 -0.707107 -0.707107 -p 0 -0.809017 -0.587786 -p 0 -0.891007 -0.453991 -p 0 -0.951057 -0.309017 -p 0 -0.987688 -0.156435 -p 0 -1 0 -p -4.66211e-09 -0.987688 0.156434 -p -9.20942e-09 -0.951057 0.309017 -p -1.353e-08 -0.891007 0.453991 -p -1.75174e-08 -0.809017 0.587785 -p -2.10734e-08 -0.707107 0.707107 -p -2.41106e-08 -0.587785 0.809017 -p -2.65541e-08 -0.453991 0.891007 -p -2.83437e-08 -0.309017 0.951057 -p -2.94354e-08 -0.156434 0.987688 -p -2.98023e-08 0 1 -p -2.94354e-08 0.156434 0.987688 -p -2.83437e-08 0.309017 0.951057 -p -2.65541e-08 0.453991 0.891007 -p -2.41106e-08 0.587785 0.809017 -p -2.10734e-08 0.707107 0.707107 -p -1.75174e-08 0.809017 0.587785 -p -1.353e-08 0.891007 0.453991 -p -9.20942e-09 0.951057 0.309017 -p -4.66211e-09 0.987688 0.156434 -p 0 1 0 -p -0.156435 0.987688 0 -p -0.309017 0.951057 0 -p -0.453991 0.891007 0 -p -0.587785 0.809017 0 -p -0.707107 0.707107 0 -p -0.809017 0.587785 0 -p -0.891007 0.453991 0 -p -0.951057 0.309017 0 -p -0.987689 0.156434 0 -p -1 0 0 -p -0.987689 -0.156434 0 -p -0.951057 -0.309017 0 -p -0.891007 -0.453991 0 -p -0.809017 -0.587785 0 -p -0.707107 -0.707107 0 -p -0.587785 -0.809017 0 -p -0.453991 -0.891007 0 -p -0.309017 -0.951057 0 -p -0.156435 -0.987688 0 -p 0 -1 0 -p 0.156434 -0.987688 0 -p 0.309017 -0.951057 0 -p 0.453991 -0.891007 0 -p 0.587785 -0.809017 0 -p 0.707107 -0.707107 0 -p 0.809017 -0.587785 0 -p 0.891006 -0.453991 0 -p 0.951057 -0.309017 0 -p 0.987688 -0.156434 0 -p 1 0 0 -p 0.951057 0 -0.309017 -p 0.809018 0 -0.587786 -p 0.587786 0 -0.809017 -p 0.309017 0 -0.951057 -p 0 0 -1 -p -0.309017 0 -0.951057 -p -0.587785 0 -0.809017 -p -0.809017 0 -0.587785 -p -0.951057 0 -0.309017 -p -1 0 0 -p -0.951057 0 0.309017 -p -0.809017 0 0.587785 -p -0.587785 0 0.809017 -p -0.309017 0 0.951057 -p -2.98023e-08 0 1 -p 0.309017 0 0.951057 -p 0.587785 0 0.809017 -p 0.809017 0 0.587785 -p 0.951057 0 0.309017 -p 1 0 0 -p 0.987688 0.156434 0 -p 0.951057 0.309017 0 -p 0.891006 0.453991 0 -p 0.809017 0.587785 0 -p 0.707107 0.707107 0 -p 0.587785 0.809017 0 -p 0.453991 0.891007 0 -p 0.309017 0.951057 0 -p 0.156434 0.987688 0 -p 0 1 0 ;')
			cmds.addAttr(matrixGrp, at = 'enum', keyable=True, en= 'Off:On', ln='ShapeVis')
			cmds.addAttr( matrixGrp, at = 'double', keyable=True, ln='parameterU')
			cmds.addAttr(matrixGrp, at = 'double', keyable=True, ln='parameterV')
			cmds.setAttr(matrixGrp+'.parameterU', 0.500)
			cmds.setAttr(matrixGrp+'.parameterV', 0.500)
			cmds.connectAttr(matrixGrp+'.parameterU', infoNodeRen+'.parameterU', f=True)
			cmds.connectAttr(matrixGrp+'.parameterV', infoNodeRen+'.parameterV', f=True)
			
			infoNode
			
			myCircle = cmds.ls(sl=True, fl=True)
			myshp = cmds.listRelatives(myCircle[0], shapes=True)
			reN=cmds.rename(myshp, matrixGrp+'Shape')
			cmds.parent(myCircle[0], matrixGrp)
			cmds.makeIdentity(myCircle[0], apply=False, t=1,r=1,s=1,n=0)
			cmds.parent(reN, matrixGrp, r=1, s=1)
			cmds.delete(myCircle[0])
			break
		cmds.delete(lofta[0])
		break