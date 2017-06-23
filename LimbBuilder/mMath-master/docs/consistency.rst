Consistency in the operators
============================

In order to speed up the process and shirnk down the needed amount of code several operators have been implemented in the N-classes.
I tried to be as consistant as possible in the operations and also trying to keep them
as intuitive as possible, and still reflect the same operation in the pure math library.
The main thing to remember is that usually scaling avector by a static value is implemented by right multiplication operator (__rmul__) in both pure math Vec, NScalar
and NVec.
Here some example:

.. code-block:: python
 

   #math vector scalar
   mathV = Vec([1,2,3])
   scaled = 3*Vec

   #Using NScalar
   nSc = NScalar("loc.ty")
   scaled = 3*nSc

   #Using NVec
   nV = NVec("loc.t")
   scaled = 3*nV

As you can see all this operation are consistant bewteen each other, I reserved the regular left multiplication (__mul__ operator), for operation that made sense between
classes.
The __mul__ operator in the vectors has been reseved for the dotProduct/innerProduct
operation, since it is the same in many math library (also in OpenMaya), in the NScalar
class this operation has been reserved for multiplication to another NScalar, which in the end it gets translated in a dynamic_scalar operation (If you think about that, it s a dot product on its own of two size 1 vectors).
In the vectors the NScalar operation needs to be called manually as a function. 

Examples:

.. code-block:: python
 
   #math vector dot
   vec1 = Vec([0,1,0])
   vec2 = Vec([1,0,0])
   dot = vec1 * vec2

   #Dot with NVecs
   vec1 = NVec("loc1.t")
   vec2 = NVec(loc2.t)
   dot = vec1 * vec2

   #NScalar mult
   scal1 = NScalar("loc1.ty")
   scal2 = NScalar("loc2.ty")
   dot = scal1 * scal2


   #here we perform some dynamic scalar operation
   #the dynamic operation in pure math library doesn't make 
   #any sense, since every value is static at the time of the operation
   #the dynamic-static concept is marely a concept in the Node side of the library

   #Dynamic scalar with NVec
   vec1 = NVec("loc1.t")
   scal1 = NScalar("loc1.ty")
   scaled = NVec.scalar_dynamic(scal1)

   #the same operation can be called manually between NScalars
   scal1 = NScalar("loc1.ty")
   scal2 = NScalar("loc2.ty")
   res = scal1.scalar_dynamic(scal2)

