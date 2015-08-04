"""Models Solr devices using the zSolrCore zProperty

"""

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

import json

class SolrMap(PythonPlugin):

    """SolrMap modeler plugin"""

    requiredProperties = (
        'zSolrCore',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Asynchronously collect data from device. Return a deferred."""
        log.info("%s: collecting data", device.id)
        coresList = getattr(device, 'zSolrCore', None)
        if not coresList:
            log.error('No zSolrCore property set - please set this for the device')
            returnValue(None)
        else:
            response = {}
            #deviceName = device.titleOrId()
            deviceName = device.id
            for core in coresList:
                try:
		    coresDict = {}
		    coresDict['name'] = core
		    coreUrl = 'http://' + deviceName + ':8080/solr/' + core + '/admin/mbeans?stats=true&cat=CORE&key=searcher&ident=true&wt=json'
		    coreResp = yield getPage(coreUrl)
		    coreResp = json.loads(coreResp)
		    coresDict['coreUrl'] = coreResp
		    replUrl = 'http://' + deviceName + ':8080/solr/' + core + '/admin/mbeans?stats=true&cat=QUERYHANDLER&key=/replication&ident=true&wt=json'
		    replResp = yield getPage(replUrl)
		    replResp = json.loads(replResp)
		    coresDict['replUrl'] = replResp
		    response[core] = coresDict
		except Exception, e:
		    log.error(
			"%s: %s", device.id, e)
		    #returnValue(None)
                    continue
	    #log.info('Response is %s \n' % (response))
	    returnValue(response)

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""

        maps = []
        solrs = []

        for k,v in results.iteritems():
            coreId = self.prepId(k)
            indexVersion = v['coreUrl']['solr-mbeans'][1]['searcher']['stats']['indexVersion']
            warmupTime = v['coreUrl']['solr-mbeans'][1]['searcher']['stats']['warmupTime']
            indexSize = v['replUrl']['solr-mbeans'][1]['/replication']['stats']['indexSize']
            #log.info(' core is %s indexVersion is %s warmupTime is %s indexSize is %s \n' % (coreId, indexVersion, warmupTime, indexSize))
	    solrs.append(ObjectMap(data={
		'id': coreId,
		'title': coreId,
		'coreName': coreId,
		'indexVersion': indexVersion,
		'indexSize': indexSize,
		'warmupTime': warmupTime,
		}))

        maps.append(RelationshipMap(
            relname = 'solrCores',
            modname = 'ZenPacks.Tunein.Solr.SolrCore',
            objmaps = solrs ))

        return maps
