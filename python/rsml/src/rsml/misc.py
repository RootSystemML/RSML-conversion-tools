"""
Practical functionality to process rsml-formated mtg
"""

def plant_vertices(g):
    """ return the list of mtg vertices that represent plants """
    return g.vertices(scale=1)
    
def axe_vertices(g, plant=None, sort=True):
    """ return the list of mtg vertices that represent root axes 
    
    :Inputs:
      - g:
         A continuous RSML-like MTG
      - plant:
         if not None, return only the axes of given plant
      - sort:
         If plant and sort, try to sort axes by the branching position
    """
    axes = g.vertices(scale=g.max_scale())
    
    if plant is None:
        return axes
    else:
        axes = [a for a in axes if g.complex(a)==plant]
        if sort:
            if 'parent_node' in g.property_names():
                order = g.property('parent_node')

def root_topsort(g):
    """ return the list of root axes in topological order
    
    The returned value is a list of dictionaries, one for each root axe, 
    containing the following items:
     - id: the id of the root axe
     - plant: the plant id which the root is part of
     - parent: the id of the parent root, or None
    """
    raise NotImplementedError
    
def axe_order(g):
    """ return a dictionary of the (numeric) axe order
    
    The order is select as:
      - the value of the 'order' property, if present
      - 1 for axe with no parent
      - the parent order +1 otherwise
    """
    # init with axes with no parent
    axes = [a for a in axe_vertices(g) if g.parent(a) is None]
    
    # init order dict
    if 'order' in g.property_names():
        order = g.property('order').copy()
    else:
        order = {}
        
    # parse all axes s.t. parent are processed before children
    while len(axes):
        axe = axes.pop()
        parent = g.parent(axe)
        order.setdefault(axe, 1 if parent is None else order[parent]+1)
        axes.extend(g.children(axe))
        
    return order
        
