"""
Manage rsml metadata attributes

The metadata element in rsml contains some mandatory content and optional ones.
In the IO operation from rsml file to&from mtg, these metadata are looked for 
in the 'metadata' graph property of the mtg::

    mtg.graph_properties()['metadata']


Mandatory metadata:
 - version: set 1.0 
 - unit:    default is 'pixel'
 - resolution: default is 1
 - software:   default is 'openalea'
 - user:       default is ''
 - file-key:   default is a random unique identifier (uuid4)
 
Optional metadata:
 - property_definition: ....
 - function_definition: ....
 - time_sequence: ...
 
`set_metadata` can be used to retrieve the metadata dictionary. This
function also fill missing items, folowing the specified behavior describe in
the function documentation.
"""
import xml.etree.ElementTree as xml


# ordered list of metadata attribute name
flat_metadata = ['version','unit','resolution','software','user',
                   'last-modified','file-key']
metadata_names = flat_metadata + ['image', 'property-definitions',
                                  'function-definitions', 'time-sequence',
                                  'private']

# default values
default = {'version':1.0,
           'unit':'pixel',
           'resolution':1,
           'software':'openalea',
           'user':'',
           'file-key':''}
#           'image':''}
#           'last-modified':'',


def set_metadata(g):
    """ Set the rsml 'metadata' element from the graph-properties of mtg `g` 
    
    The rsml metadata is a dictionary equivalent to the metadata xml element of
    rsml. Its main purpose is to be used by `rsml.io.Dumper`.
    
    This dictionary is constructed from the 'metadata' item of 
    `g.graph_properties()`, if it exist. Then it adds missing items. 
    In particular:
      - it set the 'last-modified' item to current time
      - if missing, it set the 'file-key' item to a random unique id (uuid4)
      - if the 'image' item is a string, convert it to a dict with item 'name'
      - if 'image.captured' is missing, try to set it to the file 
        'image.name' creation time, if the file exists.
      - if 'image.sha256' is missing, try to set it to file 'image.name' hash
      
    This function update given mtg `g` in-place and returns its updated 
    'metadata' graph properties.
    """
    from datetime import datetime
    
    # metadata from graph properties and default values
    metadata = default.copy()
    metadata.update(g.graph_properties().get('metadata',{}))
    
    # image metadata
    if metadata.has_key('image'):
        if isinstance(metadata['image'],basestring):
            metadata['image'] = dict(name=metadata['image'])
        image = metadata['image']
        
        if not image.has_key('sha256'):                                  
            try:
                import hashlib
                with open(image['name']) as f:
                    sha256 = hashlib.sha256(f.read())
                    image['sha256'] = sha256.hexdigest()
            except IOError: # no such file
                pass
        
        if not image.has_key('captured'):
            try:
                from os.path import getctime
                creation = getctime(image['name'])
                image['captured'] = datetime.fromtimestamp(creation).isoformat()
            except OSError: # no such file
                pass
        
    
    if metadata['file-key']!=default['file-key']:
        import uuid
        metadata['file-key'] = uuid.uuid4()

    # time stamp
    metadata['last-modified'] = datetime.now().isoformat()
    
    g.graph_properties()['metadata'] = metadata

    return metadata
    

def add_property_definition(g, label, type, unit=None, default=None):
    """ add a rsml property definition to mtg `g` 
    
    :Inputs:
      - `label`: 
           The label of the property
      - `type`:  
           Either a string of the rsml type, or a python type object for which
           the suitable rsml type is selected using the `rsml_type` function.
    """
    prop = dict(type=type if isinstance(type,basestring) else rsml_type(type))
    if unit    is not None: prop['unit']    = unit
    if default is not None: prop['default'] = default
    
    gmeta = g.graph_properties().setdefault('metadata',{})
    prop_def = gmeta.setdefault('property-definitions', {})
    prop_def[label] = prop

def rsml_type(python_type):
    """ Automatically select rsml type for the given `python_type` """
    if   issubclass(python_type, bool):  return 'boolean' 
    elif issubclass(python_type, int):   return 'integer' 
    elif issubclass(python_type, long):  return 'integer' 
    elif issubclass(python_type, float): return 'real'
    else:
        from datetime import datetime
        if issubclass(python_type, datetime): return 'datetime'
        else:                                return 'string'

_literal_types = set([type(None),bool,int,float,long,complex,unicode,str])
def filter_literal(obj, default=None):
    """ return given `obj` with only "literal" types
    
    The output can be safely converted to string and evaluated using 
    `ast.literal_eval`::
    
        import ast
        safe_obj = filter_literal(obj)
        assert ast.literal_eval(repr(save_obj))==safe_obj
        
    literal types are strings, number, tuples, lists, dicts, booleans and None
    
    For non-literal content:
     - object with an `iteritems` attribute are parsed and converted to dict
     - object with an `__iter__`  attribute are parsed and converted to list
     - the rest is replaced by given `default`
    """
    if type(obj) in _literal_types:
        return obj
    elif isinstance(obj,tuple):
        return tuple([filter_literal(v,default) for v in obj])
    elif hasattr(obj,'iteritems'):
        return dict((k,filter_literal(v,default)) for k,v in obj.iteritems())
    elif hasattr(obj,'__iter__'):
        return [filter_literal(v,default) for v in obj]
    else:
        return filter_literal(default)
        
