from ij.gui import GenericDialog

import sys
from java.lang.System import getProperty
sys.path.append(getProperty("fiji.dir") + "/plugins/CMTK_Registration")

gd = GenericDialog('About CMTK')
gd.addMessage('CMTK Registration suite is open source software released under GPLv3',)
gd.addMessage('Currently installed CMTK version: '+cmtkgui.installed_version())
gd.addMessage('CMTK binary directory: '+cmtkgui.bin_dir())
gd.setCancelLabel("CMTK Web Page")
gd.showDialog()
if gd.wasCanceled():
	from ij import IJ
	IJ.runPlugIn("ij.plugin.BrowserLauncher", "http://www.nitrc.org/projects/cmtk/")
