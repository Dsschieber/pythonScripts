def doScreenGrab(conName = ""):
	""" captures the 3D viewport as an Icon Pic, then opens the folder directory it is in"""
	import maya.OpenMaya as api
	import maya.OpenMayaUI as apiUI
	from maya import cmds
	import os
	
	if not conName:
		name = raw_input("Image name?")
		if not name:
			return
		conName = str(name)
	
	#getDirectory
	projectDirectory = os.path.abspath(cmds.workspace(q=True, rd=True) + 'assets')
	
	# get active view
	view = apiUI.M3dView.active3dView()
	
	# create an empty image viewer
	img = api.MImage()
	view.readColorBuffer(img, True)
	
	# estImage = r'C:\Users\Doug\Documents\maya\scripts\Images\textImage.png'
	iconFileName = os.path.join(projectDirectory, "{0}.jpg".format(conName))
	print(iconFileName)
	
	# write to disk
	img.writeToFile(iconFileName, 'jpg')
	os.startfile( projectDirectory)