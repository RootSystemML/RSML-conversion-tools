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
      - otherwise, 1 for axe with no parent or the parent order +1
      
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
        
def hausdorff_distance(polyline1,polyline2):
    """
    Compute the hausdorff distance from `polyline1` to `polyline2`
    
    :Inputs:
      `polyline1`: 
         a (k,n1) array for the n1 points of the 1st polyline in k-dimension
      `polyline2`:
         a (k,n2) array for the n2 points of the 2nd polyline in k-dimension
       
    :Output:
       The hausdorff distance:
           max( D(polyline1,polyline2), D(polyline2,polyline1) )
         where
           D(p1,p2) = max_(i in p1)  |p1[i] - closest-projection-on-p2|
    """
    import numpy as _np
    
    p1 = _np.asfarray(polyline1)
    p2 = _np.asfarray(polyline2)
    
    norm = lambda x: (x**2).sum(axis=0)**.5
    
    def max_min_dist(points, polyline):
        v1    = polyline[:,:-1]           # 1st segment vertex, shape (k,n2-1)
        v2    = polyline[:, 1:]           # 2nd segment vertex, shape (k,n2-1)
        sdir  = v2-v1                     # direction vector of segment
        lsl   = norm(sdir)                # distance between v1 and v2
        lsl   = _np.maximum(lsl,2**-5)    
        sdir /= lsl                       # make sdir unit vectors
        
        # distance from v1 to the projection of points on segments
        #    disallow projection out of segment: values are in [0,lsl]
        on_edge = ((points[:,:,None]-v1[:,None,:])*sdir[:,None,:]).sum(axis=0) # (n1,n2-1)
        on_edge = _np.minimum(_np.maximum(on_edge,0),lsl[None,:])
        
        # points projection on sdir
        nproj = v1[:,None,:] + on_edge[None,:,:]*sdir[:,None,:]   # (k,n1,n2-1)
        
        # distance from points to "points projection on sdir"
        return norm(nproj - points[:,:,None]).min(axis=1).max()

    return max(max_min_dist(p1,p2), max_min_dist(p2,p1))


