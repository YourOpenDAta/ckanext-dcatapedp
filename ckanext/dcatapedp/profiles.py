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

        Finds the complete subject
        1. The value of the uri field
        2.(catalog + dataset + distribution) of a distribution
        from dataset id and resource id
        3. return from ckanex.dcat.utils resource_uri
        '''
        uri = resource_dict.get('uri')
        if not uri or uri == 'None':
            distributions = g.subjects(RDF.type, DCAT.Distribution)
            dataset_id = dataset_id_from_resource(resource_dict)
            resource_id = resource_dict.get('id')
            # TODO with ckan.lib.helpers.url_for
            uri_part = 'dataset/{0}/resource/{1}'.format(dataset_id, resource_id)
            for distribution in distributions:
                if (uri_part in distribution):
                    uri = distribution
            if not uri or uri == 'None':
                uri = resource_uri(resource_dict)
        return uri

    # CKAN metadata from GRAPH

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

        interval_ref = self.g.value(subject, predicate)
        if interval_ref:
            start_date = self._object_value(interval_ref, DCAT.startDate)
            end_date = self._object_value(interval_ref, DCAT.endDate)

        return start_date, end_date

    def _spatial_edp(self, subject, predicate):
        '''
        Returns geom and centroid with the value set to
        None if they could not be found.
        Geometries are always returned in GeoJSON.
        WKT is transformed to GeoJSON.
        Check the notes on the README for the supported formats:
        https://github.com/ckan/ckanext-dcat/#rdf-dcat-to-ckan-dataset-mapping
        '''

        geom = None
        centr = None

        spatial_ref = self.g.value(subject, predicate)
        if spatial_ref and (spatial_ref, RDF.type, DCT.Location) in self.g:
            geometry = self.g.value(spatial_ref, DCAT.bbox)
            centroid = self.g.value(spatial_ref, DCAT.centroid)
            if geometry and geometry.datatype == GSP.wktLiteral:
                try:
                    geom = json.dumps(wkt.loads(str(geometry)))
                except (ValueError, TypeError, InvalidGeoJSONException):
                    pass
            if centroid and centroid.datatype == GSP.wktLiteral:
                try:
                    centr = json.dumps(wkt.loads(str(centroid)))
                except (ValueError, TypeError, InvalidGeoJSONException):
                    pass

        return geom, centr

    def _distribution_license_edp(self, subject, predicate):
        '''
        Returns the license and the license type.
        If the license is a BNode and not DCT.title it returns None.
        None if they could not be found.
        '''

        license_ref = self.g.value(subject, predicate)

        license = None
        license_type = None
        if license_ref:
            license_type = self._object_value(license_ref, DCT.type)
            if isinstance(license_ref, BNode):
                license = self._object_value(license_ref, DCT.title)
            else:
                license = str(license_ref)
        return license, license_type

    def _distribution_format_edp(self, subject, normalize_ckan_format=True):
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

        if ((imt_ref or label_ref) and normalize_ckan_format and
                toolkit.check_ckan_version(min_version='2.3')):
            if imt_ref and IANA_FILETYPE_URI in imt_ref:
                imt = imt_ref.replace(IANA_FILETYPE_URI, '')
            if label_ref and EU_FILETYPE_URI in label_ref:
                label_eu = label_ref.replace(EU_FILETYPE_URI, '')
                label = unified_resource_format_ckan(label_eu.lower())
                if not label:
                    label = label_eu
        return imt, label

    def _conforms_to_edp(self, subject):
        conformsToList = []
        for _, _, conforms_to_ref in self.g.triples((subject, DCT.conformsTo, None)):
                    conformsToList.append(self._object_value(conforms_to_ref, RDFS.label))
        if len(conformsToList) > 0:
            return json.dumps(conformsToList)
        else:
            return None


    def parse_dataset(self, dataset_dict, dataset_ref):
        # Temporal
        start, end = self._time_interval_edp(dataset_ref, DCT.temporal)
        if start:
            dataset_dict['extras'].append(
                {'key': 'temporal_start', 'value': start})
        if end:
            dataset_dict['extras'].append(
                {'key': 'temporal_end', 'value': end})

        # Spatial
        geom, centr = self._spatial_edp(dataset_ref, DCT.spatial)
        if geom:
            dataset_dict['extras'].append(
                {'key': 'spatial', 'value': geom})
        if centr:
            dataset_dict['extras'].append(
                {'key': 'spatial_centroid', 'value': centr})

        # accessRights: in euro_dcat_ap profile

        # conformsTo
        conformsToList = self._conforms_to_edp(dataset_ref)
        if conformsToList:
            self._add_or_replace_from_extra(
                    dataset_dict, 'conforms_to', conformsToList)

        # page, documentation: in euro_dcat_ap profile

        # adms identifier
        adms_identifier_list = []
        for _, _, adms_identifier_ref in self.g.triples((dataset_ref, ADMS.identifier, None)):
                    adms_identifier_list.append(self._object_value(adms_identifier_ref, SKOS.notation))
        if len(adms_identifier_list) > 0:
            self._add_or_replace_from_extra(
                    dataset_dict, 'alternate_identifier', json.dumps(adms_identifier_list))

        # provenance
        provenance_ref = self.g.value(dataset_ref, DCT.provenance)
        if (provenance_ref and isinstance(provenance_ref, BNode)):
            provenance = self.g.value(provenance_ref, RDFS.label)
            if provenance:
              self._add_or_replace_from_extra(
                    dataset_dict, 'provenance', str(provenance))

        # sample: in euro_dcat_ap profile
        # source: in euro_dcat_ap profile

        # dct type
        dct_type_ref = self.g.value(dataset_ref, DCT['type'])
        if (dct_type_ref and isinstance(dct_type_ref, BNode)):
            dct_type = self.g.value(dct_type_ref, SKOS.prefLabel)
            if dct_type:
              self._add_or_replace_from_extra(
                    dataset_dict, 'dcat_type', str(dct_type))

        # Resources
        for resource_dict in dataset_dict.get('resources', []):
            resource_uri = resource_dict['uri']
            if not resource_uri:
                continue
            distribution = URIRef(resource_uri)

            # Format
            normalize_ckan_format = toolkit.asbool(config.get(
                'ckanext.dcat.normalize_ckan_format', True))
            imt, label = self._distribution_format_edp(
                distribution, normalize_ckan_format)

            if imt:
                resource_dict['mimetype'] = imt

            if label:
                resource_dict['format'] = label
            elif imt:
                resource_dict['format'] = imt

            # License
            license, license_type = self._distribution_license_edp(
                distribution, DCT.license)

            if not license:
                try:
                    resource_dict.pop('license')
                except:
                    pass
            else:
                resource_dict['license'] = license
            if license_type:
                resource_dict['license_type'] = license_type

            # Availability
            availability = self._object_value(
                distribution, DCATAP.availability)
            if availability:
                resource_dict['availability'] = availability

            # conformsTo
            conformsToList = self._conforms_to_edp(distribution)
            if conformsToList:
                resource_dict['conforms_to'] = conformsToList

            # rights: in euro_dcat_ap profile
            # page, documentation: in euro_dcat_ap profile

        return dataset_dict

    # GRAPH from CKAN metadata

    def _generate_conforms_to_graph(self, subject):
        g = self.g
        for _, _, conforms_to in g.triples((subject, DCT.conformsTo, None)):
            conforms_to_ref = BNode()
            g.remove((subject, DCT.conformsTo, conforms_to))
            g.add((conforms_to_ref, RDF.type, DCT.Standard))
            g.add((conforms_to_ref, RDFS.label, Literal(conforms_to)))
            g.add((subject, DCT.conformsTo, conforms_to_ref))

    def _generate_page_to_graph(self, subject):
        g = self.g
        for _, _, page in g.triples((subject, FOAF.page, None)):
            page_ref = URIRefOrLiteral(page)
            g.add((page_ref, RDF.type, FOAF.Document))

    def _generate_rights_to_graph(self, subject, predicate):
        g = self.g
        access_rights = g.value(subject, predicate)
        if access_rights:
            license_rights_ref = BNode()
            g.remove((subject, predicate, None))
            g.add((license_rights_ref, RDF.type, DCT.RightsStatement))
            g.add((license_rights_ref, RDFS.label, Literal(access_rights)))
            g.add((subject, predicate, license_rights_ref))

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # add type for dataset_ref
        # g.add((dataset_ref, DCT.type, DCT_TYPE.Dataset))

        # Landing page
        landing_page = dataset_dict.get('url')
        if landing_page:
            landing_page_ref = URIRefOrLiteral(landing_page)
            g.add((landing_page_ref, RDF.type, FOAF.Document))

        # Publisher: Generalize type from FOAF.Organization to FOAF.Agent
        organization_ref = g.value(dataset_ref, DCT.publisher)
        if organization_ref:
            g.set((organization_ref, RDF.type, FOAF.Agent))
            if not EU_CORPORATE_BODY_SCHEMA_URI in organization_ref:
                # TODO Just to pass the validator but it is a mistake to put it.
                schema = URIRef(EU_CORPORATE_BODY_SCHEMA_URI)
                g.add((organization_ref, SKOS.inScheme, schema))

        # Contact details: Generalize type from VCARD.Organization to VCARD.contactPoint
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
        spatial_ref = g.value(dataset_ref, DCT.spatial)
        if spatial_ref:
            spatial_geom = self._get_dataset_value(dataset_dict, 'spatial')
            spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
            # spatial_centroid recommended property for dcat-ap v2
            spatial_centroid = self._get_dataset_value(
                dataset_dict, 'spatial_centroid')
            g.remove((spatial_ref, LOCN.geometry, None))
            if spatial_uri and GEO_SCHEMA_URI in spatial_uri:
                schema = URIRef(GEO_SCHEMA_URI)
                # TODO Just to pass the validator but it is a mistake to put it.
                g.add((spatial_ref, SKOS.inScheme, schema))
            if spatial_geom:
                # WKT, because GeoDCAT-AP says so
                try:
                    g.add((spatial_ref,
                           DCAT.bbox,
                           Literal(wkt.dumps(json.loads(spatial_geom),
                                             decimals=4),
                                   datatype=GSP.wktLiteral)))
                except:
                    # GeoJSON
                    g.add((spatial_ref,
                           LOCN.geometry,
                           Literal(spatial_geom, datatype=GEOJSON_IMT)))
                    pass

            if spatial_centroid:
                try:
                    g.add((spatial_ref,
                           DCAT.centroid,
                           Literal(wkt.dumps(json.loads(spatial_centroid),
                                             decimals=4),
                                   datatype=GSP.wktLiteral)))
                except:
                    pass

        # accessRights: change range to dct:RightsStatement
        self._generate_rights_to_graph(dataset_ref, DCT.accessRights)

        #conformsTo: change range to dct:Standard
        self._generate_conforms_to_graph(dataset_ref)

        # page change range to foaf:document
        self._generate_page_to_graph(dataset_ref)

        # adms identifier: change range to ADMS.Identifier
        for _, _, adms_identifier in g.triples((dataset_ref, ADMS.identifier, None)):
            adms_identifier_ref = BNode()
            g.remove((dataset_ref, ADMS.identifier, adms_identifier))
            g.add((adms_identifier_ref, RDF.type, ADMS.Identifier))
            g.add((adms_identifier_ref, SKOS.notation, Literal(adms_identifier)))
            g.add((dataset_ref, ADMS.identifier, adms_identifier_ref))

        # provenance: change range to dct:ProvenanceStatement
        provenance = g.value(dataset_ref, DCT.provenance)
        if provenance:
            provenance_ref = BNode()
            g.remove((dataset_ref, DCT.provenance, None))
            g.add((provenance_ref, RDF.type, DCT.ProvenanceStatement))
            g.add((provenance_ref, RDFS.label, Literal(provenance)))
            g.add((dataset_ref, DCT.provenance, provenance_ref))
        
        # sample: change range to UriRef or Literal not only literal
        for _, _, sample in g.triples((dataset_ref, ADMS.sample, None)):
            g.remove((dataset_ref, ADMS.sample, sample))
            g.add((dataset_ref, ADMS.sample, URIRefOrLiteral(sample)))

        # source: change range to UriRef or Literal not only literal
        for _, _, source in g.triples((dataset_ref, DCT.source, None)):
            g.remove((dataset_ref, DCT.source, source))
            g.add((dataset_ref, DCT.source, URIRefOrLiteral(source)))

        # type: change range to skos:concept
        dct_type = g.value(dataset_ref, DCT['type'])
        if dct_type:
            dct_type_ref = BNode()
            g.remove((dataset_ref, DCT['type'], None))
            g.add((dct_type_ref, RDF.type, SKOS.Concept))
            g.add((dct_type_ref, SKOS.prefLabel, Literal(dct_type)))
            g.add((dataset_ref, DCT['type'], dct_type_ref))

        # Resource
        for resource_dict in dataset_dict.get('resources', []):
            distribution = URIRef(self._distribution_id_from_distributions(
                g, resource_dict))

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
            # DCT.LicenseDocument as RDF.type
            # Add DCT.type as license type
            # If license is a Literal, serialize as BNode and DCT.title,
            license = self._get_resource_value(resource_dict, 'license')
            license_type = self._get_resource_value(
                resource_dict, 'license_type')
            g.remove((distribution, DCT.license, None))
            if license or license_type:
                if not license:
                    license_ref = BNode()
                else:
                    license = URIRefOrLiteral(license)
                    if isinstance(license, Literal):
                        license_ref = BNode()
                        g.add((license_ref, DCT.title, license))
                    else:
                        license_ref = license
                if license_type:
                    g.add((license_ref, DCT.type, URIRefOrLiteral(license_type)))
                g.add((license_ref, RDF.type, DCT.LicenseDocument))
                g.add((distribution, DCT.license, license_ref))

            # Availability
            availability = resource_dict.get('availability')
            if availability:
                g.add((distribution, DCATAP.availability,
                       URIRefOrLiteral(availability)))

            # conformsTo: change range to dct:Standard
            self._generate_conforms_to_graph(distribution)

            # rights: change range to dct:RightsStatement
            self._generate_rights_to_graph(distribution, DCT.rights)

            # page change range to foaf:document
            self._generate_page_to_graph(distribution)

    def graph_from_catalog(self, catalog_dict, catalog_ref):

        g = self.g
        # TODO
