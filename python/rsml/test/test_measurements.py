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
    from rsml.measurements import root_length
    
    g = simple_tree()
    L = root_length(g)
    
    assert len(L.keys())==2, 'Number of axe incorrect'
    assert sorted(L.values())==[1,3], 'invalid axe length'
    
def test_RSML_Measurement():
    from rsml.measurements import RSML_Measurements
    
    g = simple_tree()
    m = RSML_Measurements()
    m.add(g,name='simple')
    
    assert len(m)==2, 'incorrect number of axe in measurements list'
    assert m[0].get('order')==1, 'incorrect order of 1st axis'
    assert m[1].get('order')==2, 'incorrect order of 2nd axis'
    assert m[0].get('length')==3, 'incorrect length of 1st axis'
    assert m[1].get('length')==1, 'incorrect length of 2nd axis'


