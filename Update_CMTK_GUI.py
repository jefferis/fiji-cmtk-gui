'''
Update CMTK GUI wrapper code (but not core cmtk software)
'''

import urllib2,os,sys,tarfile,shutil,tempfile

from fiji.util.gui import GenericDialogPlus

import cmtkgui

def untar_github_archive(f,target_dir):
	'''
	untar all files in a github tarfile to target_dir
	target_dir is created if it does not already exist
	Uses an intermediate temporary directory and copies only the source
	code folder not the github pax_global_header file
	'''
	tar=tarfile.open(f)
	print("Extracting tar file")
	td=tempfile.mkdtemp()
	try:
		tar.extractall(path=td)
		subdir=None
		for f in os.listdir(td):
			p=os.path.join(td,f)
			if os.path.isdir(p):
				subdir=p
				break
		if subdir is None:
			raise Exception("Could not find a subdirectory in tar file")
	except Exception, e:
		# restore previous state
		shutil.rmtree(td)
		myErr("Trouble extracting downloaded file. Install aborted!")
	
	if os.path.exists(target_dir):
		shutil.rmtree(target_dir)
	
	shutil.move(os.path.join(td,subdir),target_dir)


download_url='https://github.com/jefferis/fiji-cmtk-gui/tarball/master'
# check date
installed_version='NA'
local_version_info=cmtkgui.gui_local_versioninfo()
if local_version_info.has_key('date'):
	installed_version=local_version_info['date']
github_version_info=cmtkgui.gui_github_versioninfo()
update_available=cmtkgui.gui_update_available(github_version_info)

gd = GenericDialogPlus('Update CMTK GUI')
if update_available:
	gd.addMessage('CMTK GUI update available')
	gd.setOKLabel("Download")
else:
	gd.addMessage('CMTK GUI is up to date')

gd.addMessage('Currently installed CMTK GUI version: '+installed_version)

gd.showDialog()
if gd.wasOKed():
	# nb url has a suffix to indicate that user agreed to license
	print 'Downloading url '+download_url+' to '+cmtkgui.gui_install_dir()
	cmtkgui.download_and_untar_url(download_url,cmtkgui.gui_install_dir(),untar_github_archive)
	cmtkgui.gui_write_local_versioninfo(github_version_info)
