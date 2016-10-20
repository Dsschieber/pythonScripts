'''
@author: Doug Schieber
@Last Updated: October 10, 2016
@Version: 0.8.0 Beta


Create a Stretchy IKspline or Static IKspline

Fixes WIP
- GUI work
- Local scaling from Control rather that entire spline on Stretchy IK

'''
import maya.cmds as cmds
import pymel.core as pm

def stretchyIkCreate(strCurve=None, iNum=None):
    strCurve = strCurve
    #ctrlName = ctrlName

    if not strCurve:
        cmds.ls(sl=True)[0]
        
    lStrJnt = []
    
    cmds.select(cl=True)
    
    for i in range(iNum):
        #creates joint chain
        strI = '%s' %i
        strJnt = cmds.joint(n=strCurve+'_jnt'+strI)
        lStrJnt.append(strJnt)
    
    #create ikhandle
    strCurveIk = cmds.ikHandle(sj=lStrJnt[0], ee=lStrJnt[-1], c=strCurve, n=strCurve+'_ik', sol='ikSplineSolver', ccv=False, rootOnCurve=True, parentCurve=False)[0]   
    
    #create ArcLen on curve
    gArcLen = cmds.arclen(strCurve)
    
    gAverage = gArcLen/(iNum-1)
    
    strCurveNode = cmds.createNode('curveInfo', n=strCurve+'_curveInfo')
    
    #create MD and sets it up so the the length of the curve is divided the curves original size. That gives the amount the joints will scale by.
    strMultNode = cmds.createNode('multiplyDivide', n=strCurve+'_divide')
    cmds.setAttr(strMultNode+'.operation', 2)
    cmds.setAttr(strMultNode+'.input2X', gArcLen)
    
    #gets the length of the curve inputs into multiple Divide
    cmds.connectAttr(strCurveNode+'.arcLength', strMultNode+'.input1X')
    
    strCurveShape = Mc.listRelatives(strCurve, s=True)
    print (strCurveShape[0])
    
    #naming conventions are very important here. The Shape name often doesn't match. 
    cmds.connectAttr(strCurveShape[0]+'.worldSpace', strCurveNode+'.inputCurve')
    
    for i in range(iNum):
        if i > 0:
            cmds.setAttr(lStrJnt[i]+'.tx', gAverage)
            
    for jnt in lStrJnt:
        cmds.connectAttr(strMultNode+'.outputX', jnt+'.scaleX')
        
    targetCurve = strCurve # Curve to put clusters on
    curveCVs = cmds.ls('{0}.cv[:]'.format(targetCurve), fl = True) # Get all cvs from curve
    if curveCVs: # Check if we found any cvs
        for cv in curveCVs:
            print 'Creating {0}'.format(cv)
            cmds.cluster(cv, name=targetCurve+'_cl') # Create cluster on a cv
    
    else:
        cmds.warning('Found no cvs!')
    


def IkCreate(strCurve=None, iNum=None):
    strCurve = strCurve
    #ctrlName = ctrlName
    
    if not strCurve:
        cmds.ls(sl=True)[0]
        
    lStrJnt = []
    
    cmds.select(cl=True)
    
    for i in range(iNum):
        #creates joint chain
        strI = '%s' %i
        strJnt = cmds.joint(n=strCurve+'_jnt'+strI)
        lStrJnt.append(strJnt)
    
    #create ikhandle
    strCurveIk = cmds.ikHandle(sj=lStrJnt[0], ee=lStrJnt[-1], c=strCurve, n=strCurve+'_ik', sol='ikSplineSolver', ccv=False, rootOnCurve=True, parentCurve=False)[0] 
    
    #create ArcLen on curve
    gArcLen = cmds.arclen(strCurve)
    
    gAverage = gArcLen/(iNum-1)
    
    for i in range(iNum):
        if i > 0:
            cmds.setAttr(lStrJnt[i]+'.tx', gAverage)
    
    targetCurve = strCurve # Curve to put clusters on
    curveCVs = cmds.ls('{0}.cv[:]'.format(targetCurve), fl = True) # Get all cvs from curve
    if curveCVs: # Check if we found any cvs
        for cv in curveCVs:
            print 'Creating {0}'.format(cv)
            cmds.cluster(cv, name=targetCurve+'_cl') # Create cluster on a cv
    
    else:
        cmds.warning('Found no cvs!')  
        
def loadCurve():
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
            if 'nurbsCurve' in types:
                nurbsSelection = cmds.textFieldGrp('create_IKspline',e=True,tx=sel[0])
                print('complete, Curve loaded.')
            else:
				print('error, Please only Curve.')
        else:
            print('error, Please only load Curve.')
    else:
        print('error, Please select one Curve to load.')
		
#strCurve is the name of the curve. 
#iNum is the number of joints
sel = cmds.ls(sl=True)
print (sel[0])
for cv in sel:
	
	
stretchyIkCreate("bufferTube_CRV", 74)
IkCreate("bloodTube_CRV", 80)

def ikCreateWindow():
    
    if (cmds.window('ikMakeIkWindow', exists=True)):
        print "window already open!!"
        cmds.deleteUI('ikMakeIkWindow')
        
    win= cmds.window("ikMakeIkWindow",title="Make IKSpline From Curve", w=360,h=360, mnb=False,mxb=False)
    
    cmds.columnLayout ("topColumn", adjustableColumn=True)

    cmds.separator(h=12)
    #crvName = cmds.textField(p='topColumn')
    
    #cmds.frameLayout('curveSelection',l='Curve Selection',mh=2,mw=2,li=2,p='topColumn')
    #needs to be editable for arg
    #cmds.textFieldGrp('create_IKspline',l='Curve: ',p='curveSelection',ed=False,cw2=(36,200)) 
    #needs to load up selection into textFieldGrp
    #cmds.button(l='^ Query Curve ^', c=pm.Callback(loadCurve))
    #cmds.separator(h=22, p='curveSelection')
    
    cmds.frameLayout('jointNumberLayout',l='Joints Query',mh=10,mw=5,li=2,p='topColumn')
    cmds.text(label='Number of Joints', align='center',p='jointNumberLayout')
    #needs to pass int to arg
    intStorage = cmds.intField(p='jointNumberLayout', minValue=0, value=1)
    #cmds.separator(h=22, p='jointNumber')
    
    #curveName = cmds.textFieldGrp('create_IKspline',q=True,tx=True)
    numberOfJoints = cmds.intField(intStorage, q=True, v=True)
    
    #c='cmds.file( \''+fbx_folder+fileObject+'\', i=True , mergeNamespacesOnClash=True)')
    cmds.frameLayout('createIkButtonLayout',l='Create Spline',mh=2,mw=2,li=2,p='topColumn')
    stretchySpline=cmds.button('stretchSpline',p='topColumn', label='Stretchy Spline', c=pm.CallbackWithArgs(stretchyIkCreate, 5))
    normalSpline=cmds.button('normalSpline',p='topColumn', label='Normal Spline', c=pm.CallbackWithArgs(IkCreate, 5))
    
    
    
    
    cmds.showWindow( win )
    
ikCreateWindow()

