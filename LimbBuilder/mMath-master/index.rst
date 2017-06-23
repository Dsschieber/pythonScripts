.. mVec documentation master file, created by
   sphinx-quickstart on Tue Mar  3 12:42:24 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mMath's documentation!
=================================
This is a library born to facilitate the math operation that riggers (but not only)
have to do on daily basis while building rigs. Maya doesn't provide out of the box
with the regular maya commands pure vector operations (only trough OpenMaya, that most
riggers don't know/use) and also doing simple math operation with nodes gets really
tedious.
This library aims to provide a set of tools to simplify all that, the main goal is to have
a pure math library that works in a friendly way with maya and a "mirrored" library
that does the same thing operating with nodes. By changing few bits of the code
the coder should be albe to jump from a pure math implementation to the corresponding
node implementation.

The project is opensource so fill free to comment and partecipate to the project.

Currently only basic vector operation are supported, feel free to let me know what operations you need, aslo I will start working on some matrix operations that can 
be usefull.


Contents:

.. toctree::
   :maxdepth: 2

   docs/getting_started
   docs/staticdynamic
   docs/consistency
   docs/naming
   docs/classes_reference



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

 