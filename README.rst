===============================
ZenPack to support Apache Solr
===============================

Description
===========
This ZenPack supports  devices that are using the the Apache Solr tomcat application for
distributed search indexes.  The ZenPack is deliberately configured specifically for Tunein.

This ZenPack is built with the zenpacklib library so does not have explicit code definitions for
device classes, device and component objects or zProperties.  Templates are also created through zenpacklib.
These elements are all created through the zenpack.yaml file in the main directory of the ZenPack.
See http://zenpacklib.zenoss.com/en/latest/index.html for more information on zenpacklib.

Note that if templates are changed in the zenpack.yaml file then when the ZenPack is reinstalled, the
existing templates will be renamed in the Zenoss ZODB database and the new template from the YAML file
will be installed; thus a backup is effectively taken.  Old templates should be deleted in the Zenoss GUI
when the new version is proven.

The ZenPack introduces a new zProperties, of type list (lines) for configuring Solr cores to monitor:
    * zSolrCore            default is [tunein-keyword,tunein-topic,tunein-alias,tunein-program,tunein-station,tunein-user]

The ZenPack creates a new device object called SolrDevice and new a component type for:
    * Solr Cores

where SolrDevice -> contains many SolrCore components

The /Server/Linux/Tomcat/Solr device class is supplied with appropriate zProperties 
and templates applied. Although a modeler plugin is supplied, it is not automatically
added to this device class, so as not to override any /Server/Linux plugins inherited in the
local environment.  The zPythonClass standard property is set 
to ZenPacks.Tunein.Solr.SolrDevice for the device class.

THE SolrMap MODELER PLUGIN MUST BE MANUALLY ADDED TO YOUR /Server/Linux/Tomcat/Solr DEVICE
CLASS AFTER THE ZENPACK HAS BEEN INSTALLED.

A component template for SolrCore is supplied with datasources and datapoints for:
    * SolrQuerySelect
    * SolrQueryUpdate
    * SolrQueryImport
    * SolrQueryReplication
    * SolrCore

All the templates are based on Python.  A new datasource, SolrDataSource is provided in the 
datasources directory of the ZenPack.  This permits the user to further customise the Solr Key and
Solr Category parameters in the templates, if required.  

The plugin part of the datasource uses Python and the Twisted Web Client
for Python to apply http queries to retrieve Solr data.

These Python templates require the PythonCollector ZenPack to be installed as a 
prerequisite (version >=1.6)

A /Solr Event Class is included  with the ZenPack and is configured into the templates.


Requirements & Dependencies
===========================

    * Zenoss Versions Supported:  4.x
    * External Dependencies: 
      * The zenpacklib package that this ZenPack is built on, requires PyYAML.  This is installed as 
      standard with Zenoss 5 and with Zenoss 4 with SP457.  To test whether it is installed, as
      the zenoss user, enter the python environment and import yaml:

        python
        import yaml
        yaml

        <module 'yaml' from '/opt/zenoss/lib/python2.7/site-packages/PyYAML-3.11-py2.7-linux-x86_64.egg/yaml/__init__.py'>

      If pyYAML is not installed, install it, as the zenoss user, with:

        easy_install PyYAML

      and then rerun the test above.


    * ZenPack Dependencies: PythonCollector >= 1.6
    * Installation Notes: Restart zenoss entirely after installation
    * Configuration: Add the SolrMap modeler plugin to the /Server/Linux/Tomcat/Solr device class



Download
========
Download the appropriate package for your Zenoss version from the list
below.

* Zenoss 4.0+ `Latest Package for Python 2.7`_

ZenPack installation
======================

This ZenPack can be installed from the .egg file using either the GUI or the
zenpack command line. To install in development mode, from github - 
https://github.com/jcurry/ZenPacks.Tunein.Solr  use the ZIP button
(top left) to download a tgz file and unpack it to a local directory, say,
$ZENHOME/local.  Install from $ZENHOME/local with:

zenpack --link --install ZenPacks.Tunein.Solr

Restart zenoss after installation.

Device Support
==============



Change History
==============
* 1.0.0
   * Initial Release

Screenshots
===========

See the screenshots directory.


.. External References Below. Nothing Below This Line Should Be Rendered

.. _Latest Package for Python 2.7: https://github.com/jcurry/ZenPacks.Tunein.Solr/blob/master/dist/ZenPacks.Tunein.Solr-1.0.0-py2.7.egg?raw=true

Acknowledgements
================

This ZenPack has been developed under contract to TuneIn Inc who have generously open-sourced
it to the community.

