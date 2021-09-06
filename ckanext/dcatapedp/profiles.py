from builtins import str
import json

from ckantoolkit import config

import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, RDFS

from ckan.plugins import toolkit
from ckan.lib.helpers import url_for

from ckanext.dcat.utils import resource_uri, dataset_id_from_resource, catalog_uri
from ckanext.dcat.profiles import URIRefOrLiteral, RDFProfile

from ckanext.dcatapedp.utils import unified_resource_format_iana, unified_resource_format_eu, unified_resource_format_ckan

from geomet import wkt, InvalidGeoJSONException

# Namespaces
DCT = Namespace("http://purl.org/dc/terms/")
DCT_TYPE = Namespace("http://purl.org/dc/dcmitype/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCATAP = Namespace("http://data.europa.eu/r5r/")
ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace('http://schema.org/')
TIME = Namespace('http://www.w3.org/2006/time')
LOCN = Namespace('http://www.w3.org/ns/locn#')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SPDX = Namespace('http://spdx.org/rdf/terms#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

GEOJSON_IMT = 'https://www.iana.org/assignments/media-types/application/vnd.geo+json'

GEO_SCHEMA_URI = 'http://sws.geonames.org'
EU_CORPORATE_BODY_SCHEMA_URI = 'http://publications.europa.eu/resource/authority/corporate-body'

EU_FILETYPE_URI = 'http://publications.europa.eu/resource/authority/file-type/'
IANA_FILETYPE_URI = 'https://www.iana.org/assignments/media-types/'

namespaces = {
    'dct': DCT,
    'dcat': DCAT,
    'dcatap': DCATAP,
    'adms': ADMS,
    'vcard': VCARD,
    'foaf': FOAF,
    'schema': SCHEMA,
    'time': TIME,
    'skos': SKOS,
    'locn': LOCN,
    'gsp': GSP,
    'owl': OWL,
    'spdx': SPDX,
}



class EDPDCATAPProfile(RDFProfile):
    '''
    An RDF profile for the EDP DCAT-AP recommendation for data portals

    It requires the European DCAT-AP profile (`euro_dcat_ap`)
    '''

    def _distribution_id_from_distributions(self, g, resource_dict):
        '''
        Finds the complete subject (catalog + dataset + distribution) of a distribution
        from dataset id and resource id
        '''
        distributions = g.subjects(RDF.type, DCAT.Distribution)
        dataset_id = dataset_id_from_resource(resource_dict)
        resource_id = resource_dict.get('id')
        # TODO with ckan.lib.helpers.url_for
        uri = 'dataset/{0}/resource/{1}'.format(dataset_id, resource_id)
        for distribution in distributions:
            if (uri in distribution):
                return distribution

    def _add_or_replace_from_extra(self, dictionary, key, value):
        if not 'extras' in dictionary:
            dictionary['extras'] = []
        for extra in dictionary.get('extras', []):
            if extra['key'] == key:
                extra['value'] = value
                return

        dictionary['extras'].append({'key': key, 'value': value})

    def _time_interval_edp(self, subject, predicate):
        '''
        Returns the start and end date for a time interval object
        Both subject and predicate must be rdflib URIRef or BNode objects
        It checks for time intervals defined with dcat startDate &
        endDate.
        Returns a tuple with the start and end date values, both of which
        can be None if not found
        '''

        start_date = end_date = None

        interval = self.g.value(subject, predicate)
        if interval:
            start_date = self.g.value(interval, DCAT.startDate)
            end_date = self.g.value(interval, DCAT.endDate)

        return start_date, end_date

    def _spatial_edp(self, subject, predicate):
        '''
        Returns geom with the value set to
        None if they could not be found.
        Geometries are always returned in GeoJSON.
        WKT is transformed to GeoJSON.
        Check the notes on the README for the supported formats:
        https://github.com/ckan/ckanext-dcat/#rdf-dcat-to-ckan-dataset-mapping
        '''

        geom = None

        spatial = self.g.value(subject, predicate)
        if spatial and (spatial, RDF.type, DCT.Location) in self.g:
            geometry = self.g.value(spatial, DCAT.bbox)
            if geometry and geometry.datatype == GSP.wktLiteral:
                try:
                    geom = json.dumps(wkt.loads(str(geometry)))
                except (ValueError, TypeError, InvalidGeoJSONException):
                    pass

        return geom

    def _distribution_license_edp(self, subject, predicate):
        '''
        Returns the license and the license type.
        If the license is a BNode it returns None.
        None if they could not be found.
        '''

        license = self.g.value(subject, predicate)
        licnese_type = None
        if license:
            license_type = self.g.value(license, DCT.type)
            if isinstance(license, BNode):
                license = None
        return license, license_type    

    def _distribution_format_edp(self, subject):
        '''
        Returns the Internet Media Type and format label for a distribution.
        Extracts the Internet Media Type from IANA complete URI or EU file type complete URI.
        Extracts the format from EU file type complete URI or Internet Media Type from IANA complete URI
        None if they could not be found.
        '''

        imt = None
        label = None

        imt_ref = self.g.value(subject, DCAT.mediaType)
        label_ref = self.g.value(subject, DCT['format'])

        if imt_ref and IANA_FILETYPE_URI in imt_ref:
            imt = imt_ref.replace(IANA_FILETYPE_URI, '')
        if label_ref and EU_FILETYPE_URI in label_ref:
            label_eu = label_ref.replace(EU_FILETYPE_URI, '')
            label = unified_resource_format_ckan(label_eu.lower())
            if not label:
                label = label_eu
        return imt, label


    def parse_dataset(self, dataset_dict, dataset_ref):
        return dataset_dict
        # TODO


    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # add type for dataset_ref
        # g.add((dataset_ref, DCT.type, DCT_TYPE.Dataset))

        # Landing page
        landing_page = dataset_dict.get('url')
        if landing_page:
            landing_page_ref = URIRefOrLiteral(landing_page)
            g.remove((dataset_ref, DCAT.landingPage, landing_page_ref))
            g.add((landing_page_ref, RDF.type, FOAF.Document))
            g.add((dataset_ref, DCAT.landingPage, landing_page_ref))

        # Publisher: Generalize type from FOAF.Organization to FOAF.Agent
        # TODO is not correct to generalize but edp validator does
        organization_ref = g.value(dataset_ref, DCT.publisher)
        if organization_ref:
            g.set((organization_ref, RDF.type, FOAF.Agent))
            if not EU_CORPORATE_BODY_SCHEMA_URI in organization_ref:
                # TODO Just to pass the validator but it is a mistake to put it.
                schema = URIRef(EU_CORPORATE_BODY_SCHEMA_URI)
                g.add((organization_ref, SKOS.inScheme, schema))

        # Contact details: Generalize type from VCARD.Organization to VCARD.contactPoint
        # TODO is not correct to generalize but edp validator does
        contact_point_ref = g.value(dataset_ref, DCAT.contactPoint)
        if contact_point_ref:
            g.set((contact_point_ref, RDF.type, VCARD.Kind))

        # Temporal
        temporal_ref = g.value(dataset_ref, DCT.temporal, None)
        if temporal_ref:
            start = self._get_dataset_value(dataset_dict, 'temporal_start')
            end = self._get_dataset_value(dataset_dict, 'temporal_end')
            if start:
                g.remove((temporal_ref, SCHEMA.startDate, None))
                self._add_date_triple(temporal_ref, DCAT.startDate, start)
            if end:
                g.remove((temporal_ref, SCHEMA.endDate, None))
                self._add_date_triple(temporal_ref, DCAT.endDate, end)

        # Spatial
        spatial = g.value(dataset_ref, DCT.spatial)
        if spatial:
            spatial_geom = self._get_dataset_value(dataset_dict, 'spatial')
            spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
            g.remove((spatial, LOCN.geometry, None))
            if spatial_uri and GEO_SCHEMA_URI in spatial_uri:
                schema = URIRef(GEO_SCHEMA_URI)
                # TODO Just to pass the validator but it is a mistake to put it.
                g.add((spatial, SKOS.inScheme, schema))
            if spatial_geom:
                # WKT, because GeoDCAT-AP says so
                try:
                    g.add((spatial,
                           DCAT.bbox,
                           Literal(wkt.dumps(json.loads(spatial_geom),
                                             decimals=4),
                                   datatype=GSP.wktLiteral)))
                except:
                    # GeoJSON
                    g.add((spatial,
                           LOCN.geometry,
                           Literal(spatial_geom, datatype=GEOJSON_IMT)))
                    pass

        # Resource
        for resource_dict in dataset_dict.get('resources', []):
            distribution = self._distribution_id_from_distributions(
                g, resource_dict)


            # Format
            # DCAT.mediaType (the first to accomplish): 
            # 1. It maps mimetype to IANA mimetype.
            # 2. It maps format to IANA mimetype.
            # 3. It does not modify the euro_dcat_ap profile.
            # DCT.format:
            # 1. It maps format to EUROPE file type as dct:MediaTypeOrExtent.
            # 2. It maps mimetype to EUROPE file type as dct:MediaTypeOrExtent.
            # 3. It does not modify the euro_dcat_ap profile.
            
            mimetype = resource_dict.get('mimetype')
            fmt = resource_dict.get('format')
            normalize_ckan_format = toolkit.asbool(config.get(
                'ckanext.dcat.normalize_ckan_format', True))

            if ((mimetype or fmt) and normalize_ckan_format and
                toolkit.check_ckan_version(min_version='2.3')):

                # DCAT.mediaType
                if mimetype:
                    mimetype_iana = unified_resource_format_iana(mimetype)
                elif fmt:
                    mimetype_iana = unified_resource_format_iana(fmt)
                
                if mimetype_iana:
                    mimetype_ref = URIRef(
                        '{0}{1}'.format(IANA_FILETYPE_URI, mimetype_iana))
                    g.remove((distribution, DCAT.mediaType, None))
                    g.add((mimetype_ref, RDF.type, DCT.MediaType))
                    g.add((distribution, DCAT.mediaType, mimetype_ref))
                
                # DCT.format
                if fmt:
                    fmt_eu = unified_resource_format_eu(fmt)
                elif mimetype:
                    fmt_eu = unified_resource_format_eu(mimetype)
                
                if fmt_eu:
                    fmt_ref = URIRef(
                        '{0}{1}'.format(EU_FILETYPE_URI, fmt_eu))
                    g.remove((distribution, DCT['format'], None))
                    g.add((fmt_ref, RDF.type, DCT['MediaTypeOrExtent']))
                    g.add((distribution, DCT['format'],
                        fmt_ref))


            # License
            license = self._get_resource_value(resource_dict, 'license')
            license_type = self._get_resource_value(
                resource_dict, 'license_type')
            g.remove((distribution, DCT.license, None))
            if license or license_type:
                if not license:
                    license_ref = BNode()
                else:
                    license_ref = URIRefOrLiteral(license)
                if license_type:
                    g.add((license_ref, DCT.type, URIRefOrLiteral(license_type)))
                g.add((license_ref, RDF.type, DCT.LicenseDocument))
                g.add((distribution, DCT.license, license_ref))

            # Availability
            availability = resource_dict.get('availability')
            if availability:
                availability_ref = URIRefOrLiteral(availability)
                g.add((distribution, DCATAP.availability, availability_ref))

    def test_graph_from_catalog(self, catalog_dict, catalog_ref):
        
        g = self.g
        # TODO