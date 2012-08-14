'''Display help for any CMTK tool'''
from ij.gui import GenericDialog
from java.awt.event import ItemListener
import cmtkgui
import os

class ToolListener(ItemListener):
	def itemStateChanged(self, isc):
		toolc=choicef.getSelectedItem()
		helptext=cmtkgui.run_tool_stdout(toolc,'--help')
		print helptext
		ta.setText(helptext)


gd = GenericDialog('Help for CMTK Tool')
tools=os.listdir(cmtkgui.bin_dir())
gd.addChoice('CMTK tool',tools,tools[0])
choicef=gd.getChoices().get(0)
choicef.addItemListener(ToolListener())

gd.addTextAreas('',None,50,80)
ta=gd.getTextArea1()
ta.setEditable(False)


gd.showDialog()
# gd.addMessage('Currently installed CMTK version: '+cmtkgui.installed_version())
