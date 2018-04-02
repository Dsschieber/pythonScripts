
def bakeJointsToWorld():
	""" take a selction of joints and bake it to worldspace
		removes joints from current hierarchy and parents them under new baked joint. 
	"""
	from maya import cmds

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