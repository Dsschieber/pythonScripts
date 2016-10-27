'''
empty
'''

#@static
class IKFK(self):
  def __init__(self):
    pass
  def createLocs():
    #create Locators
    varLoc1 = cmds.spaceLocator(name="limb_loc_1")
    varLoc2 = cmds.spaceLocator(name="limb_loc_2")
    varLoc3 = cmds.spaceLocator(name="limb_loc_3")

    #move Locators for clarity
    cmds.move( 3, 0, 0, varLoc1, relative=True, objectSpace=True, worldSpaceDistance=True)
    cmds.move( 1.5, 0, 1, varLoc2, relative=True, objectSpace=True, worldSpaceDistance=True)
    cmds.move( 0, 0, 0, varLoc3, relative=True, objectSpace=True, worldSpaceDistance=True)
	
