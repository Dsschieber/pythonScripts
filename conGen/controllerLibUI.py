
import os
from PySide import QtGui, QtCore, QtUiTools
from shiboken import wrapInstance
import pymel.core as pm
import maya.OpenMayaUI as omui
import logging

import conGen as conGenAPI
reload(conGenAPI)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
"""
docs here

"""


def getMayaWindow():
    """ pointer to the maya main window
    """
    ptr = omui.MQtUtil.mainWindow()
    if ptr:
        return wrapInstance(long(ptr), QtGui.QMainWindow)


def run():
    """  builds our UI
    """
    global win
    win = ControllerLibraryUI(parent=getMayaWindow())
    win.show()


class ControllerLibraryUI(QtGui.QDialog):

    # path to the .ui file but you don't need it anymore!
    # uiFilePath = os.path.join(os.path.dirname(__file__), 'geomGenerator_v001.ui')

    def __init__(self, parent=None):
        super(ControllerLibraryUI, self).__init__(parent)
        # colormapping dictionary
        self.colorMapDict = {
                    0:None,
                    1:(0,0,0),
                    2:(64,64,64),
                    3:(128,128,128),
                    4:(155,0,40),
                    5:(0,4,96),
                    6:(0,0,255),
                    7:(0,70,25),
                    8:(38,0,67),
                    9:(200,0,200),
                    10:(138,72,51),
                    11:(63,35,31),
                    12:(153,38,0),
                    13:(255,0,0),
                    14:(0,255,0),
                    15:(0,65,153),
                    16:(255,255,255),
                    17:(255,255,0),
                    18:(100,220,255),
                    19:(67,255,163),
                    20:(255,176,176),
                    21:(228,172,121),
                    22:(255,255,99),
                    23:(0,153,84),
                    24:(165,108,49),
                    25:(158,160,48),
                    26:(104,160,48),
                    27:(48,161,94),
                    28:(48,162,162),
                    29:(48,102,160),
                    30:(112,48,162),
                    31:(162,48,106)
                }

        self.scaleVal = 1.0

        self.gridLayout = QtGui.QGridLayout()
        self.verticalLayout = QtGui.QVBoxLayout()

        # label
        self.conLabel = QtGui.QLabel('Simple Controller Library')
        self.verticalLayout.addWidget(self.conLabel)

        # conName
        self.conNameLineEdit = QtGui.QLineEdit()
        self.verticalLayout.addWidget(self.conNameLineEdit)

        # =================================================================
        self.defaultIconImg = os.path.join(conGenAPI.iconsFolderPath, 'noIcon.png')
        thePixMap = QtGui.QPixmap(self.defaultIconImg)
        defPixMap = thePixMap.scaledToWidth(240)

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setPixmap(defPixMap)
        self.verticalLayout.addWidget(self.imageLabel)

        # save button
        self.saveConButton = QtGui.QPushButton("Save Controller")
        self.verticalLayout.addWidget(self.saveConButton)

        # color grid
        self.colorLabel = QtGui.QLabel('Controller Color')
        self.verticalLayout.addWidget(self.colorLabel)

        self.buttonGridLayout = QtGui.QGridLayout()
        self.buttonGridLayout.setHorizontalSpacing(1)
        self.buttonGridLayout.setVerticalSpacing(1)
        self.buttonGrp = QtGui.QButtonGroup()

        # adding buttons to grid
        btnNum = 0

        for i in range(4):
            for j in range(8):
                self.colorButton = QtGui.QPushButton("{0}".format(btnNum))
                self.colorButton.setMinimumSize(0, 0)
                self.colorButton.setMaximumSize(30, 30)
                self.colorButton.setCheckable(True)

                if btnNum == 0:
                    self.colorButton.setDisabled(True)
                    self.colorButton.setText("")
                else:

                    bColor = self.colorMapDict.get(btnNum)
                    #_logger.debug('bColor: {0}'.format(bColor))

                    needsDarkText = [14, 16, 17, 18, 19, 20, 21, 22]
                    if btnNum in needsDarkText:
                        textColor = 'black'
                    else:
                        textColor = 'white'

                    self.colorButton.setStyleSheet('QPushButton{background-color: rgb(%d,%d,%d); color: %s;}' % (bColor[0] ,bColor[1] ,bColor[2] , textColor))

                self.buttonGrp.addButton(self.colorButton)

                # adding buttons to grid
                self.buttonGridLayout.addWidget(self.colorButton, i, j)
                btnNum += 1

        self.verticalLayout.addLayout(self.buttonGridLayout)

        # slider chunk
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.scaleLabel = QtGui.QLabel("Scale:")
        self.horizontalLayout.addWidget(self.scaleLabel)
        self.scaleValLineEdit = QtGui.QLineEdit("1.0")
        self.horizontalLayout.addWidget(self.scaleValLineEdit)
        self.scaleSlider = QtGui.QSlider()
        self.scaleSlider.setMinimum(1)
        self.scaleSlider.setMaximum(100)
        self.scaleSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalLayout.addWidget(self.scaleSlider)
        self.verticalLayout.addLayout(self.horizontalLayout)

        # list widget
        self.conListWidget = QtGui.QListWidget()
        self.verticalLayout.addWidget(self.conListWidget)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        # MANY THINGS YOU HAVE TO ADD
        self.makeConnections()
        self.setWindowTitle("Controller Library")
        self.setLayout(self.gridLayout)
        self.initUiState()
        self.show()

    def initUiState(self):
        """ sets up the initial state of UI"""
        self.updateListWidget()
        self.scaleSlider.setValue(self.scaleVal)

    def makeConnections(self):
        """ connect events in our UI """
        self.conListWidget.itemDoubleClicked.connect(self.doubleClickedItem)
        self.conListWidget.itemClicked.connect(self.itemClickedEvent)
        self.scaleSlider.valueChanged[int].connect(self.sliderEvent)
        self.scaleValLineEdit.editingFinished.connect(self.manualScaleEnteredEvent)
        self.saveConButton.clicked.connect(self.saveControllerEvent)

    def itemClickedEvent(self):
        """when an item is clicked in the list widget"""
        theListWidget = self.sender()

        # print("sender: {0}".format(self.sender()))

        curItem = theListWidget.currentItem()
        curItemText = curItem.text()

        print("item clicked {0}".format(curItemText))

        picPath = os.path.join(conGenAPI.iconsFolderPath, '{0}.jpg'.format(curItemText))

        if not os.path.isfile(picPath):
            picPath = self.defaultIconImg
        newPixMap = QtGui.QPixmap(picPath)
        scaledPixMap = newPixMap.scaledToWidth(240)
        self.imageLabel.setPixmap(scaledPixMap)

    def saveControllerEvent(self):
        """ saves selected curve """
        sel = pm.selected()
        if sel and len(sel) == 1:
            try:
                crvShape = sel[0].getShape()
                if not crvShape.nodeType() == 'nurbsCurve':
                    _logger.error("Selected is not a curve")
                else:
                    _logger.debug("Selected a curve")

            except:
                _logger.error("Error Placeholder")
        else:
            _logger.debug("Do you have anything selected?")

        curveName = self.conNameLineEdit.text()
        if not curveName:
            _logger.error("No Valid Name Entered.")

        # saves the curve
        conGenAPI.saveCon(con=sel[0], conName=curveName, doScreenGrab=True, doCrop=True, debug=False)
        self.updateListWidget()

    def manualScaleEnteredEvent(self):
        """ when a manual scale is entered update the slider and self.scaleVal"""
        # print("DONE!")
        tempScale = float(self.scaleValLineEdit.text())
        if tempScale < 0.1:
            self.scaleVal = 0.1 
        elif tempScale > 10.0:
            self.scaleVal = 10.0
        else:
            self.scaleVal = tempScale
        #self.sliderEvent(self.scaleVal * 10.0)
        self.scaleSlider.setValue(self.scaleVal * 10.0)

    def sliderEvent(self, value):
        """
        """
        # slider = self.sender()
        # value = slider.value()
        print("value: {0}".format(value))

        floatVal = float(value)/10.0
        self.scaleValLineEdit.setText(str(floatVal))

        self.scaleVal = floatVal

    def doubleClickedItem(self):
        """ for when an item is double-clicked"""

        theListWidget = self.sender()

        # print("sender: {0}".format(self.sender()))

        curItem = theListWidget.currentItem()
        curItemText = curItem.text()

        print('currentItem: {0}'.format(curItemText))

        # GET COLOR
        curBtn = self.buttonGrp.checkedButton()
        color = int(curBtn.text()) if curBtn else 0

        conGenAPI.generateCon(conName=curItemText, scale=self.scaleVal, color=color)

    def updateListWidget(self):
        """ updates the list widget 
        """
        # returns sorted list
        conList = conGenAPI.consList()

        # emptying the list widget
        self.conListWidget.clear()
        for con in conList:
            item = QtGui.QListWidgetItem(con)
            self.conListWidget.addItem(item)

    def radioChange(self, geomType):
        self.geomType = geomType
        print("geomType: {0}".format(geomType))


if __name__ == "__main__":
    run()
