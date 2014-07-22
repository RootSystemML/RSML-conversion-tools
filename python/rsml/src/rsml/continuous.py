"""
Conversion from discrete to continuous mtg, and vice versa.

In practice, here continuous mtg means the mtg equivalent to rsml.

"""
from openalea.mtg.algo import local_axis
from openalea.mtg.algo import traversal

def discrete_to_continuous(g, position='position'):
    """
    Convert the "discrete mtg" `g` to continuous form **in-place**
    
    Discrete mtg `g` is expected to:
      - have the 3 scales: Plant (1), Axe (2), Segment (3)
      - have a position defined for all segmeent vertices
        The argument `position` defines how to retrieve its value:
         - it can be the name of the mtg property the position is stored in
         - or a function(g,vid) that returns the position of vertex `vid`
      - An axe components is one sequence of successors (edge_type='<')

    The given mtg is then converted to continuous form: 
      - the vertices at higher scale (i.e. the segments) are removed and their 
        position are added in a list which is stored in the 'geometry' property 
        of their complex. 
      - branch axes which are connected to their parent at the segment scale 
        (ie. the 1st segment has its parent on the parent axe) will have their
        'parent_node' property set to the index of the respective node in the
        parent geometry.
        The position of the parent node is added at the beginning of the branch 
    
    todo:
      - setter for PO, label, (...?) => function for label_axis on continuous g
      - convert "discrete" functions (such as diameter)
      - convert continuous functions?
    """
    from rsml.metadata import add_property_definition
    
    # accessor of the segment position property
    if isinstance(position, basestring):
        g_pos = g.property(position)
        position = lambda g,vid: g_pos[vid]
    
    
    # get/initialize "continuous" properties
    geometry =    g.properties().setdefault('geometry',{})
    parent_node = g.properties().setdefault('parent-node',{})
    
    # mapping to recover parent-node
    axe_branch = {}   # axe id => branch node
    geom_index = {}   # node id => index in geometry[axe]
    
    
    # process all axes 
    #    in reverse topological order so 'remove_tree' don't del subroots
    #    construct geometry property
    #    remove segments
    for axe in toporder(g, g.max_scale()-1)[::-1]:
        node0 = g.component_roots(axe)
        if len(node0)==0: continue
        else:             node0 = node0[0]
    
        # branch node
        branch_node = g.parent(node0)
        if branch_node:
            axe_branch[axe] = branch_node
            geom = [position(g,branch_node)]
        else:
            geom = []
          
        # axe node
        for vid in traversal.pre_order2(g,node0):
            geom_index[vid] = len(geom)
            geom.append(position(g,vid))
                
        geometry[axe] = geom
        g.remove_tree(node0)

    # set parent-node property
    for axe,p_node in axe_branch.iteritems():
        parent_node[axe] = geom_index[p_node]

    add_property_definition(g,label='parent-node', type=int)

    return g
    
    
def continuous_to_discrete(g):
    """ Convert mtg `g` from continuous to discrete form **in-place**
    
    Does the reverse of `discrete_to_continuous`:
      - Add a sequence of segments to all axes from their `geometry` attribute
      
    todo:
      - functions
    """
    geometry    = g.property('geometry')
    parent_node = g.property('parent-node')
    
    axe_segments = {}
    for axe in toporder(g, g.max_scale()):
        # get segment on parent branch
        p_axe = g.parent(axe)

        # create 1st segment
        position = geometry[axe]
        if parent_node.has_key(axe):
            p_seg = axe_segments[(p_axe,parent_node[axe])]
            seg   = g.add_component(axe, edge_type='/', position=position[1])
            g.add_child(p_seg,seg, edge_type='+')
            axe_segments[(axe,0)] = p_seg
            shift = 1
        else:
            seg = g.add_component(axe, edge_type='/', position=position[0])
            shift = 0
        axe_segments[(axe,shift)] = seg
            
        # create the other segments
        for i,pos in enumerate(position[(1+shift):]):
            seg = g.add_child(seg,edge_type='<', position=pos)
            axe_segments[(axe,i+1)] = seg
            
        geometry.pop(axe)
        parent_node.pop(axe,None)
    
    return g

def toporder(g, scale):
    """ Return the list of `g` vertices at scale `scale` in topological order """
    axes = []
    map(axes.extend,(traversal.pre_order2(g,vid) 
                          for vid in g.vertices(scale=scale) 
                          if not g.parent(vid)))
    return axes
    
