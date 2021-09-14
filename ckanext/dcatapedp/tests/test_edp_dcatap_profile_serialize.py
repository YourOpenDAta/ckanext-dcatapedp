from builtins import str
from builtins import object
import json

from dateutil.parser import parse as parse_date

from geomet import wkt

from rdflib import URIRef, BNode, Literal

from ckantoolkit.tests import helpers, factories

from ckan.plugins import toolkit

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcatapedp.profiles import (
    DCT, DCAT, DCATAP, ADMS, VCARD, FOAF, SCHEMA, TIME, LOCN, GSP,
    SKOS, EU_CORPORATE_BODY_SCHEMA_URI, GEO_SCHEMA_URI, GEOJSON_IMT)
from rdflib.namespace import Namespace, RDF, XSD, RDFS


class BaseSerializeTest(object):

    def _extras(self, dataset):
        extras = {}
        for extra in dataset.get('extras'):
            extras[extra['key']] = extra['value']
        return extras

    def _triples(self, graph, subject, predicate, _object, data_type=None):

        if not (isinstance(_object, URIRef) or isinstance(_object, BNode) or _object is None):
            if data_type:
                _object = Literal(_object, datatype=data_type)
            else:
                _object = Literal(_object)
        triples = [t for t in graph.triples((subject, predicate, _object))]
        return triples

    def _triple(self, graph, subject, predicate, _object, data_type=None):
        triples = self._triples(graph, subject, predicate, _object, data_type)
        return triples[0] if triples else None


class TestEDPDCATAPProfileSerializeDataset(BaseSerializeTest):

    def _get_base_dataset(self):

        dataset = {
            'id': 'cf3dcff7-34ae-4fab-a202-2f17e3153b2f',
            'name': 'examplepackage',
            'extras': []
        }
        return dataset

    def _get_base_dataset_and_resource(self):

        dataset = self._get_base_dataset()
        resource = {
            'id': '9871734c-d261-4d66-96de-cfce6ddf8a31',
            'name': 'Example resource',
            'package_id': 'cf3dcff7-34ae-4fab-a202-2f17e3153b2f',
            'extras': []
        }
        dataset['resources'] = [resource]
        return dataset, resource

    def test_graph_from_dataset(self):

        dataset = self._get_base_dataset()

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        assert str(dataset_ref) == utils.dataset_uri(dataset)

    def test_landing_page(self):

        dataset = self._get_base_dataset()
        dataset['url'] = 'http://example.com/landingpageExample.es'

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        landing_page = self._triple(
            g, dataset_ref, DCAT.landingPage, URIRef(dataset['url']))[2]
        assert landing_page
        assert self._triple(g, landing_page, RDF.type, FOAF.Document)

    def test_publisher(self):

        dataset = self._get_base_dataset()
        dataset['extras'].append(
            {
                'key': 'publisher_uri',
                'value': 'http://publications.europa.eu/resource/authority/corporate-body/SPC'
            }
        )

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert str(publisher) == extras['publisher_uri']

        assert self._triple(g, publisher, RDF.type, FOAF.Agent)
        assert not self._triple(g, publisher, RDF.type, FOAF.Organization)

        assert not self._triple(g, publisher, SKOS.inScheme, None)

    def test_publisher_not_UE_CORPORATE_BODY(self):

        dataset = self._get_base_dataset()
        dataset['extras'].append(
            {
                'key': 'publisher_uri',
                'value': 'http://example.com/publisher'
            }
        )

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert str(publisher) == extras['publisher_uri']

        assert self._triple(g, publisher, RDF.type, FOAF.Agent)
        assert not self._triple(g, publisher, RDF.type, FOAF.Organization)

        schema = URIRef(EU_CORPORATE_BODY_SCHEMA_URI)
        assert self._triple(g, publisher, SKOS.inScheme, schema)

    def test_contact_point(self):

        dataset = self._get_base_dataset()
        dataset['extras'].extend([
            {
                'key': 'contact_email',
                'value': 'maintainer@email.com'
            },
            {
                'key': 'contact_name',
                'value': 'MaintainerName ExampleSurname'
            },
            {
                'key': 'contact_uri',
                'value': 'http://example.com/ContactUri'
            }
        ])

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        contactPoint = self._triple(
            g, dataset_ref, DCAT.contactPoint, URIRef(extras['contact_uri']))[2]
        assert contactPoint
        assert self._triple(g, contactPoint, RDF.type, VCARD.Kind)
        assert self._triple(g, contactPoint, VCARD.fn, extras['contact_name'])
        assert self._triple(g, contactPoint, VCARD['hasEmail'], URIRef(
            'mailto:' + extras['contact_email']))

    def test_temporal(self):

        dataset = self._get_base_dataset()
        dataset['extras'].extend([
            {
                'key': 'temporal_end',
                'value': '2021-06-25T15:01:07.173973'
            },
            {
                'key': 'temporal_start',
                'value': '2021-05-25T15:01:07.173973'
            }
        ])

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        temporal = self._triple(g, dataset_ref, DCT.temporal, None)[2]
        assert temporal

        assert self._triple(g, temporal, RDF.type, DCT.PeriodOfTime)
        assert self._triple(g, temporal, DCAT.startDate, parse_date(
            extras['temporal_start']).isoformat(), XSD.dateTime)
        assert self._triple(g, temporal, DCAT.endDate, parse_date(
            extras['temporal_end']).isoformat(), XSD.dateTime)
        assert not self._triple(g, temporal, SCHEMA.startDate, None)
        assert not self._triple(g, temporal, SCHEMA.endDate, None)

    def test_spatial(self):

        dataset = self._get_base_dataset()
        dataset['extras'].extend([
            {
                'key': 'spatial',
                'value': '{"type": "Polygon", "coordinates": [[[40.457569, -3.741816], [40.467191, -3.649810], [40.387186, -3.660789], [40.380491, -3.803974]]]}'
            },
            {
                'key': 'spatial_centroid',
                'value': '{"type": "Point", "coordinates": [40.423123, -3.762345]}'
            },
            {
                'key': 'spatial_uri',
                'value': 'http://sws.geonames.org/6544494'
            }
        ])

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert str(spatial) == extras['spatial_uri']

        assert self._triple(g, spatial, RDF.type, DCT.Location)

        # if uri is from geonames
        schema = URIRef(GEO_SCHEMA_URI)
        assert self._triple(g, spatial, SKOS.inScheme, schema)

        assert self._triple(g, spatial, DCAT.bbox, None)
        assert not self._triple(g, spatial, LOCN.geometry, None)

        wkt_geom = wkt.dumps(json.loads(extras['spatial']), decimals=4)
        assert self._triple(g, spatial, DCAT.bbox, wkt_geom, GSP.wktLiteral)

        wkt_spatial = wkt.dumps(json.loads(
            extras['spatial_centroid']), decimals=4)
        assert self._triple(g, spatial, DCAT.centroid,
                            wkt_spatial, GSP.wktLiteral)

    def test_spatial_uri_not_GEO_SCHEMA(self):

        dataset = self._get_base_dataset()
        dataset['extras'].append(
            {
                'key': 'spatial_uri',
                'value': 'http://example.com/spatial'
            }
        )
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert str(spatial) == extras['spatial_uri']

        assert self._triple(g, spatial, RDF.type, DCT.Location)

        # if uri is from geonames
        schema = URIRef(GEO_SCHEMA_URI)
        assert not self._triple(g, spatial, SKOS.inScheme, schema)

    def test_spatial_no_wkt(self):

        dataset = self._get_base_dataset()
        dataset['extras'].extend([
            {
                'key': 'spatial',
                'value': 'NoWKT'
            },
            {
                'key': 'spatial_centroid',
                'value': 'NoWKT'
            }
        ])
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial

        assert self._triple(g, spatial, RDF.type, DCT.Location)

        assert not self._triple(g, spatial, DCAT.bbox, None)
        assert self._triple(g, spatial, LOCN.geometry,
                            extras['spatial'], GEOJSON_IMT)

        assert not self._triple(g, spatial, DCAT.centroid, None)

    def test_graph_from_resource(self):

        dataset = self._get_base_dataset()
        dataset['resources'] = [
            {
                'id': '9871734c-d261-4d66-96de-cfce6ddf8a31',
                'name': 'Example resource',
                "package_id": "cf3dcff7-34ae-4fab-a202-2f17e3153b2f",
            },
            {
                'id': '6871894c-d261-4d66-96de-adce6ddf8a32',
                'name': 'Example resource two',
                "package_id": "cf3dcff7-34ae-4fab-a202-2f17e3153b2f",
            }
        ]

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)

        assert len(self._triples(g, dataset_ref, DCAT.distribution, None)) == 2

        for resource in dataset['resources']:
            distribution = self._triple(g,
                                        dataset_ref,
                                        DCAT.distribution,
                                        URIRef(utils.resource_uri(resource)))[2]

            assert self._triple(g, distribution, RDF.type, DCAT.Distribution)

    if toolkit.check_ckan_version(min_version='2.3'):

        def test_distribution_mediaType_with_mimetype(self):
            dataset, resource = self._get_base_dataset_and_resource()
            resource['mimetype'] = 'application/json'

            s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            g = s.g
            dataset_ref = s.graph_from_dataset(dataset)
            distribution = self._triple(
                g, dataset_ref, DCAT.distribution, None)[2]
            assert str(distribution) == utils.resource_uri(resource)

            IANA_media_type_json = 'https://www.iana.org/assignments/media-types/application/json'
            media_type = self._triple(
                g, distribution, DCAT.mediaType, URIRef(IANA_media_type_json))[2]
            assert media_type
            assert self._triple(g, media_type, RDF.type, DCT.MediaType)

        def test_distribution_mediaType_with_format(self):
            dataset, resource = self._get_base_dataset_and_resource()
            resource['format'] = 'JSON'

            s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            g = s.g
            dataset_ref = s.graph_from_dataset(dataset)
            distribution = self._triple(
                g, dataset_ref, DCAT.distribution, None)[2]
            assert str(distribution) == utils.resource_uri(resource)

            IANA_media_type_json = 'https://www.iana.org/assignments/media-types/application/json'
            media_type = self._triple(
                g, distribution, DCAT.mediaType, URIRef(IANA_media_type_json))[2]
            assert media_type
            assert self._triple(g, media_type, RDF.type, DCT.MediaType)

        def test_distribution_mediaType_not_exist(self):
            dataset, resource = self._get_base_dataset_and_resource()
            resource['mimetype'] = 'NOTEXIST'

            s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            g = s.g
            dataset_ref = s.graph_from_dataset(dataset)
            distribution = self._triple(
                g, dataset_ref, DCAT.distribution, None)[2]
            assert str(distribution) == utils.resource_uri(resource)

            # If not found in IANA media types it uses the default definition from euro_dcat_ap profile
            media_type = self._triple(
                g, distribution, DCAT.mediaType, resource['mimetype'])[2]
            assert media_type

        def test_distribution_format_with_mimetype(self):
            dataset, resource = self._get_base_dataset_and_resource()
            resource['mimetype'] = 'application/json'

            s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            g = s.g
            dataset_ref = s.graph_from_dataset(dataset)
            distribution = self._triple(
                g, dataset_ref, DCAT.distribution, None)[2]
            assert str(distribution) == utils.resource_uri(resource)

            EU_format_type_json = 'http://publications.europa.eu/resource/authority/file-type/JSON'
            format_type = self._triple(
                g, distribution, DCT['format'], URIRef(EU_format_type_json))[2]
            assert format_type
            assert self._triple(g, format_type, RDF.type,
                                DCT.MediaTypeOrExtent)

        def test_distribution_format_with_format(self):
            dataset, resource = self._get_base_dataset_and_resource()
            resource['format'] = 'JSON'

            s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            g = s.g
            dataset_ref = s.graph_from_dataset(dataset)
            distribution = self._triple(
                g, dataset_ref, DCAT.distribution, None)[2]
            assert str(distribution) == utils.resource_uri(resource)

            EU_format_type_json = 'http://publications.europa.eu/resource/authority/file-type/JSON'
            format_type = self._triple(
                g, distribution, DCT['format'], URIRef(EU_format_type_json))[2]
            assert format_type
            assert self._triple(g, format_type, RDF.type,
                                DCT.MediaTypeOrExtent)

        def test_distribution_format_not_exist(self):
            dataset, resource = self._get_base_dataset_and_resource()
            resource['format'] = 'NOTEXIST'

            s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            g = s.g
            dataset_ref = s.graph_from_dataset(dataset)
            distribution = self._triple(
                g, dataset_ref, DCAT.distribution, None)[2]
            assert str(distribution) == utils.resource_uri(resource)

            # If not found in EU format types it uses the default definition from euro_dcat_ap profile
            format_type = self._triple(
                g, distribution, DCT['format'], resource['format'])[2]
            assert format_type

        def test_distribution_mediaType_and_format_with_mimetype_and_format(self):
            dataset, resource = self._get_base_dataset_and_resource()
            resource['mimetype'] = 'application/json'
            resource['format'] = 'CSV'

            s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            g = s.g
            dataset_ref = s.graph_from_dataset(dataset)
            distribution = self._triple(
                g, dataset_ref, DCAT.distribution, None)[2]
            assert str(distribution) == utils.resource_uri(resource)

            IANA_media_type_json = 'https://www.iana.org/assignments/media-types/application/json'
            EU_format_type_csv = 'http://publications.europa.eu/resource/authority/file-type/CSV'

            # Priority for mimetype in mediaType
            media_type = self._triple(
                g, distribution, DCAT.mediaType, URIRef(IANA_media_type_json))[2]
            assert media_type
            assert not self._triple(
                g, distribution, DCAT.mediaType, URIRef(EU_format_type_csv))
            assert self._triple(g, media_type, RDF.type, DCT.MediaType)

            # Priority for format in format
            format_type = self._triple(
                g, distribution, DCT['format'], URIRef(EU_format_type_csv))[2]
            assert format_type
            assert not self._triple(
                g, distribution, DCT['format'], URIRef(IANA_media_type_json))
            assert self._triple(g, format_type, RDF.type,
                                DCT.MediaTypeOrExtent)

    def test_distribution_license(self):

        dataset, resource = self._get_base_dataset_and_resource()
        resource['license'] = 'http://publications.europa.eu/resource/authority/licence/CC_BY_4_0'
        resource['extras'].append({
            "key": "license_type",
            "value": "http://purl.org/adms/licencetype/PublicDomain"
        })

        extras = self._extras(resource)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        license = URIRef(resource['license'])
        license_type = URIRef(extras['license_type'])
        assert self._triple(g, distribution, DCT.license, license)
        assert self._triple(g, license, RDF.type, DCT.LicenseDocument)
        assert self._triple(g, license, DCT.type, URIRef(license_type))

    def test_distribution_license_literal(self):

        dataset, resource = self._get_base_dataset_and_resource()
        resource['license'] = 'CC_BY_4_0'
        resource['extras'].append({
            "key": "license_type",
            "value": "PublicDomain"
        })

        extras = self._extras(resource)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        license = self._triple(g, distribution, DCT.license, None)[2]
        assert isinstance(license, BNode)
        assert self._triple(g, license, RDF.type, DCT.LicenseDocument)
        assert self._triple(g, license, DCT.title,
                            Literal(resource['license']))
        assert self._triple(g, license, DCT.type,
                            Literal(extras['license_type']))

    def test_distribution_license_only(self):

        dataset, resource = self._get_base_dataset_and_resource()
        resource['license'] = 'http://publications.europa.eu/resource/authority/licence/CC_BY_4_0'

        extras = self._extras(resource)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        license = URIRef(resource['license'])
        assert self._triple(g, distribution, DCT.license, license)
        assert self._triple(g, license, RDF.type, DCT.LicenseDocument)
        assert not self._triple(g, license, DCT.type, None)

    def test_distribution_license_type_only(self):

        dataset, resource = self._get_base_dataset_and_resource()
        resource['extras'].append({
            "key": "license_type",
            "value": "http://purl.org/adms/licencetype/PublicDomain"
        })

        extras = self._extras(resource)

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        license = self._triple(g, distribution, DCT.license, None)[2]
        license_type = URIRef(extras['license_type'])
        assert isinstance(license, BNode)
        assert self._triple(g, license, RDF.type, DCT.LicenseDocument)
        assert self._triple(g, license, DCT.type, URIRef(license_type))

    def test_distribution_availability(self):

        dataset, resource = self._get_base_dataset_and_resource()
        resource['availability'] = "http://dcat-ap.de/def/plannedAvailability/stable"

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        assert self._triple(g, distribution, DCATAP.availability,
                            URIRef(resource['availability']))

    def test_distribution_availability_literal(self):

        dataset, resource = self._get_base_dataset_and_resource()
        resource['availability'] = "stable"

        s = RDFSerializer(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        g = s.g
        dataset_ref = s.graph_from_dataset(dataset)
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        assert self._triple(
            g, distribution, DCATAP.availability, resource['availability'])


class TestEDPDCATAPProfileSerializeCatalog(BaseSerializeTest):
    pass
