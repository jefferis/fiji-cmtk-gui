fiji-cmtk-gui
=============

Working version of a simple GUI frontend for [CMTK image registration tools](http://www.nitrc.org/projects/cmtk/) in [Fiji](http://fiji.sc/)

Install
=======

  * Install [Fiji](http://fiji.sc/)
  * Enable the **CMTK Registration** update site (http://sites.imagej.net/Jefferis), 
  by following [these detailed instructions](http://imagej.net/How_to_follow_a_3rd_party_update_site).
  * Run `Plugins>CMTK Registration>Install CMTK` to install CMTK

Use
===

  * **CMTK Registration GUI** is the main entry point
  * See [Jefferis Lab Wiki](http://flybrain.mrc-lmb.cam.ac.uk/dokuwiki/doku.php?id=warping_manual:registration_gui)

Update
======

  * Use the Fiji updater to update files (but see below for Developer Install/Update)
  * To update the CMTK registration software, choose `Install CMTK`
    * This will compare the current version on the CMTK website with the installed version and offer to update if appropriate.

Problems
========

* If you have trouble please check the list of [previously reported bugs](https://github.com/jefferis/fiji-cmtk-gui/issues?utf8=%E2%9C%93&q=is%3Aissue+label%3Abug). There may already be a solution.
* See also the [NITRC CMTK User Forum](https://www.nitrc.org/forum/forum.php?forum_id=857)

Developer Install
=================

  * Download the [zip file](https://github.com/jefferis/fiji-cmtk-gui/zipball/master) for this repository
  * Expand the zip file
  * Rename the newly expanded folder to `CMTK_Registration`
  * Move this inside the `plugins` subfolder of Fiji 
    * To see this folder on a Mac you need to show Fiji in the Finder
    * Then Right Click and choose Show Package Contents
    * then navigate to the `plugins` subfolder
  * (Re)start Fiji
  * Choose **Plugins ... CMTK Registration ... Install CMTK**

Developer Update
================

  * To update the code for this GUI, choose `Update to Developer CMTK GUI`
