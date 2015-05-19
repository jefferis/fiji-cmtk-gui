from fiji.util.gui import GenericDialogPlus
from java.awt.event import TextListener
from java.awt.event import ItemListener
from java.awt import Font
from java.awt import Color
from java.lang import Runtime

import os,subprocess,sys

from java.lang.System import getProperty
sys.path.append(getProperty("fiji.dir") + "/plugins/CMTK_Registration")

from cmtkgui import relpath,makescript,findExecutable
import cmtkgui

# helper classes/functions for main generic dialog

class RegRootListener(TextListener):
	def textValueChanged(self, tvc):
		regroot = regrootf.getText()
		if len(regroot)==0:
			statusf.setText('')
			return
		if os.path.exists(regroot):
			regrootf.setForeground(Color.black)
			updateOuputFolders()
		else:
			regrootf.setForeground(Color.red)
			statusf.setText('Please choose valid root directory')
			statusf.setForeground(Color.red)
			return
		# check if we already have a sensible images dir - if not, then set
		imgdir = imgdirf.getText()
		if len(imgdir)==0 or not os.path.exists(imgdir):
			imgdir = os.path.join(regroot,'images')
			imgdirf.setText(imgdir)
		else:
			statusf.setText('')

class ImageDirListener(TextListener):
	def textValueChanged(self, tvc):
		imgdir = imgdirf.getText()
		# no comment if unset
		if len(imgdir)==0:
			statusf.setText('')
			return
		# no comment if unset
		if os.path.exists(imgdir):
			statusf.setText('')
			imgdirf.setForeground(Color.black)
			regroot = regrootf.getText()
			if len(regroot)==0 or not os.path.exists(regroot):
				regrootf.setText(os.path.dirname(imgdir))
		else:
			imgdirf.setForeground(Color.red)
			statusf.setText('Please choose valid images directory')
			statusf.setForeground(Color.red)

class OuputSuffixListener(TextListener):
	def textValueChanged(self, tvc):
		updateOuputFolders()

class RegParamListener(ItemListener):
	def itemStateChanged(self, isc):
		regparamc=choicef.getSelectedItem()
		regparams=''
		if regparamc == 'Cachero, Ostrovsky 2010':
			regparams = "-X 26 -C 8 -G 80 -R 4 -A '--accuracy 0.4' -W '--accuracy 0.4'"
		regparamf.setText(regparams)
		print "Chosen reg params: "+regparamc

def updateOuputFolders():
	outsuffix=outsuffixf.getText()
	if outsuffix:
		reg="Registration."+outsuffix
		ref="reformatted."+outsuffix
	else:
		reg="Registration"
		ref="reformatted"
	outputf.setText("Output Folders: "+reg+", "+ref)
	return

## START!
try:
	gd = GenericDialogPlus('CMTK Registration GUI')

	# 0.1) Identify path to CMTK binaries
	bindir=cmtkgui.install_dir()
	print 'bindir is ' + bindir
	# 0.1) Identify path to munger.pl script
	#munger='/Users/jefferis/bin/munger.pl'
	munger=cmtkgui.tool_path('munger')
	print 'munger is ' + munger
	gd.addHelp("http://flybrain.mrc-lmb.cam.ac.uk/dokuwiki/doku.php?id=warping_manual:registration_gui")

	dirFieldWidth=50
	gdMargin=130
	gd.addDirectoryField("Registration Folder",None,dirFieldWidth)
	regrootf = gd.getStringFields().get(0)
	# reference brain
	gd.addFileField("Reference Brain", "",dirFieldWidth)
	# input directory/image
	gd.addDirectoryOrFileField("Input Image or Image Directory",None,dirFieldWidth)
	imgdirf = gd.getStringFields().get(2)

	gd.setInsets(10,gdMargin,10)
	gd.addMessage("Output folders:")
	outputf=gd.getMessage()

	# what to do: affine/warp/reformat
	gd.setInsets(10,200,10)
	gd.addCheckboxGroup(3,2,["affine","01","warp","02","reformat","03"],[True,True,True,True,True,True],["Registration Actions","Reformat Channels"])
	#gd.addCheckboxGroup(1,3,["01","02","03"],[True,True,True],["Reformat Channels"])

	# Registration options 
	# Jefferis,Potter 2007, Cachero,Ostrovsky 2010, Manual
	gd.addChoice("Registration Params",["Jefferis, Potter 2007","Cachero, Ostrovsky 2010"],"Jefferis, Potter 2007")
	choicef=gd.getChoices().get(0)
	print choicef.getSelectedItem()

	# final Action (Test, Run, Write Script)
	gd.addChoice("Action",["Test","Write Script","Run (Experimental)"],"Write Script")
	font=Font("SansSerif",Font.BOLD,12)

	# Advanced options
	gd.setInsets(25,100,10)
	gd.addMessage("Advanced Options:",font)
	advancedoptionsf=gd.getMessage()

	ncores=Runtime.getRuntime().availableProcessors()
	defaultCores=1
	if ncores >=8:
	    defaultCores=4
	elif ncores>=4:
	    defaultCores=2
	gd.addSlider("Number of cpu cores to use",1,ncores,defaultCores)

	gd.setInsets(0,230,10)
	gd.addCheckbox("Verbose log messages",False)

	gd.addStringField("Output folder suffix","",20)
	outsuffixf = gd.getStringFields().get(3)

	gd.addStringField("(Further) Registration Params","",50);
	regparamf = gd.getStringFields().get(4)
	gd.addStringField("Additional Arguments to munger.pl","",50);

	regrootf.addTextListener(RegRootListener())
	imgdirf.addTextListener(ImageDirListener())
	outsuffixf.addTextListener(OuputSuffixListener())
	choicef.addItemListener(RegParamListener())
	# used for errors etc
	gd.addMessage("Start by choosing a registration directory or images directory!")
	statusf=gd.getMessage()
	gd.showDialog()
	if gd.wasCanceled():
		sys.exit("User cancelled!")
	# Process Dialog Choices
	rootDir=gd.getNextString()
	os.chdir(rootDir)
	refBrain=gd.getNextString()
	image=gd.getNextString()
	image=relpath(image,rootDir)
	print refBrain
	refBrain=relpath(refBrain,rootDir)
	print refBrain

	affine=gd.getNextBoolean()
	ch01=gd.getNextBoolean()
	warp=gd.getNextBoolean()
	ch02=gd.getNextBoolean()
	reformat=gd.getNextBoolean()
	ch03=gd.getNextBoolean()
	munger_actions=""
	if affine:
		munger_actions+="-a "
	if warp:
		munger_actions+="-w "
	if reformat:
		channels=''
		if ch01:
			channels+='01'
		if ch02:
			channels+='02'
		if ch03:
			channels+='03'
		if channels != '':
			munger_actions+="-r "+channels+" "

	verbose=gd.getNextBoolean()
	corestouse=gd.getNextNumber()
	outsuffix=gd.getNextString()
	regparams=gd.getNextChoice()
	print regparams
	regparams=gd.getNextString()
	mungeropts=gd.getNextString()
	action=gd.getNextChoice()

	if action == 'Test': mungeropts+=' -t'
	if verbose: mungeropts+=' -v'
	mungeropts+=' -T %d' % (int(corestouse))

	if not outsuffix == '':
		mungeropts += ' -d .'+outsuffix

	cmd='"%s" -b "%s" %s %s %s -s "%s" %s' % (munger,bindir,munger_actions,regparams,mungeropts,refBrain,image)
	print cmd

	if action !='Test':
		# make a script
		script=makescript(cmd,rootDir,outdir=os.path.join(rootDir,'commands'))
		print 'script is %s' % (script)
	
		if action != 'Write Script':
			# Actually run the script
			subprocess.call(script,shell=False)
except SystemExit, e:
	from ij import IJ
	IJ.showStatus(str(e))
