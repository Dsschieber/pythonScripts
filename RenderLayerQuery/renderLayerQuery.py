"""
Organizer for render layers and the objects within

------------BUGS----------------
getShadersInRenderLayer not finding all shaders in some renderlayers
getRenderLayerObjects not finding all the polygons that it should 
	Note: this could be due to the top transform being added rather than polygon itself. Will eventually find work around (In Progress.)

"""

try:
    from PySide import QtCore, QtUiTools
    from PySide import QtGui as widgets
    from shiboken import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtUiTools
    from PySide2 import QtWidgets as widgets
    from shiboken2 import wrapInstance

def loadUiWidget(uifilename, parent = None):
	loader = QtUiTools.QUiLoader()
	uiFile = QtCore.QFile(uifilename)
	uiFile.open(QtCore.QFile.ReadOnly)
	ui = loader.load(uiFile, parent)
	uiFile.close()
	return ui

def runRenderLayerMenuUI():
    """Command within Maya to run this script"""
    renderLayerMenu()
    #does not delete ui at the moment

class renderLayerMenu(widgets.QMainWindow):
	from maya import OpenMaya
	import maya.cmds as cmds
	import pymel.core as pm	
	import maya.mel as mel
	from functools import partial
	
	def __init__(self):
		"""Gets maya top window"""
		
		#get directory of UI
		usrProfile = mel.eval('getenv("USERPROFILE")')
		mayaVersion = str(cmds.about(version=True))
		uiFile = (usrProfile+'/Documents/maya/')+mayaVersion+'/scripts/renderlayerOrganizer.ui' #) why python? 
		
		
		main_window = [o for o in widgets.qApp.topLevelWidgets() if o.objectName()=="MayaWindow"][0]	
		super(renderLayerMenu, self).__init__(main_window)
		
		self.renderLayerMenu = loadUiWidget(uiFile, main_window)		
		self.renderLayerMenu.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		self.connectSignals()
		self.renderLayerMenu.show()
	
	def connectSignals(self):
		""" signals for buttons """
		self.renderLayerMenu.refreshRenderLayers_btm.clicked.connect(lambda: self.populateRenderLayerTree())
		self.renderLayerMenu.renderlayerTree.itemClicked.connect(lambda: self.onTreeItemSelect())
		self.renderLayerMenu.shaderListWidget.itemClicked.connect(lambda: self.onShaderItemSelect())
		self.renderLayerMenu.objectListWidget.itemClicked.connect(lambda: self.onObjectItemSelect())
	
	def populateRenderLayerTree(self):
		"""populate renderlayer tree widget"""
		self.renderLayerMenu.renderlayerTree.clear()
		renderLayerItems = self.getRenderLayers()
		items = []
		renderLayerItemSize = len(renderLayerItems)
		count = 0
		for i in renderLayerItems:
			items.append(widgets.QTreeWidgetItem(count))
			items[count].setText(0, i)
			print(count, i)
			count = count + 1
		self.renderLayerMenu.renderlayerTree.insertTopLevelItems(renderLayerItemSize, items)
	
	def populateObjectList(self, items):
		self.renderLayerMenu.objectListWidget.clear()
		self.renderLayerMenu.objectListWidget.addItems(items)
		
	def populateShaderList(self, items):
		self.renderLayerMenu.shaderListWidget.clear()
		self.renderLayerMenu.shaderListWidget.addItems(items)
		
	def onTreeItemSelect(self):
		renderLayerItem = self.renderLayerMenu.renderlayerTree.currentItem()
		itemInTree = self.itemAtIndex(renderLayerItem)
		iteminTreeToString = self.itemAtIndex(renderLayerItem) #does nothing
		shadersInLayer = self.getShadersInRenderLayer(itemInTree)
		polysInLayer = self.getRenderLayerObjects(str(itemInTree))
		if len(polysInLayer) == 0:
			"found no polygons" 
		self.populateShaderList(shadersInLayer)
		self.populateObjectList(polysInLayer)
	
	def onShaderItemSelect(self):
		""" select item in shader list, highlights polys that have shader """
		shaderLayerItem = self.renderLayerMenu.shaderListWidget.currentItem()
		shaderInTree = shaderLayerItem.text()
		mayaSelect = cmds.select(shaderInTree)
		
	def onObjectItemSelect(self):
		""" selects item in object list """
		objectLayerTree = self.renderLayerMenu.objectListWidget.selectedItems()
		selectionList = []
		for each in objectLayerTree:
			selectionList.append(each.text())
		mayaSelect = cmds.select(selectionList)

	def itemAtIndex(self, renderLayerItem):
		object = renderLayerItem.text(0)
		return object
	
	def getRenderLayers(self):
		"""gets all user made renderLayers"""
		renderLayers = cmds.ls(type='renderLayer')
		userRenderLayers = []
		for each in renderLayers:
			if ':' in each:
				"namespace found"
			else:
				if (each !="defaultRenderLayer"): 
					userRenderLayers.append(each)
		return(userRenderLayers)
	
	
	def getRenderLayerObjects(self, renderLayer):
		"""returns objects in a renderlayer"""
		objectsInRenderLayer = cmds.editRenderLayerMembers(renderLayer, q = True, nr=True)
		objects = []
		shapeTransforms = []
		#check for repeat names
		for each in objectsInRenderLayer:
			if each not in objects:
				objects.append(each)
		#check for shapes
		for other in objects:
			whatType = cmds.nodeType(other) 
			if whatType != 'mesh':
				objects.remove(other)		
		shapeTransforms = self.sortPolygons(objects)
		return shapeTransforms
	
	def sortPolygons(self, objects): 
		"""sorts for polygon mesh"""
		shapeTransforms = []
		returnTransforms = []
		for another in objects:
			isPolyMesh = cmds.filterExpand(another, sm=12, fp=True)
			parentTransform = cmds.listRelatives(isPolyMesh, p=True)
			#had to check if list or not
			if isPolyMesh != None:
				if isinstance(parentTransform, list):
					for i in range(len(parentTransform)):
						if parentTransform[i] not in shapeTransforms:
							shapeTransforms.append(parentTransform[i])	
				elif(parentTransform not in shapeTransforms):
					shapeTransforms.append(parentTransform)	
		for i in range(len(shapeTransforms)):
			returnTransforms.append(shapeTransforms[i])
		return returnTransforms
	
	def getShadersInRenderLayer(self, renderLayer):
		"""returns shaders in renderlayer"""
		stringConvert = str(renderLayer) #is returning noneType?
		shadersEngines = []
		shaders = []
		objectsInRenderLayer = cmds.listConnections(stringConvert + '.outAdjustments')
		#shadingEngine
		for each in objectsInRenderLayer:
			if cmds.objectType(each, isType='shadingEngine'):
				shadersEngines.append(each)
		for object in shadersEngines:
			temp = cmds.listConnections(object + '.surfaceShader')
			if temp[0] not in shaders:
				shaders.append(temp[0])
		return shaders
	
	def getTransforms(self, renderLayer): 
		"""in the event that no polygons are found"""
		objectsInRenderLayer = cmds.editRenderLayerMembers(renderLayer, q = True, nr=True)
		allChildren = cmds.listRelatives(objectsInRenderLayer, ad=True)
		meshPolygons = sortPolygons(allChildren)
		return meshPolygons

if __name__ == "__main__":
	runRenderLayerMenuUI()

'''
renderLayersInScene = getRenderLayers()
#render layer to be query
print(len(renderLayersInScene))
num = 8
print(renderLayersInScene[num])
meshPolyInLayer = getRenderLayerObjects(renderLayersInScene[num])
if len(meshPolyInLayer) == 0:
	print("Could not find polygons.")
	meshPolyInLayer = getTransforms(renderLayersInScene[num])
shadersInLayer = getShadersInRenderLayer(renderLayersInScene[num])
'''