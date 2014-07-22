"""
Management of the mtg plant and root properties in accordance to rsml format
"""

def set_rsml_properties(g, prop=[]):
    """ 
    Set missing id, label and accession and properties indicated by `prop`
    
    prop: either 'all'
          or a list which can contain 'length' and 'parent-position' 
    """
    set_ids(g)
    set_label(g)
    set_accession(g)
    
    if prop=='all': prop = ['length', 'parent-position']
    if 'length' in prop:          set_root_length(g)
    if 'parent-position' in prop: set_parent_position(g)


def set_ids(g):
    """ Set missing `id` property of all g vertices to the mtg id """
    ids = g.property('id')
    for vid in g:
        ids.setdefault(vid,vid)
    return ids

def set_label(g, default=['Scene','Plant','Root']):
    """ Set missing `label` of g vertices to the `default` one (w.r.t scale) """
    label = g.property('label')
    def_max = len(default)
    for vid in g:
        label.setdefault(vid,default[min(g.scale(vid),def_max)])
    return label

def set_accession(g, root_order=None, default=['PO:0020127','PO:0020121']):
    """ set missing accession property of root axes """
    from .misc import root_vertices
    from .misc import root_order    as get_order
    
    if root_order is None:
        root_order = get_order(g)
    
    accession = g.property('accession')
    def_max = len(default)-1
    for axe in root_vertices(g):
        accession.setdefault(axe,default[min(root_order[axe]-1,def_max)])
    return accession

def set_root_length(g):
    """ compute root axe length and add it to `g` """
    from .measurements import root_length
    from .metadata import add_property_definition as add_prop_to_meta
    
    length = root_length(g)
    g.properties()['length'] = length
    add_prop_to_meta(g, label='length', type='real')
    return length
    
def set_parent_position(g):
    """ compute root axe length and add it to `g` """
    from .measurements import parent_position
    from .metadata import add_property_definition as add_prop_to_meta
    
    parent_pos = parent_position(g)
    g.properties()['parent-position'] = parent_pos
    add_prop_to_meta(g, label='parent-position', type='real')
    return parent_pos

