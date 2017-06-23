from maya import cmds

import vec
reload(vec)




class NBaseVec(object):
    """
    This is the abstract class for the vectors definition
    """
    def __init__(self, attribute_name, base_name="Vector"):
        """
        This is the constructor

        The constructor is in charge to store the input data and it will also
        automatically create a name generator used internally to name nodes

        Args:

        :attribute_name: str, the name of the attribute that will be used as 
                               vector source
        :base_name: str, the base name used for the generated nodes
        """

      #Store the data
        self.attribute_name= attribute_name
        self._generator = None

        #Initialize the internal generator
        self.init_name_generator(base_name)


    def init_name_generator(self, base_name):
        """Initialize the internal generator

        This function is in charge to create the name generator used
        for generating the names used for the nodes.

        Args:
        
        :base_name: str, the base name used to init the generator
        """
        self._generator = (base_name + "%03d" % i for i in range(1, 9999))

 
    def set_generator(self, generator):
        """
        Function that sets in the class the generator we wish to use

        Args:

        :generator: generator, existing generator for the names
        """
        self._generator = generator


    def connect_to(self, target_attr):
        """
        Simple function that connects the internal attribute 
        to the target attribute

        Args:

        :target_attr: str, the attribute to connect to
        """
        cmds.connectAttr(self.attribute_name , target_attr)


    def as_list(self):
        """
        This function returns the value of the vector as a list

        :return: list
        """
        attr = cmds.getAttr(self.attribute_name)
        if not isinstance(attr,list) :
            return [attr]
        else:
            if isinstance(attr[0], tuple):
                return list(attr[0])
            else:
                return attr


    def as_vec(self):
        """
        This function returns the value of the vector as a Vec class

        :return: Vec instance
        """
        return vec.Vec(self.as_list())


    def _generate_node(self, node_type, suffix):
        """
        Generic function for generating nodes named properly

        Args:
        :node_type: str, the type of the node we want to create
        :suffix: str, the suffix for the node
        """
        return cmds.createNode(node_type, 
                n = self._generator.next()+ "_" + suffix)


class NScalar(NBaseVec):
    """
    This class represents a single float number used for vector operation, 
    in pratice it reflects a VEC1 (vec of length one) that is needed in 
    some vector operation, like scalar value operation
    """
    

    def __init__(self, attribute_name, base_name="Vector"):
        """
        This is the constructor

        Args:

        :attribute_name: the name of the attribute that will be used as 
                               vector source
        :base_name: the base name used for the generated nodes
        """ 

        NBaseVec.__init__(self,attribute_name,base_name="Vector")


    @classmethod
    def with_generator(cls, attribute_name, generator):
        """Alternative constructor from an attribute and an existing
        generator

        Args:

        :attribute_name: str, the name of the attribute that will be used as 
                               vector source
        :generator: generator, existing generator for the names
        :return: nVec instance
        """
        instance = cls(attribute_name)
        instance.set_generator(generator)
        return instance


    @classmethod
    def from_value(cls, value, base_name):
        """
        Generating a scalar vector from a value

        This function generates a node and a channel used to host the value
        and attach the channel to a NScalar vector class

        Args:

        :value: float,int, the value of the NScalar
        :base_name: str, the name we will use for the node + "_vec", the attribute name will
                        be generated with base_name + "_from_value"
        """

        node = cmds.createNode("transform", n= base_name + '_vec')
        attr_name = base_name + "_from_value"
        cmds.addAttr(node, ln = attr_name, at="float",
                        k=1)
        cmds.setAttr(node + '.' + attr_name, value)

        return cls(node + '.' + attr_name , base_name)


    def scalar_dynamic(self, scalB):
        """
        The dynamic mult for the NScalar class

        By dynamic I mean that the scalB value is going to be driven by a connection,
        thus needs to be a NScalar instance.

        :scalB: NScalar, the scalar to be multiplied by
        :return: NScalar instance
        """

        md = self._generate_node("multDoubleLinear", "mul")
        cmds.connectAttr(self.attribute_name, md + '.input1')
        cmds.connectAttr(scalB.attribute_name, md + '.input2')

        return NScalar.with_generator(md + ".output", self._generator)

    def scalar_static(self, value):
        """
        The static mult for the NScalar class

        By static  I mean that the scalB value is going to hardcoded in the 
        node performing the operation, which means it wont change over time

        :value: int,float, the value to be multiplied by
        :return: NScalar instance
        """

        md = self._generate_node("multDoubleLinear", "mul")
        cmds.connectAttr(self.attribute_name, md + '.input1')
        cmds.setAttr(md + '.input2',value)

        return NScalar.with_generator(md + ".output", self._generator)

    def division_dynamic(self, scalB):
        """
        The dynamic divison for the NScalar class

        By dynamic I mean that the scalB value is going to be driven by a connection,
        thus needs to be a NScalar instance.

        :scalB: NScalar, the scalar to be divided by
        :return: NScalar instance
        """

        md = self._generate_node("multiplyDivide", "div")
        cmds.connectAttr(self.attribute_name, md + '.input1X')
        cmds.connectAttr(scalB.attribute_name, md + '.input2X')
        cmds.setAttr(md + '.operation',2)

        return NScalar.with_generator(md + ".outputX", self._generator)


    def division_static(self,value):
        """
        The static divison for the NScalar class

        By static I mean that the scalB value is going to be static and hardcoded,
        in the node. Meant for value not changing over time

        Args:

        :value: float,int, the value needed for the operation
        :return: NScalar instance
        """

        md = self._generate_node("multiplyDivide", "div")
        cmds.connectAttr(self.attribute_name, md + '.input1X')
        cmds.setAttr(md + '.input2X', value)
        cmds.setAttr(md + '.operation',2)

        return NScalar.with_generator(md + ".outputX", self._generator)


    def blend(self, scalB, drv):
        """
        Blending function of two scalars

        This function is used to blend two different scalar where the current scalar
        will be at the 0 size of the blend , instead the provided scalar will be to the 1 side
        of the blend

        Args:

        :scalB: NScalar, the instance of the scalar to blend with
        :drv: NScalar, an instance of scalar used to drive the blend
        """
        
        bln = self._generate_node("blendColors", "blen")
        cmds.connectAttr(scalB.attribute_name, bln + '.color1R')
        cmds.connectAttr(self.attribute_name, bln + '.color2R')
        cmds.connectAttr(drv.attribute_name , bln + '.blender')

        return NScalar.with_generator(bln + ".outputR", self._generator)

    def __add__(self,scalB):
        """
        addition operator for NScalar class

        Args:
        
        :scalB: NScalar, the second class for the operation
        :return: NScalar instance
        """        
        pma = cmds.createNode("plusMinusAverage", n = self._generator.next()+ "_sub")
        cmds.connectAttr(scalB.attribute_name, pma + '.input1D[0]')
        cmds.connectAttr(self.attribute_name, pma + '.input1D[1]')

        return NScalar.with_generator(pma+ '.output1D', self._generator)

    def __sub__(self,scalB):
        """
        subtraciton operator for NScalar class

        Args:
        
        :scalB: NScalar, the second class for the operation
        :return: NScalar instance
        """        
        pma = cmds.createNode("plusMinusAverage", n = self._generator.next()+ "_sub")
        cmds.setAttr(pma + '.operation',2)
        cmds.connectAttr(scalB.attribute_name, pma + '.input1D[0]')
        cmds.connectAttr(self.attribute_name, pma + '.input1D[1]')

        return NScalar.with_generator(pma+ '.output1D', self._generator)

    def __mul__( self, scalB):
        """
        The mult operator for scalars

        :scalB: NScalar, the scalar to be multiplied with
        :return: NScalar instance
        """

        return self.scalar_dynamic(scalB)

    def __div__(self, scalB):
        """
        The division operator for scalars

        :scalB: NScalar, the scalar to be divided by
        :return: NScalar instance
        """

        return self.division_dynamic(scalB)

    def __rmul__(self, value):
        """
        Right multiplication operator for NScalar class

        This function gets called in the case we get a float,int multiplied
        by a NScalar instance and it performs a scalar_static operation

        Args:
        
        :value: float,int, the value to scale the vector by
        :return: NVec instance
        """   
        return self.scalar_static(value)

    def __rdiv__(self, value):
        """
        Right division operator for NScalar class

        This function gets called in the case we get a float,int divided
        by a NScalar instance and it performs a scalar_static operation

        Args:
        
        :value: float,int, the value to divide the vector by
        :return: NVec instance
        """   
        return self.division_static(value)


class NVec(NBaseVec):
    """
    This class lets easily perform vector operation as node based 
    maya operation
    """
    
    def __init__(self, attribute_name, base_name="Vector"):
        """This is the constructor

        Args:

        :attribute_name: str, the name of the attribute that will be used as \
        vector source
        :base_name: the base name used for the generated nodes
        """

        NBaseVec.__init__(self,attribute_name,base_name="Vector")


    @classmethod
    def with_generator(cls, attribute_name, generator):
        """Alternative constructor from an attribute and an existing
        generator

        Args:

        :attribute_name: str, the name of the attribute that will be used as 
                               vector source
        :generator: generator, existing generator for the names
        :return: nVec instance
        """
        instance = cls(attribute_name)
        instance.set_generator(generator)
        return instance

    
    def length(self):
        """
        This function computes the length of the vector

        :return: NVec instance
        """

        dist = cmds.createNode("distanceBetween", n= self._generator.next()+"_length")
        cmds.connectAttr(self.attribute_name, dist + '.point2')

        return NScalar.with_generator(dist+ '.distance', self._generator)

    
    def normalize(self):
        """
        This function normalize the vector

        :return: NVec instance
        """

        norm = cmds.createNode("vectorProduct", n = self._generator.next()+ "_norm")
        cmds.connectAttr(self.attribute_name, norm + '.input1')
        cmds.setAttr(norm + '.operation', 0)
        cmds.setAttr(norm + '.normalizeOutput',1)
        return NVec.with_generator(norm+ '.output', self._generator)

    def scalar_dynamic (self, scal):
        '''
        This function performs a scalar multiplication

        This function is called dynamic because it uses a connection to get
        the value for the multiplication, in short it is a NScalar instance (aka a vec1)
        that gets used three times to multiply the current vector

        :scal: NScalar, a scalar class instance
        :return: NVec instance
        ''' 

        assert type(scal) == NScalar, "__sub__ ERROR: input parameter needs to be of type NScalar"

        mult = cmds.createNode("multiplyDivide", n=  self._generator.next()+ '_scalarDyn')
        cmds.connectAttr(scal.attribute_name , mult + '.input2X')
        cmds.connectAttr(scal.attribute_name , mult + '.input2Y')
        cmds.connectAttr(scal.attribute_name , mult + '.input2Z')
        cmds.connectAttr(self.attribute_name, mult + '.input1')
        return NVec.with_generator(mult+ '.output', self._generator)

    def scalar_static(self, value):
        """
        This is a static scalar multiplication of the vector

        By static it means it multiplies by a fixed value which is not dynamic 
        like an attribute connection

        Args:

        :value: float,int, the value for which we wist to scale the vector for
        :return: NVec instance
        """

        mult = cmds.createNode("multiplyDivide", n=  self._generator.next()+ '_scalarStatic')
        cmds.setAttr(mult + '.input2X',value)
        cmds.setAttr(mult + '.input2Y',value)
        cmds.setAttr(mult + '.input2Z',value)
        cmds.connectAttr(self.attribute_name, mult + '.input1')
        return NVec.with_generator(mult+ '.output', self._generator)

    def dot(self, vecB):
        """
        This function performs a dot product

        Args:

        :vecB: NVec, the second class for the operation
        :return: NVec instance
        """ 
        assert type(vecB) == NVec, "__sub__ ERROR: input parameter needs to be of type NVec"

        vecProd = cmds.createNode("vectorProduct", n = self._generator.next()+ "_dot")
        cmds.connectAttr(self.attribute_name , vecProd + '.input1')
        cmds.connectAttr(vecB.attribute_name , vecProd + '.input2')

        return NVec.with_generator(vecProd+ '.output', self._generator)

    def cross(self,vecB):
        """
        Cross product function 

        Args:

        :vecB: NVec, the second class for the operation
        :return: NVec instance
        """
        assert type(vecB) == NVec, "__sub__ ERROR: input parameter needs to be of type NVec"

        vecProd = cmds.createNode("vectorProduct", n = self._generator.next()+ "_cross")
        cmds.setAttr(vecProd + '.operation', 2)
        cmds.connectAttr(self.attribute_name , vecProd + '.input1')
        cmds.connectAttr(vecB.attribute_name , vecProd + '.input2')

        return NVec.with_generator(vecProd+ '.output', self._generator)

    def __len__(self):
        """
        Length operator for the nVec class

        :return: NVec instance
        """

        return self.length()


    def __sub__(self,vecB):
        """
        Subtraction operator for NVec

        Args:

        :vecB: NVec, the second class for the operation
        :return: NVec instance
        """
        assert type(vecB) == NVec, "__sub__ ERROR: input parameter needs to be of type NVec"
        pma = cmds.createNode("plusMinusAverage", n = self._generator.next()+ "_sub")
        cmds.connectAttr(vecB.attribute_name, pma + '.input3D[0]')
        cmds.connectAttr(self.attribute_name, pma + '.input3D[1]')
        cmds.setAttr(pma + '.operation',2)

        return NVec.with_generator(pma+ '.output3D', self._generator)


    def __xor__(self, vecB):
        """
        Cross product operator

        Args:

        :vecB: NVec, the second class for the operation
        :return: NVec instance
        """
        return self.cross(vecB)

    def __add__(self, vecB):
        """
        addition operator for NVec class

        Args:
        
        :vecB: NVec, the second class for the operation
        :return: NVec instance
        """        
        pma = cmds.createNode("plusMinusAverage", n = self._generator.next()+ "_sub")
        cmds.connectAttr(vecB.attribute_name, pma + '.input3D[0]')
        cmds.connectAttr(self.attribute_name, pma + '.input3D[1]')

        return NVec.with_generator(pma+ '.output3D', self._generator)

    def __neg__(self):
        """
        Negation operator for the NVec class
        """
        return self.scalar_static(-1.0)

    def __mul__(self, vecB):
        """
        multiplication operator for NVec class

        Args:
        
        :vecB: NVec, the second class for the operation
        :return: NVec instance
        """        

        return self.dot(vecB)

    def __rmul__(self,value):
        """
        Right multiplication operator for NVec class

        This function gets called in the case we get a float,int multiplied
        by a NVec instance and it performs a static_scalar operation

        Args:
        
        :value: float,int, the value to scale the vector by
        :return: NVec instance
        """   
        return self.scalar_static(value)



"""
#perpendicular
import sys
sys.path.append("/user_data/WORK_IN_PROGRESS/mVec/")

import nVec
reload(nVec)

locBase = "loc_base.worldPosition"
locA = "locA_tip.worldPosition"
locB = "locB_tip.worldPosition"
target = "target_loc.t"
scalar = "scalar_loc.ty"

vecBase = nVec.NVec(locBase,"test")
vecA = nVec.NVec(locA,"test")
vecB = nVec.NVec(locB,"test")
scalV = nVec.NVec(scalar,"scal")
vec1 = vecA - vecBase
vec2 = vecB - vecBase

cross = vec1 ^ vec2
norm = cross.normalize()
final = vecBase + (2*(-norm).scalar_dynamic(scalV))
final.connect_to(target)

"""


"""
import sys
sys.path.append("/user_data/WORK_IN_PROGRESS/mVec/")
from maya import cmds

import nVec
reload(nVec)


locBase = "loc_base.worldPosition"
locA = "locA_tip.worldPosition"
locB = "locB_tip.worldPosition"
target = "target_loc.t"
scalar = "scalar_loc.ty"

vecBase = nVec.NVec(locBase,"test")
vecA = nVec.NVec(locA,"test")
vecB = nVec.NVec(locB,"test")
scalV = nVec.NScalar(scalar,"scal")
vec1 = vecA - vecBase
vec2 = vecB - vecBase

cross = vec1 ^ vec2
norm = cross.normalize()
final = vecBase + (2*(-norm).scalar_dynamic(scalV))
final.connect_to(target)
print final.as_list()

import vec
reload(vec)

locBaseL = cmds.getAttr("loc_base.worldPosition")[0]
locAL = cmds.getAttr("locA_tip.worldPosition")[0]
locBL = cmds.getAttr("locB_tip.worldPosition")[0]
scalV = cmds.getAttr("scalar_loc.ty")
vecBase = vec.Vec(locBaseL)
vecA = vec.Vec(locAL)
vecB = vec.Vec(locBL)

vec1 = vecA - vecBase
vec2 = vecB - vecBase

cross = vec1 ^ vec2
norm = cross.normalize()
final = vecBase + (scalV*2*(-norm))
print final.as_list()

"""


"""
#basic stretch IK

from maya import cmds
import nVec
reload(nVec)

#declaring initial vectors
startV = nVec.NVec("start_drv.worldPosition", "sStretch")
endV = nVec.NVec("end_drv.worldPosition", "eStretch")
poleV = nVec.NVec("poleVec_drv.worldPosition", "pStretch")
stretchV= nVec.NScalar("end_drv.stretch","stretch")
lockV= nVec.NScalar("end_drv.lock","lock")

#computing the length between the end and the start of the chain
distV = endV - startV
length = distV.length()

#getting initial chain length and converting into vectors
upLen = cmds.getAttr(chain[1] + '.tx')
lowLen = cmds.getAttr(chain[2] + '.tx')
upLenV = nVec.NScalar.from_value(upLen, "upLen")
lowLenV = nVec.NScalar.from_value(lowLen, "lowLen")

#getting total length chain (this can be easily multiplied by the global scale)
initLen = upLenV+lowLenV

#finding theratio
ratio = length /initLen

#calculating scaled length
scaledUp = upLenV * ratio
scaledlow = lowLenV * ratio

#computing final blended stretch
finalScaledUp = upLenV.blend(scaledUp, stretchV)
finalScaledLow = lowLenV.blend(scaledlow,stretchV)

#condition node (old school)
cnd = cmds.createNode("condition")
ratio.connect_to(cnd + '.firstTerm')
cmds.setAttr(cnd + '.secondTerm' ,1)
cmds.setAttr(cnd + '.operation', 3)

#connecting our final calculaded stretch node to the cnd colors
finalScaledUp.connect_to(cnd + '.colorIfTrueR')
upLenV.connect_to(cnd + '.colorIfFalseR')
finalScaledLow.connect_to(cnd + '.colorIfTrueG')
lowLenV.connect_to(cnd + '.colorIfFalseG')

cmds.connectAttr(cnd + '.outColorR', chain[1] + '.tx')
cmds.connectAttr(cnd + '.outColorG', chain[2] + '.tx')



"""
"""
#ADVANCED STRETCH
from maya import cmds
import nVec
reload(nVec)

#declaring initial vectors
startV = nVec.NVec("start_drv.worldPosition", "sStretch")
endV = nVec.NVec("end_drv.worldPosition", "eStretch")
poleV = nVec.NVec("poleVec_drv.worldPosition", "pStretch")
stretchV= nVec.NScalar("end_drv.stretch","stretch")
lockV= nVec.NScalar("end_drv.lock","lock")

#computing the length between the end and the start of the chain
distV = endV - startV
length = distV.length()

#getting initial chain length and converting into vectors
upLen = cmds.getAttr(chain[1] + '.tx')
lowLen = cmds.getAttr(chain[2] + '.tx')
upLenV = nVec.NScalar.from_value(upLen, "upLen")
lowLenV = nVec.NScalar.from_value(lowLen, "lowLen")

#getting total length chain (this can be easily multiplied by the global scale)
initLen = upLenV+lowLenV

#finding theratio
ratio = length /initLen

#calculating scaled length
scaledUp = upLenV * ratio
scaledlow = lowLenV * ratio

#computing final blended stretch
finalScaledUp = upLenV.blend(scaledUp, stretchV)
finalScaledLow = lowLenV.blend(scaledlow,stretchV)

#condition node (old school)
cnd = cmds.createNode("condition")
ratio.connect_to(cnd + '.firstTerm')
cmds.setAttr(cnd + '.secondTerm' ,1)
cmds.setAttr(cnd + '.operation', 3)

#connecting our final calculaded stretch node to the cnd colors
finalScaledUp.connect_to(cnd + '.colorIfTrueR')
upLenV.connect_to(cnd + '.colorIfFalseR')
finalScaledLow.connect_to(cnd + '.colorIfTrueG')
lowLenV.connect_to(cnd + '.colorIfFalseG')

#now compute the pole vector lock
#get polevec vectors
upPoleVec = poleV - startV
lowPoleVec = poleV - endV

#computing the length
upPoleLen = upPoleVec.length()
lowPoleLen= lowPoleVec.length()

#blending default length with poleVec vectors
upPoleBlen = upLenV.blend(upPoleLen, lockV)
lowPoleBlen = lowLenV.blend(lowPoleLen, lockV)

#connecting a NScalar to the output of the node
finalStrUp = nVec.NScalar(cnd + '.outColorR')
finalStrLow = nVec.NScalar(cnd + '.outColorG')

#blending the stretch and lock lengths
resUp = finalStrUp.blend(upPoleBlen,lockV)
resLow =finalStrLow.blend(lowPoleBlen,lockV)

#connect final result
resUp.connect_to(chain[1] + '.tx')
resLow.connect_to(chain[2] + '.tx')

"""
