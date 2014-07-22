"""
Module that provide measuring tools on continuous RSML-type MTG
"""
from .misc import plant_vertices
from .misc import axe_vertices

def _segment_length(geometry):
    """ return an array of the segment length along the root `geometry` """
    import numpy as np
    pos = np.array(geometry)
    vec = np.diff(pos,axis=0)**2
    return (vec.sum(axis=1)**.5)


def axes_length(g):
    """ return a dictionary of (axe-id, axe-length) """
    geometry = g.property('geometry')
    length = g.properties().get('length',{}).copy()
        
    for axe in axe_vertices(g):
        if axe not in length:
            geom = geometry.get(axe)
            if geom is None: length[axe] = 0
            else:            length[axe] = _segment_length(geom).sum()
            
    return length

def parent_position(g):
    """ Try to compute the parent postion of root sub-axes 
    
    The parent position is computed as follow:
      - Use the root axe 'parent_position' property, if present,
      - Otherwise, compute it using 'parent_node', if present,
      - Otherwise, return None
      
    The values are returned as a dictionary of (axe-id, axe-parent-position)
    """
    from . import misc
    axes = misc.axe_vertices(g)
    
    parent_pos  = g.properties().get('parent-position', {}).copy()
    parent_node = g.properties().get('parent-node', {})
        
    # axe arclength computed for parent of subaxes with parent_node prop
    cumlen = {}
    geometry = g.properties().get('geometry')
    def get_pos_from_node(axe):
        if axe not in parent_node:
            return None
        else:
            parent = g.parent(axe)
            if not parent in cumlen:
                cumlen[parent] = _segment_length(geometry[parent]).cumsum()
            return cumlen[parent][parent_node[axe]]
    
    for axe in axes:
        if axe not in parent_pos:
            parent_pos[axe] = get_pos_from_node(axe)
    
    return parent_pos
    
def measurement_table(g):
    """ Return a table (list-of-list) of g measurements
    
    ##todo: finish doc
    """
    m = [] # exported measurements
    
    length = axes_length(g)
    
    # for all plants
    for plant in plant_vertices(g):
        m.append[['plant', plant]]
        
        for axe in axe_vetices(g, plant):
            ##todo: sort by axe branching position, if provided
            m.append[['axe', axe, 'length', length[axe]]]
            
    return m
