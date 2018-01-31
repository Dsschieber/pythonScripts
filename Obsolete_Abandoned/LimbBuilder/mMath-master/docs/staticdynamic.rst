.. _static-dynamic:

===========================
Static VS Dynamic opeation
===========================

In this page I will discuss the difference between dynamic and static multiplication/division
in the library.

The main difference in the two opration is has the name suggest in the nature of the attribute, if a static operation is used it means that the input value will be 
hardcoded somewhere (depends on the opration) and it will stay the same forever, it 
wont change, unless the user will connect a value to that.
Dynamic operation instead use as source value a node attribute which can change anytime
based on connection.

Let me give you a couple of examples:

.. code-block:: python
 

   #lets declare a vector
   testV = nVec.NVec("testLocator.worldPosition","test")
   #now we are going to negate it
   neg = -testV

Negating a vector is the same as minus one multiplied by the vector, this operation is translated 
in a static multiplication because -1 is a static value and is not going to change over time. Same goes for any other  scalar multiplication, for example:

.. code-block:: python
 

   #lets declare a vector
   testV = nVec.NVec("testLocator.worldPosition","test")
   #now we are going to negate it
   scal = 2*testV

Instead a dynamic scalar operation is performed by a NVector and a NScalar multiplication:

.. code-block:: python
 

   #lets declare a vector and a multiplier
   testV = nVec.NVec("testLocator.worldPosition","test")
   multV = nVec.NScalar("mulLocator.ty", "mul")
   scaledV = testV.scalar_dynamic(multV)

In the above snippet of code we generated a vecor which is caled by the value of ty 
of the mulLocator node. The operation is wired trough connection, this means that changing
the ty value of the mulLocator node will affect dynamically the value of the scaled vector.


