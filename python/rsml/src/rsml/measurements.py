"""
Module that provide measuring tools on continuous RSML-type MTG
"""
from openalea.mtg import MTG 

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
    
class RSML_Measurements(list):
    """
    Class to store a list of root measurements
        
    Root are stored in tree order (i.e. depth-first-order)
    Each row is a dictionary of measurements
    
    use the `add` method to add measurements from a root MTG
    """
    def __init__(self):
        """ Contrust a RSML_Measurement """
        pass
    
    def add(self, g, name=None):
        """ Add measurements of roots in `g` """ 
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
            table[i] = dict(id=ids[root], order=order[root], accession=acc[root], 
                            parent=parent[root], parent_position=parpos[root], 
                            length=length[root], name=name)
                
        self.extend(table)
            
        return self
    
    def export_csv(self, filename, sep='\t'):
        """ export file `filename` with csv format 
        
        Use `sep` as csv file separator
        """
        keys = ['name','id','order','accession','parent','parent_position','length']
        default = ' '*len(keys)
        
        # convert table entries to a list of string, then table rows to string
        csv = [map(str,map(row.get,keys,default)) for row in self]
        csv = [sep.join(row)+'\n' for row in csv]
        
        # export to given filename
        with open(filename,'w') as f:
            f.write(sep.join(keys)+'\n')
            f.writelines(csv)
            
    def import_csv(self, filename, sep='\t'):
        from csv import reader
        from ast import literal_eval
        
        def try_eval(s):
            try:
                return literal_eval(s)
            except:
                return s
                
        with open(filename) as f:
            content = reader(f,delimiter=sep)
            keys = content.next()
            for row in content:
                self.append(dict(zip(keys,map(try_eval,row))))
                
        
