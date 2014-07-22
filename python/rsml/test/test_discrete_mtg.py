"""
Test discrete mtg -> continuous -> rsml, and backward
"""

def test_load_discrete():
    import cPickle
    from openalea.deploy.shared_data import shared_data
    import rsml
    filename = shared_data(rsml)/'discrete.bmtg'
    with open(filename) as f:
        g = cPickle.load(f)
    return g
    
def simple_tree():
    """ create a simple tree """
    from openalea.mtg import MTG
    g  = MTG()
    p  = g.add_component(g.root, edge_type='/') # plant
    
    # primary axe
    a1  = g.add_component(p,      edge_type='/') # the axe
    s11 = g.add_component(a1, position=(1,1,0), edge_type='/') # segment 1
    s12 = g.add_child(s11, position=(1,2,0), edge_type='<')    # segment 2
    s13 = g.add_child(s12, position=(1,3,0), edge_type='<')    # segment 3
    s14 = g.add_child(s13, position=(1,4,0), edge_type='<')    # segment 4

    # 1st lateral axe
    a2  = g.add_child(a1, edge_type='/') # the axe
    s21 = g.add_component(a2, position=(0,2,0), edge_type='/') # segment 1
    s21 = g.add_child(s12, s21, edge_type='+')                 # attach on parent segment
    s22 = g.add_child(s21, position=(0,3,0), edge_type='<')    # segment 2

    # 2nd lateral axe
    a3  = g.add_child(a1, edge_type='/') # the axe
    s31 = g.add_component(a3, position=(2,3,0), edge_type='/') # segment 1
    s31 = g.add_child(s13, s31, edge_type='+')                 # attach on parent segment

    return g
    
def test_discrete_to_continuous():
    from rsml.continuous import discrete_to_continuous
    from rsml.continuous import continuous_to_discrete
    
    def test_tree(g0):
        gc = discrete_to_continuous(g0.copy())
        gd = continuous_to_discrete(gc.copy())
        
        assert len(g0.vertices(scale=3))==len(gd.vertices(scale=3)), 'not the same number of segment'
    
    test_tree(simple_tree())           # test simple tree
    test_tree(test_load_discrete())    # test complex tree
    
    
##def test_discrete_to_rsml():
##    needs a tmp file    


