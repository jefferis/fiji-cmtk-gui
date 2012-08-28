'''
cmtkgui module containing helper functions for Fiji CMTK GUI
'''
import os, sys, time, csv
import subprocess, re, urllib2, tempfile

from ij.gui import GenericDialog
from ij import IJ
from java.lang import System

gui_tarball_url='https://github.com/jefferis/fiji-cmtk-gui/tarball/master'

def myExit(err):
	'''Placeholder until I figure out suitable way to break out of jython script'''
	if err==None:
		err=''
	sys.exit(err)

def myErr(err):
	IJ.error(err)
	myExit(err)

def findExecutable(execname,msg=''):
    '''
    @return full path to a command using the shell's which function
    '''
    execpath=subprocess.Popen(["which", execname], stdout=subprocess.PIPE).communicate()[0].rstrip()
    if execpath == '' :
        gd = GenericDialog(msg)
        if msg == '' :
            msg="Locate the directory containing program "+execname
        gd.addDirectoryField(msg, "")
        gd.showDialog()
        execdir = gd.getNextString()
        execpath = os.path.join(execdir,execname)
        if os.path.exists(execpath) :
            return execpath
        else :
            sys.exit('Unable to locate '+execname+' in directory '+execdir)
    else : return execpath

def relpath(path, basedir = os.curdir):
    ''' @return a relative path from basedir to (sub) path.
    
    basedir defaults to curdir
    Does not work with paths outside basedir
    This is superseded by a builtin in python >=2.6
    '''
    basedir = os.path.abspath(basedir)
    path = os.path.abspath(path)
    
    if basedir == path :
        return '.'
    if basedir in path :
    	# nb joining empty string appends terminal pathsep in platform independent way
        return path.replace(os.path.join(basedir,''),'')
    return (path)

def makescript(cmd,rootdir,outdir):
    '''
    Make a shell script file that can be used to rerun the warp action, using
    chmod to ensure that it is executable.
    
    On MacOS X the file suffix is command so that it can be double clicked in the Finder.
    '''
    if not os.path.exists(outdir): os.mkdir(outdir)
    mtime = time.strftime('%Y-%m-%d_%H.%M.%S')
    suffix='sh'
    osname=System.getProperty("os.name")
    if "OS X" in osname:
        suffix='command'
    filename= "munger_%s.%s" %(mtime,suffix)
    filepath=os.path.join(outdir,filename)
    f = open(filepath, 'w')
    f.write('#!/bin/sh\n# %s\ncd \"%s"\n%s' % (mtime, rootdir, cmd))
    f.close()
    os.chmod(filepath,0755)
    return filepath

def downloads():
	'''
	Fetch a list of available tar.gz downloads
	Exclude macports versions or 
	'''
	nitrc_url='http://www.nitrc.org'
	cmtk_dwld_url=nitrc_url+'/frs/?group_id=212'
	response = urllib2.urlopen(cmtk_dwld_url)
	html = response.readlines()

	urls=list()
	for line in html:
		match=re.search('href="(.*tar.gz)".*',line)
		if match is not None:
			badmatch=re.search('(-mp-|-MacPorts-|Source)',line)
			if badmatch == None:
				relpath=match.group(1)
				url=nitrc_url+relpath
				urls.append(url)
	if len(urls)==0:return None
	else: return urls

def os_string():
	'''
	Return a string indicating the current OS formatted according to CMTK filename conventions
	Linux
	MacOSX-10.4
	MacOSX-10.5
	MacOSX-10.6
	CYGWIN
	'''
	osname=System.getProperty("os.name")

	if osname.startswith('Windows'):
		return 'CYGWIN'
	elif osname.startswith('Linux'):
		return 'Linux'
	elif osname.startswith('Mac'):
		osversion=System.getProperty("os.version")
		match=re.match(r'10\.([0-9]+)(\.[0-9])*',osversion)
		if match==None:
			sys.exit('Unable to identify OS version: '+osversion)
		osmajor=match.group(1)
		iosmajor=int(osmajor)
		if iosmajor<4:
			myErr('Sorry CMTK requires MacOSX >=10.4')
		elif iosmajor>6:
			osmajor='6'
		return 'MacOSX-10.'+osmajor
	else:
		return None

def recommended_file(files):
	'''
	Pick the recommended download file based on current OS
	'''
	osname=os_string()
	if osname==None:
		return None
	for f in files:
		match=re.search(osname,f)
		if match:
			return f
	return None

def install_dir():
	'''return sensible location to install cmtk'''
	ijdir=IJ.getDirectory('imagej')
	return os.path.join(ijdir,'bin','cmtk')

def gui_install_dir():
	'''return sensible location to install CMTK GUI'''
	pluginsdir=IJ.getDirectory('plugins')
	return os.path.join(pluginsdir,'Scripts','Plugins','CMTK_Registration')

def bin_dir():
	'''
	Return path to cmtk binaries
	Currently the same as install dir
	'''
	return install_dir()

def tool_path(tool):
	'''path to a CMTK tool'''
	return os.path.join(bin_dir(),tool)

def installed_version():
	'''Return current version of CMTK installed in Fiji bin dir'''
	ver=run_tool_stdout('warpx','--version')
	if ver:
		return ver
	else: return ""

def run_tool_stdout(tool,args):
	'''Return stdout after running CMTK tool with args'''
	toolp=tool_path(tool)
	if not os.path.exists(toolp):
		return None
	arglist=[toolp]
	if isinstance(args,list):
		arglist+=args
	elif args is None:
		arglist+=['']
	else:
		arglist+=[args]
	return subprocess.Popen(arglist, stdout=subprocess.PIPE).communicate()[0].rstrip()

def nitrc_version():
	'''Check NITRC website to see what version is available'''
	match=re.search(r"CMTK-([0-9]+\.[0-9]+\.[0-9]+)",os.path.basename(downloads()[0]))
	if match:
		return match.group(1)
	else:
		return None

def parse_version_string(ver_string):
	'''
	Parse a CMTK version string into major,minor and patch numbers (integers)
	'''
	if ver_string is None:
		return None
	v=re.match(r"(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)",ver_string)
	if v:
		ver_list=(v.group('major'),v.group('minor'),v.group('patch'))
		return map(int,ver_list)
	else:
		return None

def update_available():
	'''
	Check if NITRC version is newer than current version.
	Assumes that NITRC version can never be older than current version.
	'''
	r=parse_version_string(nitrc_version())
	l=parse_version_string(installed_version())
	if r is None: return None
	if l is None: return True
	if l[0]<r[0]: return True
	elif l[1]<r[1]: return True
	elif l[2]<r[2]: return True
	else: return False

def gui_github_versioninfo():
	'''
	Create a dictionary containing version information for current
	github code
	'''
	try: u = urllib2.urlopen(gui_tarball_url)
	except IOError, e:
		myErr("Unable to read github repository")
	headers = u.info()
	date = headers['date']
	size = int(headers['Content-Length'])
	filename = re.sub(".*filename=","",headers['Content-Disposition'])
	u.close()
	abbrev_sha1 = re.sub(".*-([a-f0-9]+).tar.gz","\\1",filename)
	return {'abbrev_sha1':abbrev_sha1, 'filename':filename, 'date':date, 'size':size}

def gui_local_versioninfo():
	'''	
	Read a csv file containing the version information for current
	CMTK GUI code
	'''
	version_file = os.path.join(gui_install_dir(),"CMTKGUIVersion.csv")
	if not os.path.exists(version_file):
		return {}
	versioninfo = {}
	for key, val in csv.reader(open(version_file)):
		versioninfo[key] = val
	return(versioninfo)

def gui_write_local_versioninfo(versioninfo):
	'''
	Write a csv file containing the version information for current
	CMTK GUI code
	'''
	version_file = os.path.join(gui_install_dir(),"CMTKGUIVersion.csv")
	myfile = open(version_file, "w")
	
	w = csv.writer(myfile)
	for key, val in versioninfo.items():
		w.writerow([key, val])
	myfile.close()

def gui_update_available(github_versioninfo=None):
	'''
	Check if an update is available on github
	optionally using a cached copy of the versioninfo dictionary
	'''
	lvi=gui_local_versioninfo()
	if not lvi.has_key('abbrev_sha1'):
		return True
	if github_versioninfo is None:
		github_versioninfo=gui_github_versioninfo()
	if lvi['abbrev_sha1']==gvi['abbrev_sha1']:
		return(False)
	else:
		 return (False)

def download_and_untar_url(download_url,target_dir,untarfun,download_file=None,
	download_msg=None):
	'''
	download file in temporary location
	untar to target_dir using untarfun
	clean up download
	'''
	# open url and set up using header information
	u = urllib2.urlopen(download_url)
	headers = u.info()
	download_size = int(headers['Content-Length'])
	if download_file == None:
		if headers.has_key('Content-Disposition'):
			download_file = re.sub(".*filename=","",headers['Content-Disposition'])
		else:
			myErr("No filename specified for download and none in http header!")
	if download_msg==None:
		download_msg='Downloading: %s' % (download_file)
	tf=tempfile.NamedTemporaryFile(suffix=download_file)
	print 'Downloading '+download_url+' to '+ tf.name
	print "Download size should be %d" % (download_size)

	# Now for the download
	block_size=100000
	if download_size>block_size:
		bytes_read=0
		while bytes_read<download_size:
			IJ.showStatus("%s (%.1f/%.1f Mb)" % 
				(download_msg,(bytes_read/1000000.0),(download_size/1000000.0)))
			IJ.showProgress(bytes_read,download_size)
			tf.file.write(u.read(block_size))
			bytes_read+=block_size
		IJ.showProgress(1.0)
	else:
		tf.file.write(u.read())
	u.close()
	tf.file.close()
	print ('Downloaded file has size %d')%(os.path.getsize(tf.name))
	untarfun(tf.name,target_dir)
	IJ.showStatus('Cleaning up!')
	tf.close()
