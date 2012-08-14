'''
Download appropriate CMTK binary archive and install to fiji bin/cmtk directory
'''

import urllib2,os,sys,tempfile,tarfile,shutil

from fiji.util.gui import GenericDialogPlus

import cmtkgui

def download_and_untar_url(download_url,download_file,target_dir):
	'''
	download file in temporary location
	untar to target_dir
	clean up download
	'''
	tf=tempfile.NamedTemporaryFile(suffix=download_file)
	print 'Downloading '+download_url+' to '+ tf.name
	u = urllib2.urlopen(download_url)
	headers = u.info()
	download_size = int(headers['Content-Length'])
	print "Download size should be %d" % (download_size)
	block_size=100000
	bytes_read=0
	while bytes_read<download_size:
		IJ.showStatus("Downloading CMTK binaries (%.1f/%.1f Mb)" % 
			((bytes_read/1000000.0),(download_size/1000000.0)))
		IJ.showProgress(bytes_read,download_size)
		tf.file.write(u.read(block_size))
		bytes_read+=block_size
	IJ.showProgress(1.0)
	u.close()
	tf.file.close()
	print ('Downloaded file has size %d')%(os.path.getsize(tf.name))
	IJ.showStatus("Extracting tar file and installing CMTK")
	untar_binaries(tf.name,target_dir)
	IJ.showStatus('Cleaning up!')
	tf.close()

def bin_files(members):
	'''
	Quick utility function to select binary files to install from CMTK Archive.
	'''
	for tarinfo in members:
		lastdir=os.path.basename(os.path.dirname(tarinfo.name))
		if lastdir == "bin":
#			print 'keeping '+tarinfo.name
			yield tarinfo

def license_files(members):
	'''
	Quick utility function to select license files to install from CMTK Archive.
	Do this by copying files from doc 
	'''
	for tarinfo in members:
		if re.search(os.path.join(os.path.sep,"doc",""),tarinfo.name):
			yield tarinfo

def untar_binaries(f,target_dir):
	'''
	untar binary files in a subfolder bin of tarfile f
	moving them from a temporay location to a final location in target_dir
	target_dir is created if it does not already exist
	'''
	tar=tarfile.open(f)
	td=tempfile.mkdtemp()
	print("Extracting tar file")
	tar.extractall(path=td,members=bin_files(tar))
	# now move each binary to where we actually wanted it to go
	binaries=bin_files(tar)
	print("Installing binaries to "+target_dir)
	if not os.path.isdir(target_dir):
		os.makedirs(target_dir)
	for binary in binaries:
		frompath = os.path.join(td,binary.name)
#		print 'from = '+frompath
		shutil.move(frompath,target_dir)
	print("Cleaning up!")
	shutil.rmtree(td)

download_urls=cmtkgui.downloads()
# download_urls=['http://www.nitrc.org/frs/download.php/4814/CMTK-2.2.3-CYGWIN-i686.tar.gz', 'http://www.nitrc.org/frs/download.php/4812/CMTK-2.2.3-Linux-x86_64.tar.gz', 'http://www.nitrc.org/frs/download.php/4820/CMTK-2.2.3-MacOSX-10.4-i686.tar.gz', 'http://www.nitrc.org/frs/download.php/4822/CMTK-2.2.3-MacOSX-10.5-x86_64.tar.gz', 'http://www.nitrc.org/frs/download.php/4824/CMTK-2.2.3-MacOSX-10.6-x86_64.tar.gz', 'http://www.nitrc.org/frs/download.php/4604/CMTK-2.2.1-CYGWIN-i686.tar.gz', 'http://www.nitrc.org/frs/download.php/4596/CMTK-2.2.1-Linux-x86_64.tar.gz', 'http://www.nitrc.org/frs/download.php/4608/CMTK-2.2.1-MacOSX-10.4-i686.tar.gz', 'http://www.nitrc.org/frs/download.php/4610/CMTK-2.2.1-MacOSX-10.5-x86_64.tar.gz', 'http://www.nitrc.org/frs/download.php/4611/CMTK-2.2.1-MacOSX-10.6-x86_64.tar.gz']
download_files=map(os.path.basename,download_urls)
download_dict=dict(zip(download_files,download_urls))
print cmtkgui.install_dir()

gd = GenericDialogPlus('Install CMTK')
gd.addMessage('Currently installed CMTK version: '+cmtkgui.installed_version())
recommended_file=cmtkgui.recommended_file(download_files)
if recommended_file is None:
	recommended_file = download_files[0]
gd.addChoice("Download file",download_files,recommended_file)
gd.addMessage('By downloading this file you agree to the following (if you '+
	'do not agree to this, please press "Cancel" below):')
gd.addMessage('Core CMTK code is licensed under the GPLv3.\nBundled software'+
	' may be licensed under different terms - see licences/ directory for details')
gd.showDialog()
if gd.wasOKed():
	download_file=gd.getNextChoice()
	# nb url has a suffix to indicate that user agreed to license
	download_url=download_dict[download_file]+'/?i_agree=1&download_now=1'
	print "Downloading "+download_file+' from url '+download_url+' to '+cmtkgui.install_dir()
	download_and_untar_url(download_url,download_file,cmtkgui.install_dir())
	#untar_binaries('/Users/jefferis/test.tar.gz',cmtkgui.install_dir())