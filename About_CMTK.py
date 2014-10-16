from ij.gui import GenericDialog

from java.lang.System import getProperty
sys.path.append(getProperty("fiji.dir") + "/plugins/CMTK_Registration")
import cmtkgui

gd = GenericDialog('About CMTK')
gd.addMessage('CMTK Registration suite is open source software released under GPLv3',)
gd.addMessage('Currently installed CMTK version: '+cmtkgui.installed_version())
gd.addMessage('CMTK binary directory: '+cmtkgui.bin_dir())
gd.setCancelLabel("CMTK Web Page")
gd.showDialog()
if gd.wasCanceled():
	BrowserLauncher().run("http://www.nitrc.org/projects/cmtk/")