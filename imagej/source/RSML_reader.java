
/**
 * @author Xavier Draye - Université catholique de Louvain
 * @author Guillaume Lobet - Université de Liège
 *   
 * Main class for the RSML improter
 */

import java.awt.*;
import ij.*;
import ij.plugin.frame.PlugInFrame;

public class RSML_reader extends PlugInFrame {

	private static final long serialVersionUID = 1L;
	public static SR sr;
	public static RSMLGUI rsmlGui;
	private static RSML_reader instance;

	/**
	 * Constructor
	 */
	public RSML_reader() {
      super("RSML Reader");

      if (instance != null) {
         IJ.error("RSML Reader is already running");
         return;
         }
         
      (sr = new SR()).initialize();
      rsmlGui = new RSMLGUI();      
      }

   /**
    * Close the window
    */
   public void dispose() {
      Rectangle r = getBounds();
      SR.prefs.putInt("Explorer.Location.X", r.x);
      SR.prefs.putInt("Explorer.Location.Y", r.y);
      SR.prefs.putInt("Explorer.Location.Width", r.width);
      SR.prefs.putInt("Explorer.Location.Height", r.height);
      rsmlGui.dispose();
      instance = null;
      super.dispose();
      }

   /**
    * Get instance
    * @return
    */
   public static RSML_reader getInstance() {return instance; }

   
   /**
    * Main class
    * @param args
    */
   @SuppressWarnings("unused")
public static void main(String args[]) {
      ImageJ ij = new ImageJ();
      RSML_reader ie = new RSML_reader();
      }
   }

