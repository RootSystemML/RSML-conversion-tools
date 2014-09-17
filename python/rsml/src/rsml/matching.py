"""
Simple matching functionalities for RSML MTG trees
"""

import numpy as _np

from rsml.misc import plant_vertices

def match_plants(t1,t2, max_distance=None):
    """
    Find a 1-to-1 matching between plants in `t1` & `t2` 
    
    The matching is done to minimize distance between plants "seed": the 
    mean of the first node of all primary axes.
    
    This function returns:
     - the set of matched (t1-plant-id,t2-plant-id,distance)
     - the set of unmatch t1 plant id
     - the set of unmatch t2 plant id
    
    The matching is done usinf `one_to_one_match`
    """
    from operator import div
    
    # compute seed position of plants in t
    # ------------------------------------
    def seeds_position(t):
        """ return dict of (plant-id, (x, y)) """
        plants = plant_vertices(t)
        
        seed_pos = {}
        geometry = t.property('geometry')
        for plant in plants:
            axes = t.component_roots(plant)
            apos = zip(*[geometry[axe][0] for axe in axes])
            spos = map(div, map(sum,apos), map(len,apos))
            seed_pos[plant] = spos
        
        return seed_pos
        
    seed1 = seeds_position(t1)
    seed2 = seeds_position(t2)
    
    # make distance matrix
    # --------------------
    I1 = seed1.keys()
    I2 = seed2.keys()
    
    X1 = _np.array(seed1.values())[:,None,:]  # (n1, 1,k-dim)
    X2 = _np.array(seed2.values())[None,:,:]  # ( 1,n2,k-dim)
    
    D = ((X1-X2)**2).sum(axis=-1)**.5         # (n1,n2)

    matched,u1,u2 = one_to_one_match(D,max_distance=max_distance)
    
    # convert array id to plant id
    matched = set((I1[p1],I2[p2],d) for p1,p2,d in matched)
    unmatched1 = set(I1[p1] for p1 in u1)
    unmatched2 = set(I2[p2] for p2 in u2)
    
    return matched, unmatched1, unmatched2
        
def match_roots(t1,t2, plant_match, max_distance=None):
    """ Iteratively match root axes following the trees topology
    
    This function iteratively match root axes from 1st to last (topological) 
    order. The matching is selected using `one_to_one_match` using hausdorff
    distance.
    
    :Inputs:
      t1: 1st rsml-mtg
      t2: 2nd rsml-mtg
      plant_match: match between plants in `t1` and `t2`
    
    :Outputs:
      - the set of root matches as (t1_root_id, t2_root_id, hausdorff-distance)
      - the set of unmatched root in t1
      - the set of unmatched root in t2
      
    Note:
      Children of unmatched elements are not listed in unmatched sets
    """
    match = set()
    queue = set()
    unmatched1 = set()
    unmatched2 = set()
    
    def find_match(axes1, axes2):
        if len(axes1) and len(axes2):
            m,u1,u2 = _match_root_axes(t1=t1,axes1=axes1,t2=t2,axes2=axes2,
                                       max_distance=max_distance)
        else:
            m = []
            u1 = axes1
            u2 = axes2
            
        match.update(m)
        queue.update(m)
        unmatched1.update(u1)
        unmatched2.update(u2)
        
    for p1,p2,d in plant_match:
        axes1 = t1.component_roots(p1)
        axes2 = t2.component_roots(p2)
        find_match(axes1,axes2)        
        
    while len(queue):
        r1,r2,d = queue.pop()
        axes1 = t1.children(r1)
        axes2 = t2.children(r2)
        find_match(axes1,axes2)
        
    return match, unmatched1, unmatched2

def _match_root_axes(t1, axes1, t2, axes2, max_distance=None):
    """ return "best" match between axes in `axes1` and in `axes2` """
    from rsml.misc import hausdorff_distance
    
    # construct distance matrix
    geom1 = t1.property('geometry')
    geom2 = t2.property('geometry')
    
    D = _np.zeros((len(axes1),len(axes2)))
    
    axe2_poly = {}
    
    for i,axe1 in enumerate(axes1):
        p1 = _np.array(geom1[axe1])
        
        for j,axe2 in enumerate(axes2):
            if axe2 in axe2_poly:
                p2 = axe2_poly[axe2]
            else:
                p2 = _np.array(geom2[axe2])
                axe2_poly[axe2] = p2
            
            D[i,j] = hausdorff_distance(p1.T,p2.T)


    # compute and return matching
    m, u1, u2 = one_to_one_match(D, max_distance=max_distance)
    
    matches = set((axes1[i],axes2[j],d) for i,j,d in m)
    unmatched1 = set(axes1[i] for i in u1)
    unmatched2 = set(axes2[j] for j in u2)
    
    return matches, unmatched1, unmatched2
    

def one_to_one_match(distance, max_distance=None):
    """ select minimal 1-to-1 matching in `distance` matrix, iteratively
    
    Iteratively select the match `(i,j)` with minimum value in `distance` but
    only if both `i` and `j` were not matched at a previous step.
    
    If `max_distance` is not None, don't match pairs with a distance value
    higher than given `max_distance`
    
    Return:
      - the set match {(i0,j0,d0),(i1,j1,d1),...}
        where i*,j*,d* are the 1st, 2nd indices, and their distance 
      - the set of unmatch i
      - the set of unmatch j
      
    example::
      
      d = np.random.randint(0,10,5,4)
      m,i,j = direct_match(d)
      print '\n'.join(str(ij)+' matched with d='+str(di) for ij,di in zip(m,d[zip(*m)]))
    """
    distance = _np.asarray(distance)
    ni,nj = distance.shape
    distance = distance.ravel()
    order = distance.argsort()
    
    ij = zip(*_np.unravel_index(order,(ni,nj)))
    d  = distance[order].tolist()
    
    if max_distance is None: max_distance=d[-1]
    
    match = set()
    mi = set()
    mj = set()
    for (i,j),dij in zip(ij,d):
        if dij>max_distance or len(mi)==ni or len(mj)==nj: break
        elif i in mi or j in mj: continue
        match.add((i,j,dij))
        mi.add(i)
        mj.add(j)
        
    unmatched_i = mi.symmetric_difference(range(ni))
    unmatched_j = mj.symmetric_difference(range(nj))
    
    return match, unmatched_i, unmatched_j
