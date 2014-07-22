Continuous mtg for rsml IO
==========================

The rsml package implements IO functionalities from and to a *continuous mtg*. In this page we gives some description of what is expected to be found in such a mtg object.


mtg2rsml
++++++++

The function `mtg2rsml` convert an *continous mtg* into an XML tree following the RSML standard, then write it into the given file.

Here is a list of mtg content that is parsed into rsml:

Metadata
--------

The mtg can (should?) provide a *graph_property* **"metadata"** (a dictionary) which items are parsed depending on their name (i.e. key):

 - `image`: Should be a dictionary for which each item is added as an XML element: the item value (str) is set as the element *text* value.
 - `property_definition`: not implemented
 - `time_sequence`: not implemented
 - Any other (not dictionary) metadata entries are added as an XML element
 
Scene - Plants
--------------

All components of the mtg root vertex are parsed as rsml *Plant*, for which the following attributes are taken from the respsective properties of the mtg vertex:

 - `ID`: if not provided, use the vertex id
 - `label`: if not provided as a property, use the *mtg label* of the vertex

In addition, 
 
Scene - Root axes
-----------------
 
All the (mtg) components of the processed plant are parsed and added the the rsml structure.

...

Questions:
++++++++++

 - accession: what property name in the mtg?
