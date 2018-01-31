Names generation
================

Naming is always a crucial part when it comes to rigging, the main problem is trying to
avoid duplicate names, that can lead to several problems. Even thought here we are dealing with nodes and duplicate names are not going to be a massive problem is still
something to take care of, the other problem is that generating manually a name for each
node we crate it is quite painfull and it wont work with operator math, I have no way 
to passing a name if I am doing something like:

.. code-block:: python

   vec1 + vec2

That name need to be generated in a different way, the first solution would be something on the line

.. code-block:: python

   vec1.sum(vec2, "myName")

Which is not as neat and clean as the __add__ operator, the actual idea came from a friend
of mine Leandro Pedroni, he told me to use generators, that idea worked just great.
Let me explain you really quick.
When you instanciate a N-Class like it can be an NVec, you need to pass a base_name argument.

That argument will be used to initialize a generators that will yield each time a new name.
Lets have a look at the actual code:

.. code-block:: python

   self._generator = (base_name + "%03d" % i for i in range(1, 9999))

Here we created a generator that will result in a series of names padded three, if we pass
"test" as a base name the generator will yield test001, test002 etc.
Then each operator is in charge of adding a suffix to the name based on the operation,
for example : "test002_sub".
Now the next problem that aries is how do you keep generators synced ? We could go down 
the road of having a new generator for each node but you have to input a unique base name
each time which can be trouble some, what I decided to do is to pass down the generator 
from class to class. Here an example

.. code-block:: python

   vec1 = NVec("loc.tx", "aimVec")
   vec2 = NVec("loc2.ty", "upVec")

   cross = vec1^vec2

In the above example we initialize two vectors and we take a cross product, what is 
happening under the hood is that internally the vec1.cross() method is called,
this method is in charge of computing the vector and returnign a new vector class
holding the result, the new instance is created with an alternative constructor which allows a generator to be passed so wont have to be created

.. code-block:: python

  return NVec.with_generator(vecProd+ '.output', self._generator)

In this way the generator is passed from class to class and will be consumed the more 
node we create, I like this approach a lot because it helps visualize the stream of operation, if we see "aimVec" in the name we know that the opration is coming from the 
steam of vec1 etc.

If you don't like the actual default generators the user can crate it's own custom generator and pass it down to the classes and have their customized namings.
