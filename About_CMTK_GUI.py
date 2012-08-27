from ij.gui import GenericDialog
import cmtkgui

gd = GenericDialog('About CMTK GUI')
gd.addMessage('CMTK GUI is open source software released under GPLv3',)
gd.setCancelLabel("CMTK GUI Web Page")
gd.showDialog()
if gd.wasCanceled():
	BrowserLauncher().run("https://github.com/jefferis/fiji-cmtk-gui")