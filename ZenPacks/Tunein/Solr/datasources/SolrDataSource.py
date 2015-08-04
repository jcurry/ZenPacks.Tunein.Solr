# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

from zope.component import adapts
from zope.interface import implements

from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

import json
import pprint

# Setup logging
import logging
log = logging.getLogger('zen.Solr')

# PythonCollector Imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSource, PythonDataSourcePlugin

class SolrDataSource(PythonDataSource):
    """ Get  Solr data
        using HTTP API """

    ZENPACKID = 'ZenPacks.Tunein.Solr'

    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('SolrDataSource',)
    sourcetype = sourcetypes[0]

    component = '${here/id}'
    eventClass = '/Solr'

    # Custom fields in the datasource - with default values
    #    (which can be overriden in template )
    CoreName = '${here/coreName}'
    SolrCat = 'QUERYHANDLER'
    SolrKey = '/select'

    cycletime = 300

    _properties = PythonDataSource._properties + (
        {'id': 'CoreName', 'type': 'string', 'mode': 'w'},
        {'id': 'SolrCat', 'type': 'string', 'mode': 'w'},
        {'id': 'SolrKey', 'type': 'string', 'mode': 'w'},
    )

    # Collection plugin for this type. Defined below in this file.
    plugin_classname = ZENPACKID + '.datasources.SolrDataSource.SolrDataSourcePlugin'


class ISolrDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""

    CoreName = schema.TextLine(
        title = _t(u'Core Name'),
        group = _t('CoreName'))

    SolrCat = schema.TextLine(
        title = _t(u'Category'),
        group = _t('SolrCat'))

    SolrKey = schema.TextLine(
        title = _t(u'Key'),
        group = _t('SolrKey'))

class SolrDataSourceInfo(RRDDataSourceInfo):
    """ Adapter between ISolrDataSourceInfo and SolrDataSource """

    implements(ISolrDataSourceInfo)
    adapts(SolrDataSource)

    CoreName = ProxyProperty('CoreName')
    SolrCat = ProxyProperty('SolrCat')
    SolrKey = ProxyProperty('SolrKey')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False


class SolrDataSourcePlugin(PythonDataSourcePlugin):
    """ Data source plugin  for Solr
        with query in style
        http://sc01solrweb01.tiprod.net:8080/solr/tunein-keyword/admin/mbeans?stats=true&cat=QUERYHANDLER&key=/select&ident=true&wt=json
    """

    # List of device attributes you might need to do collection.
    proxy_attributes = (
        'zSolrCore',
        )

    @classmethod
    def config_key(cls, datasource, context):
        # Each component has its own zSolrCore so need to include context.id

            return (
                context.device().id,
                datasource.getCycleTime(context),
		datasource.rrdTemplate().id,
		datasource.id,
                context.id,
                'TuneinSolr',
                )

    @classmethod
    def params(cls, datasource, context):
        """
        Return params dictionary needed for this plugin.
 
        This is a classmethod that is executed in zenhub. The datasource and
        context parameters are the full objects.

        You have access to the dmd object database here and any attributes
        and methods for the context (either device or component).
 
        You can omit this method from your implementation if you don't require
        any additional information on each of the datasources of the config
        parameter to the collect method below. If you only need extra
        information at the device level it is easier to just use
        proxy_attributes as mentioned above.
        """

        # context is the object in question - device or component - component in this case
        params = {}

        params['CoreName'] = context.coreName
        params['SolrKey'] = datasource.talesEval(datasource.SolrKey, context)
        params['SolrCat'] = datasource.talesEval(datasource.SolrCat, context)
        deviceName = context.device().titleOrId()
        url = 'http://' + deviceName + ':8080/solr/' + context.coreName + '/admin/mbeans?stats=true&cat=' + params['SolrCat'] + '&key=' + params['SolrKey'] + '&ident=true&wt=json'
        params['url'] = url

        log.debug(' params is %s \n' % (params))
        return params

    @inlineCallbacks
    def collect(self, config):
        ds0 = config.datasources[0]
        url = ds0.params['url']
	response = yield getPage(url)
	response = json.loads(response)
	returnValue(response)

    def onResult(self, result, config):
        """
        Called first for success and error.
 
        You can omit this method if you want the result of the collect method
        to be used without further processing.
        """

        """ Expecting results in the format
        {u'responseHeader': {u'QTime': 0, u'status': 0},
         u'solr-mbeans': [u'QUERYHANDLER',
                  {u'/select': {u'class': u'org.apache.solr.handler.component.SearchHandler',
                                u'description': u'Search using components: query,facet,mlt,highlight,stats,debug,',
                                u'src': u'$URL: https://svn.apache.org/repos/asf/lucene/dev/branches/lucene_solr_4_7/solr/core/src/java/org/apache/solr/handler/component/SearchHandler.java $',
                                u'stats': {u'15minRateReqsPerSecond': 18.075537941762295,
                                           u'5minRateReqsPerSecond': 17.8694818261944,
                                           u'75thPcRequestTime': 0.2909145,
                                           u'95thPcRequestTime': 0.392635,
                                           u'999thPcRequestTime': 1.8323845120000026,
                                           u'99thPcRequestTime': 0.5797193700000012,
                                           u'avgRequestsPerSecond': 14.137846852899436,
                                           u'avgTimePerRequest': 0.22413381900889817,
                                           u'errors': 0,
                                           u'handlerStart': 1431979800440,
                                           u'medianRequestTime': 0.23052899999999998,
                                           u'requests': 59621583,
                                           u'timeouts': 0,
                                           u'totalTime': 13363213.093146},
                                u'version': u'4.7.1'}}]}

        or for CORE request.....

        {u'responseHeader': {u'QTime': 0, u'status': 0},
         u'solr-mbeans': [u'CORE',
                  {u'searcher': {u'class': u'org.apache.solr.search.SolrIndexSearcher',
                                 u'description': u'index searcher',
                                 u'src': u'$URL: https://svn.apache.org/repos/asf/lucene/dev/branches/lucene_solr_4_7/solr/core/src/java/org/apache/solr/search/SolrIndexSearcher.java $',
                                 u'stats': {u'caching': True,
                                            u'deletedDocs': 1,
                                            u'indexVersion': 7996,
                                            u'maxDoc': 2228,
                                            u'numDocs': 2227,
                                            u'openedAt': u'2015-07-02T15:37:01.424Z',
                                            u'reader': u'StandardDirectoryReader(segments_1nk:7996:nrt _1ni(4.7):C2224/1:delGen=1 _1nu(4.7):C1 _1o7(4.7):C1 _1oj(4.7):C1 _1ov(4.7):C1)',
                                            u'readerDir': u'org.apache.lucene.store.NRTCachingDirectory:NRTCachingDirectory(MMapDirectory@/srv/tunein-solr/tunein-keyword/data/index.20150520224102357 lockFactory=NativeFSLockFactory@/srv/tunein-solr/tunein-keyword/data/index.20150520224102357; maxCacheMB=48.0 maxMergeSizeMB=4.0)',
                                            u'registeredAt': u'2015-07-02T15:37:01.885Z',
                                            u'searcherName': u'Searcher@7a45db79[tunein-keyword] main',
                                            u'warmupTime': 459},
                                 u'version': u'1.0'}}]}
        """
        log.debug( 'result is %s ' % (result))

        return result

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
        You should return a data structure with zero or more events, values
        and maps.
        Note that values is a dictionary and events and maps are lists.

        return {
            'events': [{
                'summary': 'successful collection',
                'eventKey': 'myPlugin_result',
                'severity': 0,
                },{
                'summary': 'first event summary',
                'eventKey': 'myPlugin_result',
                'severity': 2,
                },{
                'summary': 'second event summary',
                'eventKey': 'myPlugin_result',
                'severity': 3,
                }],
 
            'values': {
                None: {  # datapoints for the device (no component)
                    'datapoint1': 123.4,
                    'datapoint2': 5.678,
                    },
                'cpu1': {
                    'user': 12.1,
                    nsystem': 1.21,
                    'io': 23,
                    }
                },
 
            'maps': [
                ObjectMap(...),
                RelationshipMap(..),
                ]
            }
            """

        log.debug( 'In success - result is %s and config is %s ' % (result, config))

        data = self.new_data()
        ds0 = config.datasources[0]
        for ds in config.datasources:
            SolrKey = ds.params['SolrKey']
            log.debug('ds is %s and ds.component is %s and SolrKey is %s \n' % (ds, ds.component, SolrKey))
            try:
		statsData = result['solr-mbeans'][1][SolrKey]['stats']
            except:
                continue

            for datapoint_id in (x.id for x in ds.points):
                if datapoint_id not in statsData:
                    continue
                try:
                    value = statsData[datapoint_id]
                    if datapoint_id == 'indexSize':
                        # indexSize is a string - u'indexSize': u'291.6 KB'
                        #    so chop off the KB / MB / GB  and multiply to get bytes
                        val = value.split()
                        if val[1] == 'KB':
                            value = float(value.split()[0]) * 1024
                        elif val[1] == 'MB':
                            value = float(value.split()[0]) * 1024 * 1024
                        elif val[1] == 'GB':
                            value = float(value.split()[0]) * 1024 * 1024 * 1024
                        else:
                            # Dont know what else it might be so just return value
                            value = float(value.split()[0])
                except Exception, e:
                    log.error('Failed to get value datapoint for %s, error is %s' % (datapoint_id, e))
                    # Sometimes values are NA or not available.
                    continue

                dpname = '_'.join((ds.datasource, datapoint_id))
                data['values'][ds.component][dpname] = (value, 'N')

        return data

    def onError(self, result, config):
        """
        Called only on error. After onResult, before onComplete.
 
        You can omit this method if you want the error result of the collect
        method to be used without further processing. It recommended to
        implement this method to capture errors.
        """
        log.debug( 'In OnError - result is %s and config is %s ' % (result, config))
        return {
            'events': [{
                'summary': 'Error getting Solrdata with zenpython: %s' % result,
                'eventKey': 'Solr',
                'severity': 4,
                }],
            }

    def onComplete(self, result, config):
        """
        Called last for success and error.
 
        You can omit this method if you want the result of either the
        onSuccess or onError method to be used without further processing.
        """
        return result


