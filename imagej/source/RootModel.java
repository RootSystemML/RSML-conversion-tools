

import ij.*;
import ij.gui.PolygonRoi;
import ij.gui.Roi;
import ij.measure.ResultsTable;
import ij.process.*;

import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;

import javax.swing.*;

import java.util.*;
import java.util.List;
import java.io.*;

// XML file support
import javax.xml.parsers.DocumentBuilder; 
import javax.xml.parsers.DocumentBuilderFactory;  
import javax.xml.parsers.ParserConfigurationException;

import org.xml.sax.SAXException;  

/** @author Xavier Draye and Guillaume Lobet - Université catholique de Louvain */


//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


class IdenticalDataFileFilter extends javax.swing.filechooser.FileFilter {

	   String rootFName;
	   
	   public IdenticalDataFileFilter (String rootFName) {
		  int l = rootFName.length();
		  int crop = l-(l/10);
	      this.rootFName = rootFName.substring(0, crop);
	   }

	   public boolean accept(File f) {
		   return (f.getName().toLowerCase().endsWith("xml") && f.getName().startsWith(rootFName));
	   }

	   public String getDescription() {
	      return "SmartRoot Datafiles associated with " + rootFName;
	   }
}

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class DataFileFilterRSML extends javax.swing.filechooser.FileFilter 
implements java.io.FileFilter {

	public DataFileFilterRSML () { }

	public boolean accept(File f) {
		return f.getName().toLowerCase().endsWith("rsml");
	}

	public String getDescription() {
		return "Root System Markup Language";
	}
}
   

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class RootModel extends WindowAdapter{
	  
	
//	static int nextRootKey;
	static String version = "4.1";
	static String datafileKey = "default";	
	
	
   ImagePlus img;
   ImageProcessor ip;
   double angleStep;
   float threshold;
   float dM=0;
   public ArrayList<Root> rootList = new ArrayList<Root>();
   public int nextAutoRootID;

   /** Return code from selectNode() */
   static final int NODE = 1;
   static final int ROOT = 2;
   static final int CHILD = 3;
   static final int PARENT = 4;
   static final int CHILDPARENT = 5;

   /** autoBuildFromNode() estimates the putative location for a new node in the direction of the 
       line joining the previous and current nodes, using a distance which is the minimum of 
       putative distances 1 & 2 (see AUTOBUILD_STEP_FACTOR_BORDER AUTOBUILD_STEP_FACTOR_DIAMETER)
       but which is at least equal to AUTOBUILD_MIN_STEP  */
   /** Putative distance 1 (from the current node) is equal to the
       distance to the root border (along the predicted direction) multiplied by the AUTOBUILD_STEP_FACTOR_BORDER */
   /** Putative distance 2 (from the current node) is equal to the
       root diameter at the current node multiplied by the AUTOBUILD_STEP_FACTOR_DIAMETER */
   /** Minimum angle step for the automatic recentering of nodes in autoBuildFromNode() */
   /** Angle step for the automatic recentering of nodes in autoBuildFromNode(): the angle step
       is equal to AUTOBUILD_THETA_STEP_FACTOR divided by the root diameter */


   float AUTOBUILD_MIN_STEP = 3.0f;
   float AUTOBUILD_STEP_FACTOR_BORDER = 0.5f;
   float AUTOBUILD_STEP_FACTOR_DIAMETER = 2.0f;
   float AUTOBUILD_MIN_THETA_STEP = 0.02f;
   float AUTOBUILD_THETA_STEP_FACTOR = (float) Math.PI / 2.0f;



   /** Modifier flags for tracing operations */
   static final int AUTO_TRACE = 1;
   static final int FREEZE_DIAMETER = 2;
   static final int SNAP_TO_BORDER = 4;
   
   static final int THRESHOLD_ADAPTIVE1 = 1;
   static final int THRESHOLD_ADAPTIVE2 = 2; 
   
   static final int REGULAR_TRACING = 1;
   static final int LATERAL_TRACING = 2;
   static final int LINE_TRACING = 4;
   static final int LATERAL_TRACING_ONE = 8;

   static private DataFileFilterRSML datafileFilterRSML = new DataFileFilterRSML();

   private String directory;
   public String imgName;
   public float previousMagnification = 0.0f;
   public static final String[] fileSuffix = {"xml", "xml01", "xml02", "xml03", "xml04"};
   public static final String[] fileSuffixRSML = {"rsml", "rsml01", "rsml02", "rsml03", "rsml04"};

   private float dpi;
   public float pixelSize;
   
   /** Constructors */  
   public RootModel(String dataFName) {	 
	      dpi = SR.prefs.getFloat("DPI_default", dpi);
	      pixelSize = 2.54f / dpi;
	      readRSML(dataFName);	      	      
   }
   
   
   /**
    * Computed the scale base on an unit and a resolutiono
    */
   public float getDPI(String unit, float resolution){
	   if (unit.startsWith("cm") || unit.startsWith("cen")) {
	          return resolution * 2.54f;
	          }
	      else if (unit.startsWith("mm") || unit.startsWith("mill")) {
	          return (resolution / 10) * 2.54f;
	          }	 
	      else if (unit.startsWith("m") || unit.startsWith("me")) {
	          return (resolution * 100) * 2.54f;
	          }	 	      
	      else if (unit.startsWith("IN") || unit.startsWith("in")) {
	          return resolution;
	          }
	       else {
	    	   return 0.0f;
	          }	      
   }
   

   public void csvSendMarks(PrintWriter pw, boolean header, String name, boolean last){
	   
	   if(header)
		   pw.println("image, source, root, root_name, mark_type, position_from_base, diameter, angle, x, y, root_order, root_ontology, value");
	   String stmt;
       for (int i = 0; i < rootList.size(); i++) {
           Root r = (Root) rootList.get(i);
           // Root origin information
           stmt = name + ", ";
           stmt = stmt.concat(imgName + ", ");  // XD 20110629
           stmt = stmt.concat(r.getRootKey() + ", ");
           stmt = stmt.concat(r.getRootID() + ", ");
           stmt = stmt.concat("Origin, ");
           stmt = stmt.concat("0.0, 0.0, 0.0, ");
           stmt = stmt.concat(r.firstNode.x * pixelSize + ", ");
           stmt = stmt.concat(r.firstNode.y * pixelSize + ", ");
           stmt = stmt.concat(r.isChild()+ ", ");
           stmt = stmt.concat(r.getPoAccession()+ ", ");
           stmt = stmt.concat(imgName);
           pw.println(stmt);
           pw.flush();
           // Marks information
           for (int j = 0; j < r.markList.size(); j++) {
              Mark m = (Mark)r.markList.get(j);
              //Point p = r.getLocation(m.lPos * pixelSize);
              stmt = imgName + ", ";
              stmt = stmt.concat((m.isForeign ? m.foreignImgName : imgName) + ", ");  // XD 20110629
              stmt = stmt.concat(r.getRootKey() + ", ");
              stmt = stmt.concat(r.getRootID() + ", ");
              stmt = stmt.concat(Mark.getName(m.type) + ", ");
              stmt = stmt.concat(r.lPosPixelsToCm(m.lPos) + ", ");
              stmt = stmt.concat(m.diameter * pixelSize + ", ");
              stmt = stmt.concat(m.angle + ", ");
//              if (p != null) {
//                 stmt = stmt.concat(p.x * pixelSize + ", ");
//                 stmt = stmt.concat(p.y * pixelSize + ", ");
//              }
//              else {
//                 SR.write("[WARNING] " + Mark.getName(m.type) + " mark '" + m.value + "' on root '"+ r.getRootID() + "' is past the end of root.");
//                 stmt = stmt.concat(" 0.0, 0.0, ");
//              }
              stmt = stmt.concat(r.isChild()+ ", ");
              stmt = stmt.concat(r.getPoAccession()+ ", ");
              if (m.needsTwinPosition()) 
                 stmt = stmt.concat(((m.twinLPos - m.lPos) * pixelSize) + "");
              else stmt = stmt.concat(m.value + "");
              pw.println(stmt);
              pw.flush();
              }
           // Root end information
           stmt = imgName + ", ";
           stmt = stmt.concat(imgName + ", ");  // XD 20110629
           stmt = stmt.concat(r.getRootKey() + ", ");
           stmt = stmt.concat(r.getRootID() + ", ");
           stmt = stmt.concat("Length, ");
           stmt = stmt.concat(r.lPosPixelsToCm(r.getRootLength()) + ", ");
           stmt = stmt.concat("0.0, 0.0, ");
           stmt = stmt.concat(r.lastNode.x * pixelSize + ", ");
           stmt = stmt.concat(r.lastNode.y * pixelSize + ", ");
           stmt = stmt.concat(r.isChild() + ", ");
           stmt = stmt.concat(r.getPoAccession() + ", ");
           stmt = stmt.concat(imgName + "");
           pw.println(stmt);
           if(last) pw.flush();           
           }
       SR.write("CSV data transfer completed for 'Marks'.");     
   }

	    
	/**
	 * Send the root data to the ResulsTable rt
	 * @param rt
	 * @param name
	 */
   public void sendRootData(ResultsTable rt, String name){

      for (int i = 0; i < rootList.size(); i++) {
         Root r = (Root) rootList.get(i);
         if (!r.validate()) continue; // corrupted Root instance
         rt.incrementCounter();	
         rt.addValue("image",name);
         rt.addValue("root_name",r.getRootID());
         rt.addValue("root",r.getRootKey());
         rt.addValue("length",r.lPosPixelsToCm(r.getRootLength()));
         rt.addValue("surface",r.getRootSurface());
         rt.addValue("volume",r.getRootVolume());
         rt.addValue("convexhull_area",r.getConvexHullArea());
         rt.addValue("diameter",r.getAVGDiameter());
         rt.addValue("root_order",r.isChild());
         rt.addValue("root_ontology",r.getPoAccession());
         rt.addValue("parent_name",r.getParentName());
         if(r.getParent() != null) rt.addValue("parent",r.getParent().getRootKey());
         else rt.addValue("parent","-1");
         rt.addValue("insertion_position",r.lPosPixelsToCm(r.getDistanceFromBase()));
         rt.addValue("insertion_angle",r.getInsertAngl() * (180 / Math.PI));
         rt.addValue("n_child",r.childList.size());
         rt.addValue("child_density",r.getChildDensity());
         if(r.firstChild != null){
        	 rt.addValue("first_child",r.getFirstChild().getRootKey());
        	 rt.addValue("insertion_first_child",r.lPosPixelsToCm(r.getFirstChild().getDistanceFromBase()));
         }
         else{ 
        	 rt.addValue("first_child","null");
        	 rt.addValue("insertion_first_child","null");
         }
         if(r.lastChild != null){
        	 rt.addValue("last_child",r.getLastChild().getRootKey());
        	 rt.addValue("insertion_last_child",r.lPosPixelsToCm(r.getLastChild().getDistanceFromBase()));
         }
         else{ 
        	 rt.addValue("last_child","null");
        	 rt.addValue("insertion_last_child","null");
         }
      }
   }
 
   
   /**
    * Send the node data to the Result Table
    * @param rt
    * @param name
    */
   public void sendNodeData(ResultsTable rt, String name){
	   
       for (int i = 0; i < rootList.size(); i++) {
           Root r = (Root) rootList.get(i);
           if (!r.validate()) continue; // corrupted Root instance
           Node n = r.firstNode;
           do {
	  	         rt.incrementCounter();	
	  	         rt.addValue("image",name);
	  	         rt.addValue("root",r.getRootKey());
	  	         rt.addValue("root_name",r.getRootID());
	  	         rt.addValue("x",n.x * pixelSize);
	  	         rt.addValue("y",n.y * pixelSize);
	  	         rt.addValue("theta",n.theta);
	  	         rt.addValue("diameter",n.diameter * pixelSize);
	  	         rt.addValue("distance_from_base",n.cLength * pixelSize);
	  	         rt.addValue("distance_from_apex",(r.getRootLength() - n.cLength ) *pixelSize);
	  	         rt.addValue("root_order",r.isChild());
	  	         rt.addValue("root_ontology",r.getPoAccession());
              } while ((n = n.child) != null);
        }
	 }

   /**
    * Send the image data to the Result Table
    * @param rt
    * @param name
    */
   public void sendImageData(ResultsTable rt, String name){
	   
	   rt.incrementCounter();	
	   rt.addValue("image",name);
	   rt.addValue("tot_root_length",getTotalRLength());
	   rt.addValue("convexhull_area",getConvexHullArea());
	   // Primary roots
	   rt.addValue("n_primary",getNPRoot());
	   rt.addValue("tot_prim_length",getTotalPRLength());
	   rt.addValue("mean_prim_length",getAvgPRLength());
	   rt.addValue("mean_prim_diameter",getAvgPRDiam());
	   rt.addValue("mean_lat_density",getAvgChildDens());
	   // Secondary roots
	   rt.addValue("n_laterals",getNSRoot());
	   rt.addValue("tot_lat_length",getTotalSRLength());
	   rt.addValue("mean_lat_length",getAvgSRLength());
	   rt.addValue("mean_lat_diameter",getAvgSRDiam());	   
	 }
   
   /**
    * Get a given root in the root list
    * @param i
    * @return
    */
   public Root getRoot (int i) {
      if (i < getNRoot()) return (Root) rootList.get(i);
      else return null;
      }


   /**
    * Get the total number of roots
    * @return
    */
   public int getNRoot() {
      return rootList.size();
     }
      
 
   /**
    * Ge tthe DPI value for the image
    * @return
    */
   public float getDPI() {return dpi; }
   
   /**
    * Set the DPI avlue for the image
    * @param dpi
    */
   public void setDPI(float dpi) {
      this.dpi = dpi;
      pixelSize = (float) (2.54 / dpi);
      for (int i = 0; i < rootList.size(); i++) ((Root) rootList.get(i)).setDPI(dpi);
      }

   /**
    * Remove all the roots from the root list
    */
   public void clearDatafile() {
      rootList.clear(); 
      }


   /**
    * 
    */
   private void logReadError() {
      SR.write("An I/O error occured while attemping to read the datafile.");
      SR.write("A new empty datafile will be created.");
      SR.write("Backup versions of the datafile, if any, can be loaded");
      SR.write("using the File -> Use backup datafile menu item.");
      }

   
   
   /**
    * Read common datafile structure
    * @param f
    */
   public void readRSML(String f) {

	   // Choose the datafile
	   String fPath = f;

	   if(f == null){
		   	clearDatafile();
	   		JFileChooser fc = new JFileChooser(new File(directory));
	   		fc.setFileFilter(datafileFilterRSML);
	   		if (fc.showDialog(null, "Select Root System Markup Datafile") == JFileChooser.CANCEL_OPTION) return;	 	
	   		fPath = fc.getSelectedFile().getAbsolutePath();
	   }	   
	
	   nextAutoRootID = 0;
	         
	   
	   org.w3c.dom.Document documentDOM = null;
	   DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();

	   try {
		   DocumentBuilder builder = factory.newDocumentBuilder();
		   documentDOM = builder.parse(new File(fPath) );
	   }
	   catch (SAXException sxe) {
		   logReadError();
		   return;
	   }
	   catch (ParserConfigurationException pce) {
		   logReadError();
		   return;
	   }
	   catch (IOException ioe) {
		   logReadError();
		   return;
	   }

	   documentDOM.normalize();
	      
	   org.w3c.dom.Node nodeDOM = documentDOM.getFirstChild();
	      	   
	   if (!nodeDOM.getNodeName().equals("rsml")) {
		   logReadError();
		   return;
	   }	
	   
	   String origin = "smartroot";
	   // Navigate the whole document
	   nodeDOM = nodeDOM.getFirstChild();
	   while (nodeDOM != null) {
		   
		   String nName = nodeDOM.getNodeName();
		   
		   // Get and process the metadata
		   if(nName.equals("metadata")){
			   org.w3c.dom.Node nodeMeta = nodeDOM.getFirstChild();
			   String unit = "cm";
			   float res = 1.0f;			   
			   while (nodeMeta != null) {		   
				   	String metaName = nodeMeta.getNodeName();				   	
				   	// Get the image resolution
				   	if(metaName.equals("unit")) unit = nodeMeta.getFirstChild().getNodeValue();	         		         
				   	if(metaName.equals("resolution")) res = Float.valueOf(nodeMeta.getFirstChild().getNodeValue());
				   	if(metaName.equals("file-key")) datafileKey = nodeMeta.getFirstChild().getNodeValue();
				   	if(metaName.equals("software")) origin = nodeMeta.getFirstChild().getNodeValue(); 	
					nodeMeta = nodeMeta.getNextSibling();
			   }
			   dpi = getDPI(unit, res);
			   pixelSize = 2.54f / dpi;
		   }
		         
		   // Get the plant
		   if(nName.equals("scene")){
			   org.w3c.dom.Node nodeScene = nodeDOM.getFirstChild();
			   while (nodeScene != null) {		   
				   	String sceneName = nodeScene.getNodeName();
				   	
				   if(sceneName.equals("plant")){
					   org.w3c.dom.Node nodeRoot = nodeScene.getFirstChild();
					   while (nodeRoot != null) {
						   String rootName = nodeRoot.getNodeName();
				   
						   // Get the Roots
						   if(rootName.equals("root")){
							  new Root(dpi, nodeRoot, true, null, this, origin);
						   }
						   nodeRoot = nodeRoot.getNextSibling();
					   }
				  }
				   nodeScene = nodeScene.getNextSibling();  
			   }	 
		   }
		   nodeDOM = nodeDOM.getNextSibling();  
	   }
	   SR.write(rootList.size()+" root(s) were created");
	   setDPI(dpi);
   	}
	   
   
   /**
    * Ge the directory containing the image
    * @return
    */
   public String getDirectory () { return directory; }
 

	/** Get the closest root from the base of a given root 
	 * @param r the root from which we want the closest root
	 * @return the closest root from the apex of the root r*/
	
	public Root getClosestRoot(Root r){
		Node n = r.firstNode;
		int ls = rootList.size();
		if (ls == 1) return null;
		Root rp;
		Root rpFinal = null;
		float dist;
		float distMin = 1000000.0f;
		
		for (int i = 0; i < ls; i++){
			rp =(Root) rootList.get(i);
			if(rp.getRootKey() == r.getRootKey()) continue;
			Node np = rp.firstNode;
			dist = (float) Point2D.distance((double) n.x, (double) n.y, (double) np.x, (double) np.y);
			if (dist < distMin){
				distMin = dist;
				rpFinal = rp;
			}
			while (np.child != null){
				np = np.child;
				dist = (float) Point2D.distance((double) n.x, (double) n.y, (double) np.x, (double) np.y);
				if (dist < distMin){
					distMin = dist;
					rpFinal = rp;
				}
			}
		}
		return rpFinal;
	}
	
	/**
	 * Attach c to p
	 * @param p the parent root
	 * @param c the child root
	 */
	public void setParent(Root p, Root c){
		c.attachParent(p);
		p.attachChild(c);
	}
	
	/**
	 * Get the number of primary roots
	 * @return the number of primary roots
	 */
	public int getNPRoot(){
		int n = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() == 0) n++;
		}
		return n;
	}
	
	/**
	 * Get the number of secondary roots
	 * @return the number of secondary roots
	 */
	public int getNSRoot(){
		int n = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() !=0) n++;
		}
		return n;
	}
	
	/**
	 * Get the average length of secondary roots
	 * @return the average length of secondary roots
	 */
	public float getAvgSRLength(){
		float n = 0;
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() !=0) {
				n += r.getRootLength();
				m++;
			}
		}
		return n/m * pixelSize;
	}
	
	/**
	 * Get average length of primary roots
	 * @return the average length of primary roots
	 */
	public float getAvgPRLength(){
		float n = 0;
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() == 0 ) {
				n += r.getRootLength();
				m++;
			}
		}
		return n/m * pixelSize;
	}
	
	/**
	 * Get the total root length
	 * @return the totla root length
	 */
	public float getTotalRLength(){
		float n = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			n += r.getRootLength();
		}
		return n * pixelSize;		
		
	}
	
	/**
	 * Get the average length of all roots
	 * @return the average length of all roots
	 */
	public float getAvgRLength(){
		float n = 0;
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			n += r.getRootLength();
			m++;
		}
		return n/m * pixelSize;
	}
	
	/**
	 * Get the average diameter of secondary roots
	 * @return the average diameter of secondary roots
	 */
	public float getAvgSRDiam(){
		float n = 0;
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() != 0) {
				Node node = r.firstNode;
				n += node.diameter;
				m++;
				while (node.child != null){
					node = node.child;
					n += node.diameter;
					m++;
				}
			}
		}
		return n/m * pixelSize;
	}
	
	
	/**
	 * Get the average insertion angle of secondary roots
	 * @return the average insertion angle of secondary roots
	 */
	public float getAvgSRInsAng(){
		float n = 0;
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() !=0 ) {
				n += r.getInsertAngl() * (180 / Math.PI);
				m++;
			}
		}
		return n/m ;
	}
	
	
	/**
	 * Get the total length of the primary roots
	 * @return the total length of the primary roots
	 */
	public float getTotalPRLength(){
		int l = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if(r.isChild() == 0){
				l += r.lPosPixelsToCm(r.getRootLength());
			}
		}
		return l;
	}
	
	/**
	 * Get the total lenght of the lateral roots
	 * @return the total lenght of the lateral roots
	 */
	public float getTotalSRLength(){
		int l = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if(r.isChild() > 0){
				l += r.lPosPixelsToCm(r.getRootLength());
			}
		}
		return l;
	}
	
	/**
	 * Get the average diameter of primary roots
	 * @return the average diameter of primary roots
	 */
	public float getAvgPRDiam(){
		float n = 0;
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() == 0) {
				Node node = r.firstNode;
				n += node.diameter;
				m++;
				while (node.child != null){
					node = node.child;
					n += node.diameter;
					m++;
				}
			}
		}
		return n / m * pixelSize;
	}
	
	/**
	 * Get average interbranch distance
	 * @return the average interbranch distance
	 */
	public float getAvgInterBranch(){
		float iB = 0;
		Root r;
		int n = 0;
		for(int i = 0 ; i < rootList.size() ; i++){
			r = (Root) rootList.get(i);
			if(r.getInterBranch() != 0){
				iB += r.getInterBranch();
				n++;
			}
		}
		return (iB / n) * pixelSize;
	}

	/**
	 * Get the number of nodes of the primary roots
	 * @return the number of nodes of the primary roots
	 */
	public int getNPNode(){
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() == 0) {
				Node node = r.firstNode;
				m++;
				while (node.child != null){
					node = node.child;
					m++;
				}
			}
		}
		return m;
	}
	
	/**
	 * Get the number of node of the secondary roots
	 * @return the number of node of the secondary roots
	 */
	
	public int getNSNode(){
		int m = 0;
		Root r;
		for(int i =0 ; i < rootList.size() ; i++){
			r =  (Root) rootList.get(i);
			if (r.isChild() != 0) {
				Node node = r.firstNode;
				m++;
				while (node.child != null){
					node = node.child;
					m++;
				}
			}
		}
		return m;
	}
	
	
	/**
	 * Get a list of strings containing all the name of roots having children
	 * @return a list of strings containing all the name of roots having children
	 */
	public String[] getParentRootNameList(){
		int ind = 0;
		int c = 0;
		Root r;
		for (int i = 0 ; i < rootList.size(); i++){
			r = (Root) rootList.get(i);
			if(r.childList.size() != 0){
				ind ++;
			}
		}	
		String[] n = new String[ind];
		for (int i = 0 ; i < rootList.size(); i++){
			r = (Root) rootList.get(i);
			if(r.childList.size() != 0){
				n[i-c] = r.getRootID();
			}
			else c++;
		}	
		return n;
	}
	
	
	/**
	 * Get a list of strings containing all the name of primary
	 * @return a list of strings containing all the name of primary
	 */
	public String[] getPrimaryRootNameList(){
		int ind = 0;
		int c = 0;
		Root r;
		for (int i = 0 ; i < rootList.size(); i++){
			r = (Root) rootList.get(i);
			if(r.isChild() == 0){
				ind ++;
			}
		}	
		String[] n = new String[ind];
		for (int i = 0 ; i < rootList.size(); i++){
			r = (Root) rootList.get(i);
			if(r.isChild() == 0){
				n[i-c] = r.getRootID();
			}
			else c++;
		}	
		return n;
	}
	
	/**
	 * Get the average child density of all the parent roots of the image
	 * @return the average child density of all the parent roots of the image
	 */
	public float getAvgChildDens(){
		float cd = 0;
		int n = 0;
		Root r;
		for (int i = 0 ; i < rootList.size(); i++){
			r = (Root) rootList.get(i);
			if(r.getChildDensity() != 0){
				cd += r.getChildDensity();
				n++;
			}
		}
		return cd / n;
	}
	
	/**
	 * Return the image name
	 */
    public String toString(){
    	return this.imgName;
    }


    /**
     * Get the center of the tracing
     * @return
     */
    public float[] getCenter(){
    	float[] coord = new float[2];
    	
    	// Get x
    	float min = 1e5f, max = 0; 
    	Root r;
    	Node n;
    	for(int i = 0; i < rootList.size(); i++){
    		r = rootList.get(i);
			n = r.firstNode;
			while(n.child != null){
				if(n.x < min) min = n.x;
				if(n.x > max) max = n.x;
				n = n.child;
			}
    	}
    	coord[0] = min + ((max-min)/2);
    	
    	
    	// Get y
    	min = 1e5f;
    	max = 0; 
    	for(int i = 0; i < rootList.size(); i++){
    		r = rootList.get(i);
			n = r.firstNode;
			while(n.child != null){
				if(n.y < min) min = n.y;
				if(n.y > max) max = n.y;
				n = n.child;
			}
    	}
    	coord[1] = min + ((max-min)/2);

    	
    	
    	return coord;
    }
    
    
    /**
     * Get the widht of the tracing
     * @return
     */
    public int getWidth(){
    	float min = 1e5f, max = 0; 
    	Root r;
    	Node n;
    	for(int i = 0; i < rootList.size(); i++){
    		r = rootList.get(i);
			n = r.firstNode;
			while(n.child != null){
				if(n.x < min) min = n.x;
				if(n.x > max) max = n.x;
				n = n.child;
			}
    	}
    	return (int)(max+min);
    }
    
    /**
     * Get the height of the tracing
     * @return
     */
    public int getHeight(){
    	float min = 1e5f, max = 0; 
    	Root r;
    	Node n;
    	for(int i = 0; i < rootList.size(); i++){
    		r = rootList.get(i);
			n = r.firstNode;
			while(n.child != null){
				if(n.y < min) min = n.y;
				if(n.y > max) max = n.y;
				n = n.child;
			}
    	}
    	return (int)(max+min);
    }

  
    /**
     * Create an image processor based on the roots contained into the root system
     * @param color
     * @param line
     * @param real
     * @param w
     * @param h
     * @param convexhull
     * @return
     */
    public ImageProcessor createImage(boolean color, int line, boolean real, int w, int h, boolean convexhull){
    	
    	Root r;
    	Node n, n1;
    	ImagePlus tracing;

    	
    	if(color) tracing = IJ.createImage("tracing", "RGB", w, h, 1);
    	else tracing = IJ.createImage("tracing", "8-bit", w, h, 1);
  
        	
    	ImageProcessor tracingP = tracing.getProcessor();    	
    	
	    //if(name == null) fit.checkImageProcessor();
    	for(int i = 0; i < rootList.size(); i++){
			r =  (Root) rootList.get(i);
			n = r.firstNode;
			
			if(color){
				switch(r.isChild()){
					case 0: tracing.setColor(Color.orange); break;
					case 1: tracing.setColor(Color.green); break;
					case 2: tracing.setColor(Color.yellow); break;
				}
			}
			else tracing.setColor(Color.black);
			
			while(n.child != null){
				n1 = n;
				n = n.child;
				if(real) tracingP.setLineWidth((int) n.diameter);
				else tracingP.setLineWidth(line);
		    	tracingP.drawLine((int) n1.x, (int) n1.y, (int) n.x, (int) n.y);
			}
			tracing.setProcessor(tracingP);
			if(convexhull){
				if(r.isChild() == 0){
					tracing.setColor(Color.red);
					PolygonRoi ch = r.getConvexHull();
		    		int[] xRoi = ch.getXCoordinates();
		    		int[] yRoi = ch.getYCoordinates();
		    		Rectangle rect = ch.getBounds();		
		    		for(int j = 1 ; j < xRoi.length; j++){
		    			tracingP.drawLine(xRoi[j-1]+rect.x, yRoi[j-1]+rect.y, xRoi[j]+rect.x, yRoi[j]+rect.y);
		    		}
	    			tracingP.drawLine(xRoi[xRoi.length-1]+rect.x, yRoi[xRoi.length-1]+rect.y, xRoi[0]+rect.x, yRoi[0]+rect.y);
				}
			}
			tracingP = tracing.getProcessor();
    	}
    	
    	return tracingP;
    }
    

    /**
     * Get the index of the po accession
     * @param po
     * @return
     */
    public int getIndexFromPo(String po){
    	for(int i = 0; i < SR.listPo.length; i++){
    		if(po.equals(SR.listPo[i])) return i;
    	}
    	return 0;
    }
    
    /**
     * Get the convexhull area of all the roots in the image
     * @return
     */
    public float getConvexHullArea(){
    	return 0;
    }
    /**
     * Get the convexhull of all the roots in the image. Uses the native image functions
     * @return
     */
    public PolygonRoi getConvexHull(){
    		
    	List<Integer> xList = new ArrayList<Integer>(); 
    	List<Integer> yList = new ArrayList<Integer>();
    	
    	// Add all the nodes coordinates
    	for(int i = 0; i < rootList.size(); i++){
    		Root r = rootList.get(i);
    		Node n = r.firstNode;
    		while (n.child != null){
    			xList.add((int) n.x);
    			yList.add((int) n.y);
    			n = n.child;
    		}
    		xList.add((int) n.x);
    		yList.add((int) n.y);
    	}
    	
    	int[] xRoiNew = new int[xList.size()];
    	int[] yRoiNew = new int[yList.size()];
    	for(int l = 0; l < yList.size(); l++){
    		xRoiNew[l] = xList.get(l);
    		yRoiNew[l] = yList.get(l);
    	}
    	
    	Roi roi = new PolygonRoi(xRoiNew, yRoiNew, yRoiNew.length, Roi.POLYGON);
    	return new PolygonRoi(roi.getConvexHull(),  Roi.POLYGON);
    }    
}

