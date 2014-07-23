"""
Module that provide measuring tools on continuous RSML-type MTG
"""
from .misc import root_vertices
from .misc import root_tree
from .misc import root_order

def _segment_length(geometry):
    """ return an array of the segment length along the root `geometry` """
    import numpy as np
    pos = np.array(geometry)
    vec = np.diff(pos,axis=0)**2
    return (vec.sum(axis=1)**.5)


def root_length(g):
    """ return a dictionary of (axe-id, axe-length) """
    geometry = g.property('geometry')
    length = g.properties().get('length',{}).copy()
        
    for axe in root_vertices(g):
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
    parent_pos  = g.properties().get('parent-position', {}).copy()
    parent_node = g.properties().get('parent-node', {})
        
    # axe arclength computed for parent of subaxes with parent_node prop
    cumlen = {}
    geometry = g.properties().get('geometry')
    def get_pos_from_node(axe):
        if axe not in parent_node:
            return None
            
        pnode = parent_node[axe]
        if pnode==0:
            return 0
            
        parent = g.parent(axe)
        if not parent in cumlen:
            cumlen[parent] = _segment_length(geometry[parent]).cumsum()
            
        return cumlen[parent][pnode-1]
    
    # parse all root axes
    for axe in root_vertices(g):
        if axe not in parent_pos:
            parent_pos[axe] = get_pos_from_node(axe)
    
    return parent_pos
    
def measurement_table(g):
    """ Return a table (list-of-list) of g measurements
    
    Root are given in tree order (i.e. depth-first-order)
    """
    from . import properties as prop
    
    parpos = parent_position(g)
    tree   = root_tree(g, suborder=parpos)
    order  = root_order(g, tree=tree)
    length = root_length(g)
    
    ids    = prop.set_ids(g)
    acc    = prop.set_accession(g, root_order=order)
    parent = [(root,g.parent(root)) for root in tree]
    parent = dict((r, None if p is None else ids[p]) for r,p in parent)

    table = [None]*len(tree)
    for i,root in enumerate(tree):
        row = [ids[root], order[root], acc[root], parent[root], parpos[root], length[root]]
        table[i] = row
            
    return table
    
def export(g, filename, sep='\t'):
    """ save output of measurement_table in `filename` with csv format """
    table = measurement_table(g)
    table = [map(str,row) for row in table]
    #table = [[' ' if e is None else str(e) for e in row] for row in table]
    csv = [sep.join(row)+'\n' for row in table]
    
    with open(filename,'w') as f:
        f.write('id order PO:accession parent position length\n'.replace(' ','\t'))
        f.writelines(csv)
