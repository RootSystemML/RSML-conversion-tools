"""
Management of the mtg plant and root properties in accordance to rsml format
"""

def set_rsml_properties(g):
    """ set missing id, label and accession using default behavior """
    set_ids(g)
    set_label(g)
    set_accession(g)


def set_ids(g):
    """ Set missing `id` property of all g vertices to the mtg id """
    ids = g.property('id')
    for vid in g:
        ids.setdefault(vid,vid)
    

def set_label(g, default=['Scene','Plant','Root']):
    """ Set missing `label` of g vertices to the `default` one (w.r.t scale) """
    label = g.property('label')
    def_max = len(default)
    for vid in g:
        label.setdefault(vid,default[min(g.scale(vid),def_max)])

def set_accession(g, axe_order=None, default=['PO:0020127','PO:0020121']):
    """ set missing accession property of root axes """
    from .misc import axe_vertices as get_axes
    from .misc import axe_order    as get_order
    
    if axe_order is None:
        axe_order = get_order(g)
    
    accession = g.property('accession')
    def_max = len(default)
    for axe in get_axes(g):
        accession.setdefault(axe,default[min(axe_order[vid],def_max)])

