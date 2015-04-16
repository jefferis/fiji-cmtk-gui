from ij.gui import GenericDialog

import sys
from java.lang.System import getProperty
sys.path.append(getProperty("fiji.dir") + "/plugins/CMTK_Registration")
import cmtkgui

gd = GenericDialog('About CMTK GUI')
gd.addMessage('CMTK GUI is open source software released under GPLv3')
gd.addMessage('CMTK GUI is independently developed by Greg Jefferis and is NOT supported by CMTK team')
gd.setCancelLabel("CMTK GUI Web Page")
gd.showDialog()
if gd.wasCanceled():
	from ij import IJ
	IJ.runPlugIn("ij.plugin.BrowserLauncher", "https://github.com/jefferis/fiji-cmtk-gui")
