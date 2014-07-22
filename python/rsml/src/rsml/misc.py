"""
Practical functionality to process rsml-formated mtg
"""

def plant_vertices(g):
    """ return the list of mtg vertices that represent plants """
    return g.vertices(scale=1)
    
def root_vertices(g):
    """ return the list of mtg vertices that represent root axes """
    return g.vertices(scale=g.max_scale())

def root_tree(g, suborder=None):
    """ return the list of root axes in topological order 
    
    If suborder is given, it should be a dictionary of (root-id,value) which is
    used to sort sibling root w.r.t. their respective value.
    """
    if suborder is None:
        sort = lambda x:x[::-1]
    else:
        sort = lambda x: sorted(x, key=suborder.get)[::-1]

    # init with axes with no parent
    axes = sort([a for a in root_vertices(g) if g.parent(a) is None])
    
    # parse root axes in depth-first-order
    tree = []
    while len(axes):
        axe = axes.pop()
        tree.append(axe)
        axes.extend(sort(g.children(axe)))
        
    return tree
    
def root_order(g, tree=None):
    """ return a dictionary of the (numeric) axe order
    
    The order is select as:
      - the value of the 'order' property, if present
      - 1 for axe with no parent
      - the parent order +1 otherwise
      
    tree is the optional list of root id in `g`. If not given, it is computed
    """
    # init order dict
    if 'order' in g.property_names():
        order = g.property('order').copy()
    else:
        order = {}
        
    if tree is None:
        tree = root_tree(g)
        
    # parse all axes s.t. parent are processed before children
    for root in tree:
        parent = g.parent(root)
        order.setdefault(root, 1 if parent is None else order[parent]+1)
        
    return order
        
