'''

General Operations

================================================================================
Author: Doug Schieber
Script: opLimbCreation_func.py
Date Created: 6/23/2017
Last Updated: 6/23/2017

mMath-Master scripts made by Marco Giordano


================================================================================
					FUNCTIONS:



================================================================================
				    NOTES:



================================================================================

'''

#script testing

import os, sys
sys.path.append("C:\Users\Doug\Documents\GitHub\pythonScripts\LimbBuilder")
import opLimbCreation_func as Oper
import opController_func as CC
reload(Oper)
reload(CC)

def testJoint(locators):
	'''
	for testing operations
	
	'''
	objectName = "test"
	leftRightPrefix = "l_"
	
	#create ik bind chain
	ikJoints = Oper.opMakeJoints( prefix = objectName, limbtype = leftRightPrefix + "IK",jointOrientation = "xyz", locs = locators)
	ikMirroredJoints = Oper.opMirrorJoints(mirrorType=2, mirrorBehaviorType=True, mirrorSearchReplace=['l_','r_'], joints=ikJoints)
	CC.opCreateIkjointChain(joints = ikJoints, prefix = objectName)
	CC.opCreateIkjointChain(joints = ikMirroredJoints, prefix = objectName)
	#do ik control stuff
	
	#create fk bind chain
	fkJoints = Oper.opMakeJoints( prefix = objectName, limbtype = leftRightPrefix + "FK",jointOrientation = "xyz", locs = locators)
	fkMirroredJoints = Oper.opMirrorJoints(mirrorType=2, mirrorBehaviorType=True, mirrorSearchReplace=['l_','r_'], joints=fkJoints)
	#do fk Stuff
	
	#create bind chain
	bnJoints = Oper.opMakeJoints( prefix = objectName, limbtype = leftRightPrefix + "BN",jointOrientation = "xyz", locs = locators)
	bnMirroredJoints = Oper.opMirrorJoints(mirrorType=2, mirrorBehaviorType=True, mirrorSearchReplace=['l_','r_'], joints=bnJoints)
	
	#is not returning binds
	orientConstraints = oper.opOrientBind(bind=bnJoints,fk=fkJoints,ik= ikJoints)
	mirroredOrientConstraints = oper.opOrientBind(bind=bnMirroredJoints,fk=fkMirroredJoints,ik= ikMirroredJoints)
	

def testLocs(createLocs=True):
	locs = []
	if createLocs == True:
		locs = Oper.opCreateLocs()
	return locs

if __name__ == "__main__":

	#testLocs(True)
	testJoint(locators = locs)
	
	