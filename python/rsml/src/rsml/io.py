""" XML SmartRoot / RootNav reader and writer

TODO:
  * Manage metadata
  * Annotations
  * image
  * Time-series

MTG writer:
  * Generate same file.
  * Manage an MTG with 2 scales: Plant, RootAxis
  * Manage an MTG with 3 scales: Plant, RootAxis, Segment

Visualisation:
1. PlantGL and Matplotlib
2. Time-series
3. Annotations

"""
##############################################################################
# XML SmartRoot / RootNav reader and writer
##############################################################################

from ast import literal_eval

import xml.etree.ElementTree as xml
from xml.dom import minidom

#from openalea.core.graph.property_graph import PropertyGraph
from openalea.mtg import MTG, fat_mtg

from . import metadata

class Parser(object):
    """ Read an XML file an convert it into an MTG.

    """

    def parse(self, filename, debug=False):
        self.debug = debug
        self.trash = []
        self._g = MTG()

        # Current proxy node for managing properties
        self._node = None 

        doc = xml.parse(filename)
        root = doc.getroot()
        # recursive call of the functions to add neww plants/root axis to the MTG
        self.dispatch(root)

        g = fat_mtg(self._g)

        # Add metadata as property of the graph
        #g.graph_property()

        return g

    def dispatch(self, elt):
        """ Call the suitable function to process `elt` w.r.t to `elt.tag` """
        try:
            tag = elt.tag.replace('-','_')
            return self.__getattribute__(tag)(elt.getchildren(), **elt.attrib)
        except Exception, e:
            if self.debug:
                print e
                #raise Exception("Unvalid element %s"%elt.tag)
                print "Unvalid element %s"%elt.tag

    @staticmethod
    def add_field(elt, my_dict) :
        """ Update the properties in the MTG """
        tag = elt.tag#.replace('-','_') 
        my_dict[tag]=elt.text

    def rsml(self, elts, **properties):
        """ A RSA with attributes, parameters and a recursive structure.

        """
        for elt in elts:
            self.dispatch(elt)


    def metadata(self, elts, **properties):
        """ Parse image information """

        meta  = self._metadata = dict()
        gprop = self._g.graph_properties()
        for elt in elts:
            elt_tag = elt.tag
            if elt_tag=='last-modified': 
                meta[elt_tag] = str2datetime(elt.text)
            elif elt_tag in ['version','resolution']:
                meta[elt_tag] = literal_eval(elt.text)
            elif elt_tag in ['user','file-key','software','unit']:
                meta[elt_tag] = elt.text
            elif elt.tag in ["property-definitions","time-sequence","image",'private']:
                self.dispatch(elt)
            elif elt_tag=='mtg_graph_properties':
                gprop.update(read_xml_tree(elt))
            else:
                meta[elt_tag] = read_xml_tree(elt)

        gprop['metadata'] = meta

    def property_definitions(self, elts, **properties):
        """ A plant with parameters and a recursive structure.

        """
        self._propdef = {}
        for elt in elts:
            self.dispatch(elt)
        
        self._metadata['property_definitions'] = self._propdef

    def property_definition(self, elts, **properties):
        """ A plant with parameters and a recursive structure """
        prop = dict()
        for elt in elts:
            self.add_field(elt,prop)
        label = prop.pop('label')
        if label:
            self._propdef[label]=prop


    def time_sequence(self, elts, **properties):
        """ A plant with parameters and a recursive structure.

        """
        pass

    def image(self, elts, **properties):
        """ A plant with parameters and a recursive structure.

        """
        meta = self._metadata
        meta['image'] = {}
        for elt in elts:
            self.add_field(elt, meta['image'])     

    def scene(self, elts, **properties):
        """ A plant with parameters and a recursive structure.

        """
        for elt in elts:
            self.dispatch(elt)

    def plant(self, elts, **properties):
        """ A plant with parameters and a recursive structure.

        """
        g = self._g
        self.plant_id = g.add_component(g.root, label='Plant')
        node = self._node = g.node(self.plant_id)

        # Manage the topology
        for elt in elts:
            if elt.tag == 'root':
                self._node = node
            self.dispatch(elt)

    def root(self, elts, **attrib):
        """ A root axis with geometry, functions, properties """
        parent = self._node

        if parent.scale() == 1:
            axis = parent.add_component(edge_type='/', **attrib) # 1st  order
        else:
            axis = parent.add_child(edge_type='+',**attrib)      # 2nd+ order
            
        if 'label' not in attrib:
            axis.label = 'root'

        self._node = axis

        # parse children element (geometry,properties,...)
        for elt in elts:
            if elt.tag == 'root':
                self._node = axis
            self.dispatch(elt)

        self._node = parent

    def properties(self, elts) :
        """ Update the tooy properties in the MTG """
        proxy_node = self._node
        for a in elts:
            # read mtg graph property that was stored in scene properties
            if a.tag=="graph_property":
                gprop = self._g.graph_properties()
                gprop.update(read_xml_tree(a))
                
            # read property value
            elif a.attrib.has_key('value'):
                proxy_node.__setattr__(a.tag, literal_eval(a.attrib['value']))
            else:
                proxy_node.__setattr__(a.tag, a.text)

    def geometry(self, elts, **properties):
        """ A root axis - geometry """
        for elt in elts:
            self.dispatch(elt)

    def polyline(self, elts, **properties):
        """ A root axis - geometry - polyline """
        self._polyline = []  # will store all points in `elts`
        for elt in elts:
            self.dispatch(elt)

    def point(self, elts, **properties):
        poly = self._polyline
        point = []
        if properties:
            coords = ['x', 'y', 'z']
            point = [float(properties[c]) for c in coords if c in properties]
        else:
            point = [float(elt.text) for elt in elts]
        poly.append(point)

        self._node.geometry = poly

    def functions(self, elts, **properties):
        """ A root axis with geometry, functions, properties.
        """
        for elt in elts:
            self.dispatch(elt)

    def function(self, elts, **properties):
        """ A root axis with geometry, functions, properties.
        """
        g = self._g

        node = self._node

        name = properties['name']
        domain = properties['domain']

        samples = [self.sample(elt, domain=domain) for elt in elts]
        node.__setattr__(name,samples)
        funs = g.graph_properties()['metadata'].setdefault('functions',[])
        if name not in funs:
            funs.append(name)

    def sample(self, elt, domain):
        p = elt.attrib
        value = float(p['value'])

        if domain == "length":
            position= float(p['position'])
            return (position, value)
        else:
            return value

    def annotations(self, elts, **properties):
        """ Annotations attached to a part of the MTG.
        """
        self._node.annotations = []
        for elt in elts:
            self.dispatch(elt)

    def annotation(self, elts, **properties):
        """ Annotations attached to a part of the MTG.
        """
        name = properties.get('name', 'default')
        anno = Annotation(name=name) 
        for elt in elts:
            if elt.tag == 'value':
                anno.value = elt.text
            elif elt.tag == 'software':
                anno.software = elt.text
            elif elt.tag == 'point':
                _properties = elt.attrib
                coords = ['x', 'y', 'z']
                point = [float(_properties[c]) for c in coords if c in _properties]
                anno.points.append(point)
            else:
                # Error
                print 'Invalid Annotation format', elt.tag


class Annotation(object):
    def __init__(self, name):
        self.name = name
        self.points = []
        self.value=''
        self.software = ''

def str2datetime(str_time):
    """ convert datetime string to datetime object """
    from datetime import datetime as dt
    if len(str_time)==10: time_format = '%Y-%m-%d'
    else:                 time_format = '%Y-%m-%dT%H:%M:%S'
    return dt.strptime(str_time[:19], time_format)

def read_xml_tree(elt):
    """ return xml tree `elt` """
    children = elt.getchildren()
    if len(children):
        children_dict = {}
        for child in children:
            children_dict[child.tag] = read_xml_tree(child)
        return children_dict
    else:
        return elt.text
            

##########################################################################
# Create an XML file from an MTG

class Dumper(object):
    """ Convert an MTG into RSML format 

    """
    accession = "{http://www.plantontology.org/xml-dtd/po.dtd}accession"
    def dump(self, graph):
        self._g = graph
        self.mtg()
        
        xmlstr = xml.tostring(self.xml_root, encoding='UTF-8')
        prettystr = minidom.parseString(xmlstr)
        return prettystr.toprettyxml(indent="  ", encoding='UTF-8')

    def SubElement(self, parent, tag, text='', attrib={}, **kwds):
        elt = xml.SubElement(parent, tag, attrib, **kwds)
        elt.text = text
        return elt
        
    def SubTree(self, parent, tag, tree):
        """ recursively add `tree` to xml parent element
        
        `tree` is a dictionary, for which a `tag` child is appended to `parent`
        Then recursively add:
          - a subtree for dictionary item
          - an element otherwise with text set to `str(item-value)`
        """
        elt = xml.SubElement(parent, tag)
        for name, child in tree.iteritems():
            if isinstance(child,dict):
                self.SubTree(elt, name, child)
            else:
                self.SubElement(elt, name, text=str(child))
        return elt

    def mtg(self):
        """ Convert the MTG into a XML tree. """
        # Create a DocType at the begining of the file
        
        # Create the metadata
        self.xml_root = xml.Element('rsml',
                        attrib={"xmlns:po":"http://www.plantontology.org/xml-dtd/po.dtd"})
        self.xml_nodes = {}

        self.metadata()
        self.scene()

    def metadata(self):
        g = self._g
        self.xml_meta = xml.SubElement(self.xml_root,'metadata')

        gmetadata = metadata.set_metadata(g)
        
        for tag in metadata.flat_metadata:
            self.SubElement(self.xml_meta, tag=tag, text=str(gmetadata[tag]))
            
        # image metadata
                
        self.image(gmetadata)
        self.property_definitions(gmetadata)
        print 'TODO: time-sequence'
        
    def image(self,metadata):
        """ dump image element of metadata """
        image = metadata.get('image')
        if image is None: return
        
        img = self.SubElement(self.xml_meta, 'image')
        for tag, text in image.iteritems():
            self.SubElement(img, tag, text=str(text))
                
    def property_definitions(self, metadata):
        """ dump property definitions of metadata """
        gproperties = metadata.get('property-definitions')
        if gproperties is None: 
            return
        
        pdefs = self.SubElement(self.xml_meta, 'property-definitions')
        for label,prop in gproperties.iteritems():
            pdef = self.SubElement(pdefs, tag='property-definition')
            self.SubElement(pdef, tag='label', text=str(label))
            tags = prop.keys()
            tags = [tag for tag in ['type','unit','default'] if tag in tags]
            for tag in tags:
                self.SubElement(pdef, tag=tag, text=str(prop[tag]))
        

    def scene(self):
        g = self._g

        self.xml_scene = self.SubElement(self.xml_root, 'scene')

        # put non-metadata graph properties into 'graph_property' scene 
        # TODO: Add other scene properties?
        gprop = dict((k,v) for (k,v) in g.graph_properties().iteritems() if k!='metadata')
        if len(gprop):
            gprop = metadata.filter_literal(gprop)
            #sc_prop  = self.SubElement(self.xml_scene, 'properties')
            #sc_gprop = self.SubTree(sc_prop, 'graph_property', gprop)
        
        # Traverse the MTG
        self.plants = []
        #self.branching_point = {}
        #self.spaces = 0
        for tree_id in g.components_iter(g.root):
            self.plant(tree_id)

            # for vid in traversal.iter_mtg2(g, tree_id):
            #     if vid == tree_id: 
            #         continue

            #     self.process_vertex(vid)



    def plant(self, vid):
        g = self._g


        self.prev_node = g.node(vid)
        props = g[vid]

        self.xml_nodes[vid] = plant = self.SubElement(self.xml_scene, 'plant')        

        # Extract SegmentType & LeafType
        plant.attrib['id'] = str(props.pop('id', vid))
        plant.attrib['label'] = str(props.pop('label', g.label(vid)))        
        
        for rid in g.component_roots_iter(vid):
            self.root(plant, rid)
        # Manage the recursive structure?
        # self.plants.append(tree)

    def root(self, xml_parent, mtg_vid):
        g = self._g
        vid = mtg_vid
        
        self.xml_nodes[vid] = axis = self.SubElement(xml_parent, 'root') 

        # set xml attributes
        props = g[vid]
        axis.attrib['id']    = str(props.pop('id', vid))
        axis.attrib['label'] = str(props.pop('label', g.label(vid)))
        if 'po:accession' in props:
            axis.attrib['po:accession'] = str(props.pop('po:accession'))

        # set xml axis element
        self.properties(vid, axis)
        ##self.functions(axis,**props)
        self.geometry(axis,**props)
        
        # process children root axis
        # --------------------------
        for subroot in g.children(vid):
            self.root(axis, subroot)

    def geometry(self, axis, **props):
        """ Set the root `axis` geometry elements
        
        `axis` is the xml element id of the root axis
        `props` should contain a suitable 'geometry' attribute
        
        TODO: other geometry types?
        """
        if 'geometry' in props:
            polyline = props['geometry']
            ta = self.SubElement(axis, 'geometry')
            tb = self.SubElement(ta,   'polyline')
            xyz=['x','y','z']
            for pt in polyline: 
                pt_elt = self.SubElement(tb, 'point', 
                                         attrib=dict(zip(xyz,map(str,pt))))
                
        else:
            from warnings import warn 
            xml2mtg_id = dict((xml_id,mtg_id) for mtg_id,xml_id in self.xml_nodes.iteritems())
            mtg_id = xml2mtg_id.get(axis,'undefined')
            warn('Root axis with id={} has no geometry'.format(mtg_id)) # mandatory in rsml
                    
    def properties(self, vid, axis):
        """ set the `axis` properties """
        g = self._g
        meta = g.graph_properties()['metadata'].get('property-definitions', {})
        ax_prop = g[vid]
        ax_prop = dict((p,ax_prop[p]) for p in meta if p in ax_prop)
        
        if len(ax_prop)==0: return
        
        elt_prop = self.SubElement(axis, tag='properties')
        for prop,value in ax_prop.iteritems():
            self.SubElement(elt_prop, tag=prop, attrib={'value':str(value)})
        
    def functions(self, axis, **props):
        """ Set the root `axis` functions
        
        `axis` is the xml element id of the root axis
        `props` ....
        """
        # TODO: Hack, hack, hack...
        g = self._g
        graph_prop = g.graph_properties()
        pname = []
        if 'metadata' in graph_prop:
            meta = graph_prop['metadata']
            if 'functions' in meta:
                pname = meta['functions']
        
        functions_elt = None
        for tag in pname:
            if tag in props:
                if functions_elt is None:
                    functions_elt = self.SubElement(xml_elt, 'functions')
                function_elt = self.SubElement(functions_elt, 'function')
                function_elt.attrib['domain'] = 'polyline'
                function_elt.attrib['name'] = tag
        
                for sample in attrib[tag]:
                    sample_elt = self.SubElement(function_elt, 'sample')
                    if isinstance(sample, (tuple, list)) and len(sample)  == 2:
                        sample_elt.attrib['position'] = str(sample[0])
                        sample_elt.attrib['value'] = str(sample[1])
                    else:
                        sample_elt.attrib['value'] = str(sample)
                        
                        

##########################################################################
# Wrapper functions for OpenAlea usage.

def rsml2mtg(rsml_graph, debug=False):
    """
    Convert a rsml string, or file, to a MTG.
    """
    parser = Parser()
    return parser.parse(rsml_graph, debug=debug)
    

def mtg2rsml(g, rsml_file):
    """
    Write **continuous** mtg `g` in `rsml_file`
    
    :See also: `Dumper`, `rsml.continuous`
    """
    dump = Dumper()
    s = dump.dump(g)
    if isinstance(rsml_file,basestring):
        with open(rsml_file, 'w') as f:
            f.write(s)
    else:
        rsml_file.write(s)
