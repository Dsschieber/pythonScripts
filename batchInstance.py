import logging
import pymel.core as pm

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def batchInstance():
	""" batch instance a selection  """
	sel = pm.ls(sl=True, fl=True)
	last = sel[0]
	lastShapes = pm.listRelatives(last, f=True, s=True)
	sharedShape =lastShapes[0]
	_logger.debug(sharedShape)
	skip = 0
	for each in sel: 
		if skip > 0:
			shapes = pm.listRelatives(each, s=True, f=True)
			if shapes == 0:
				_logger.warning(each + " has no shape.")
			pm.delete(shapes[0])
			pm.parent(sharedShape, each, s=True, add=True)
		else:
			skip = skip + 1