import cgi
import etree
from ownlib import ows
from owslib.util import openURL, testXMLValue, nspath_eval

namespaces = {
    None    : 'http://www.opengis.net/sos/1.0',
    'xlink' : 'http://www.w3.org/1999/xlink',
    'gml'   : 'http://www.opengis.net/gml',
    'ogc'   : 'http://www.opengis.net/ogc',
    'ows'   : 'http://www.opengis.net/ows',
}

class SosService(object):
    """
        Abstraction for OGC Sensor Observation Service (SOS).
    """

    def __init__(self, url, version='1.0.0', xml=None, 
                username=None, password=None):
        """Initialize."""
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        self._capabilities = None

        owscommon = ows.OwsCommon('1.0.0')
        namespaces['ows'] = owscommon.namespace

        # Authentication handled by Reader
        reader = SosCapabilitiesReader(
                version=self.version, url=self.url, username=self.username, password=self.password
                )
        if xml:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url)

        # Avoid building metadata if the response is an Exception
        se = self._capabilities.find('{self.OWS_NAMESPACE}ExceptionReport') 
        if se is not None: 
            raise ows.ExceptionReport(se) 

        # build metadata objects
        self._buildMetadata()

    def nsp(text):
        return nspath_eval(text,namespaces)

    def _buildMetadata(self):
        """ 
            Set up capabilities metadata objects
        """
        # ows:ServiceIdentification metadata
        service_id_element = self._capabilities.find(nsp('ows:ServiceIdentification'))
        self.identification = ows.ServiceIdentification(service_id_element, namespaces['ows'])
        
        # ows:ServiceProvider metadata
        service_provider_element = self._capabilities.find(nsp('ows:ServiceProvider'))
        self.provider = ows.ServiceProvider(service_provider_element, namespaces['ows'])
            
        # ows:OperationsMetadata metadata
        self.operations = []
        for op in self._capabilities.find(nsp('ows:OperationsMetadata/ows:Operation')):
            self.operations.append(ows.OperationMetadata(op, namespaces['ows']))
          
        # sos:Contents metadata
        self.offerings = []
        for offering in self._capabilities.find(nsp('sos:Contents/sos:ObservationOfferingList/sos:ObservationOffering')):
            offering_id = testXMLAttribute(offering,nsp('gml:id'))
            name = testXMLValue(offering.find(nsp('gml:name')))
            description = testXMLValue(offering.find(nsp('gml:description')))
            srsName = testXMLValue(offering.find(nsp('gml:srsName')))
            # (left, bottom, right, top) in srs units
            bbox = testXMLValue(offering.find(nsp('gml:srsName')))
            begin_time = 
            end_time
            offerings.append()

class SosContents(object):
    def __init__(self, element):
        

class SosCapabilitiesReader(object):
    def __init__(self, version="1.0.0", url=None, username=None, password=None):
        self.version = version
        self.url = url
        self.username = username
        self.password = password

    def capabilities_url(self, service_url):
        """
            Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'SOS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url):
        """
            Get and parse a WMS capabilities document, returning an
            elementtree instance

            service_url is the base url, to which is appended the service,
            version, and request parameters
        """
        getcaprequest = self.capabilities_url(service_url)
        spliturl=getcaprequest.split('?')
        u = openURL(spliturl[0], spliturl[1], method='Get', username = self.username, password = self.password)
        return etree.fromstring(u.read())

    def readString(self, st):
        """
            Parse a SOS capabilities document, returning an elementtree instance

            st should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)

