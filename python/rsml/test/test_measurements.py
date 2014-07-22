"""
Tests for the measurements module
"""

def simple_tree():
    """ create a simple tree """
    from openalea.mtg import MTG
    g  = MTG()
    p  = g.add_component(g.root, edge_type='/') # plant
    
    # primary axe
    geom = [[0,0,0],[0,1,0],[0,3,0]]
    a1 = g.add_component(p, edge_type='/', geometry=geom) # primary axe
    
    # secondary axe
    geom = [[0,1,0],[1,1,0]]
    a2  = g.add_child(a1, edge_type='+', geometry=geom)   # 2ndary axe

    return g

def test_length():
    from rsml.measurements import axes_length
    
    g = simple_tree()
    L = axes_length(g)
    
    assert len(L.keys())==2, 'Number of axe incorrect'
    assert sorted(L.values())==[1,3], 'invalid axe length'
