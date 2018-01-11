'''
Auther: Doug Schieber
Last Updated: October 10, 2016
Version 1.0.0

Script Creates a FBX importer from a Directory

'''
# import shits
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import os

def textFieldQuery():
	search = cmds.textFieldGrp('searchTextField',q=True,tx=True)
	searLen = len(search)
	#change file directory here to your own
	fbx_folder = ("M:") + "/Resources/FBX/"
	
	if(os.path.isdir(fbx_folder)):
		#burn old scrollLayout and build a new one
		cmds.deleteUI("fbxScroll", lay=True)
		scrollFBXLayout = cmds.scrollLayout( "fbxScroll",bgc = (.3,.3,.3), p="FBXFrameLayout", horizontalScrollBarThickness = 30, verticalScrollBarThickness =  30, height = 250)
		#if nothing is in search then build a list from everything in folder
		for fileObject in cmds.getFileList(fld=fbx_folder, fs="*.fbx"):
			if search == '':
				#cmds.file( fbx_folder + object , import=True , mergeNamespacesOnClash=True)
				cmds.button(fileObject , bgc=(.5,.5,.5), label = fileObject , parent = 'fbxScroll', c='cmds.file( \''+fbx_folder+fileObject+'\', i=True , mergeNamespacesOnClash=True)')
			#this part hates me 
			else:
				fileObjects = [fileObject]
				for stuff in fileObjects:
					newObject = stuff.split('|')[-1]
					if search in newObject:
						print(newObject)
						cmds.button(newObject , bgc=(.5,.5,.5), label = fileObject , parent = 'fbxScroll', c='cmds.file( \''+fbx_folder+newObject+'\', i=True , mergeNamespacesOnClash=True)')
		
		
		# so inefficient  
		for fileObject in cmds.getFileList(fld=fbx_folder, fs="*.mb"):
			if search == '':
				#cmds.file( fbx_folder + object , import=True , mergeNamespacesOnClash=True)
				cmds.button(fileObject , bgc=(.5,.5,.5), label = fileObject , parent = 'fbxScroll', c='cmds.file( \''+fbx_folder+fileObject+'\', i=True , mergeNamespacesOnClash=True)')
			#this part hates me 
			else:
				fileObjects = [fileObject]
				for stuff in fileObjects:
					newObject = stuff.split('|')[-1]
					if search in newObject:
						print(newObject)
						cmds.button(newObject , bgc=(.5,.5,.5), label = fileObject , parent = 'fbxScroll', c='cmds.file( \''+fbx_folder+newObject+'\', i=True , mergeNamespacesOnClash=True)')
		
		for fileObject in cmds.getFileList(fld=fbx_folder, fs="*.ma"):
			if search == '':
				#cmds.file( fbx_folder + object , import=True , mergeNamespacesOnClash=True)
				cmds.button(fileObject , bgc=(.5,.5,.5), label = fileObject , parent = 'fbxScroll', c='cmds.file( \''+fbx_folder+fileObject+'\', i=True , mergeNamespacesOnClash=True)')
			#this part hates me 
			else:
				fileObjects = [fileObject]
				for stuff in fileObjects:
					newObject = stuff.split('|')[-1]
					if search in newObject:
						print(newObject)
						cmds.button(newObject , bgc=(.5,.5,.5), label = fileObject , parent = 'fbxScroll', c='cmds.file( \''+fbx_folder+newObject+'\', i=True , mergeNamespacesOnClash=True)')
							
					#print(search)
				#cmds.button(fileObject , bgc=(.5,.5,.5), label = fileObject , parent = 'fbxScroll', c='cmds.file( \''+fbx_folder+fileObject+'\', i=True , mergeNamespacesOnClash=True)')
	
def modelImportWindow():
	modelImport = 'fbxImportWindow'
	if (cmds.window(modelImport, exists=True)):
		print "window already open!!"
		cmds.deleteUI(modelImport)
	modelWin= cmds.window(modelImport ,title='Import FBX', w=360,h=360, mnb=False,mxb=False)
	cmds.columnLayout ("topColumn", adjustableColumn=True)
	cmds.frameLayout(  "FBXsearchEngine", width=350, mh=10, mw = 10, p = 'topColumn' ,label = " Search Library " )
	cmds.frameLayout ("FBXFrameLayout", width=350, mh=10, mw = 10, p = 'topColumn' ,label = " Resource Library " )
	scrollFBXLayout = cmds.scrollLayout( "fbxScroll",bgc = (.3,.3,.3), p="FBXFrameLayout", horizontalScrollBarThickness = 30, verticalScrollBarThickness =  30, height = 250)
	
	cmds.textFieldGrp('searchTextField', p='FBXsearchEngine',l='Search:',cw2=(45,158))
	
	
	#c=Callback(textFieldQuery.search)
	cmds.button(l='Search \nand Build FBX_List',p='FBXsearchEngine',h=44,w=109,c=pm.Callback(textFieldQuery)) 
	
	cmds.separator( w=325,p='FBXsearchEngine')
	
	
	cmds.showWindow( modelWin )
		
	'''
	# Get all the Maya files in a directory
	import os
	maya_files = []
	for content in os.listdir('C:/somedirectory'):
	    if content.endswith('.ma') or content.endswith('.mb'):
	        maya_files.append(content)
	
	# Traverse a directory and all subdirectories for fbx files
	fbx_files = []
	for root, dirs, files in os.walk('/my/tools/directory'):
	    print 'Currently searching {0}'.format(root)
	    for file_name in files:
	        if file_name.endswith('.fbx'):
	            fbx_files.append(os.path.join(root, file_name))
	'''
	
modelImportWindow()