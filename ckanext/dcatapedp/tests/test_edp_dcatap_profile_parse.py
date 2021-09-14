from builtins import str
from builtins import object
import json

from dateutil.parser import parse as parse_date

from geomet import wkt

from rdflib import Graph, URIRef, BNode, Literal

from ckan.plugins import toolkit

from ckanext.dcat.processors import RDFParser
from ckanext.dcatapedp.profiles import (
    DCT, DCAT, DCATAP, ADMS, VCARD, FOAF, SCHEMA, TIME, LOCN, GSP,
    OWL, SKOS, EU_CORPORATE_BODY_SCHEMA_URI)
from rdflib.namespace import Namespace, RDF, XSD


class BaseParseTest(object):

    def _extras(self, element):
        extras = {}
        for extra in element.get('extras'):
            extras[extra['key']] = extra['value']
        return extras

    def _print_graph(self, g):
        print(g.serialize(format="pretty-xml"))


class TestEDPDCATAPProfileSerializeDataset(BaseParseTest):

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

    def _get_base_graph(self):

        g = Graph()

        g.namespace_manager.bind("foaf", FOAF)
        g.namespace_manager.bind("owl", OWL)
        g.namespace_manager.bind("dcatap", DCATAP)
        g.namespace_manager.bind("rdf", RDF)
        g.namespace_manager.bind("dcat", DCAT)
        g.namespace_manager.bind("dct", DCT)
        g.namespace_manager.bind("skos", SKOS)
        g.namespace_manager.bind("vcard", VCARD)
        g.namespace_manager.bind("locn", LOCN)

        dataset_base = self._get_base_dataset()
        dataset_id = dataset_base['id']

        dataset_ref = URIRef('http://example.com/dataset/' + dataset_id)

        g.add((dataset_ref, RDF.type, DCAT.Dataset))
        g.add((dataset_ref, DCT.identifier, Literal(dataset_id)))
        g.add((dataset_ref, DCT.title, Literal(dataset_base['name'])))
        return g, dataset_ref

    def _get_base_graph_with_resource(self):

        g, dataset_ref = self._get_base_graph()

        dataset_base, resource_base = self._get_base_dataset_and_resource()
        dataset_id = dataset_base['id']
        distribution_id = resource_base['id']

        distribution_ref = URIRef(
            'http://example.com/dataset/' + dataset_id + '/distribution/' + distribution_id)

        g.add((dataset_ref, DCAT.distribution, distribution_ref))
        g.add((distribution_ref, RDF.type, DCAT.Distribution))
        g.add((distribution_ref, RDF.type, DCAT.Distribution))
        g.add((distribution_ref, DCT.title, Literal(resource_base['name'])))

        return g, dataset_ref, distribution_ref

    def test_dataset_from_graph(self):

        g, dataset_ref = self._get_base_graph()
        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset_base = self._get_base_dataset()
        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]
        extras = self._extras(dataset)

        assert extras['identifier'] == dataset_base['id']
        assert dataset['title'] == dataset_base['name']

    def test_landing_page(self):

        landing_page_ref = URIRef('http://example.com/landingpageExample.es')

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCAT['landingPage'], landing_page_ref))
        g.add((landing_page_ref, RDF.type, FOAF.Document))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]

        assert dataset['url'] == str(landing_page_ref)

    def test_publisher(self):

        organization_ref = URIRef(
            'http://publications.europa.eu/resource/authority/corporate-body/SPC')

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['publisher'], organization_ref))
        g.add((organization_ref, RDF.type, FOAF.Agent))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['publisher_uri'] == str(organization_ref)

    def test_publisher_not_UE_CORPORATE_BODY(self):

        organization_ref = URIRef('http://example_organization')

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['publisher'], organization_ref))
        g.add((organization_ref, RDF.type, FOAF.Agent))
        schema = URIRef(EU_CORPORATE_BODY_SCHEMA_URI)
        g.add((organization_ref, SKOS.inScheme, schema))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['publisher_uri'] == str(organization_ref)

    def test_contact_point(self):

        contact_ref = URIRef('http://example.com/ContactUri')
        contact_name = 'MaintainerName ExampleSurname'
        contact_email = 'maintainer@email.com'

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCAT['contactPoint'], contact_ref))
        g.add((contact_ref, RDF.type, VCARD.Kind))
        g.add((contact_ref, VCARD['fn'], Literal(contact_name)))
        g.add((contact_ref, VCARD['hasEmail'],
               Literal('mailto:' + contact_email)))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['contact_uri'] == str(contact_ref)
        assert extras['contact_name'] == contact_name
        assert extras['contact_email'] == contact_email

    def test_temporal(self):

        temporal_ref = BNode()
        start_date = '2021-05-25T15:01:07.173973'
        start_date_parsed = parse_date(start_date).isoformat()
        end_date = '2021-06-25T15:01:07.173973'
        end_date_parsed = parse_date(end_date).isoformat()

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['temporal'], temporal_ref))
        g.add((temporal_ref, DCAT['startDate'], Literal(
            start_date_parsed, datatype=XSD.dateTime)))
        g.add((temporal_ref, DCAT['endDate'], Literal(
            end_date_parsed, datatype=XSD.dateTime)))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert str(extras['temporal_start']) == start_date
        assert extras['temporal_end'] == end_date

    def test_spatial(self):

        spatial_uri = URIRef('http://sws.geonames.org/6544494')
        spatial_geom = '{"type": "Polygon", "coordinates": [[[40.4575, -3.7418], [40.4671, -3.6498], [40.3871, -3.6607], [40.3804, -3.8039]]]}'
        spatial_centroid = '{"type": "Point", "coordinates": [40.4231, -3.7623]}'

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['spatial'], spatial_uri))
        g.add((spatial_uri, RDF.type, DCT['Location']))
        g.add((spatial_uri, SKOS['inScheme'],
               URIRef('http://sws.geonames.org')))
        g.add((spatial_uri, DCAT['bbox'], Literal(
            wkt.dumps(json.loads(spatial_geom), decimals=4), datatype=GSP.wktLiteral)))
        g.add((spatial_uri, DCAT['centroid'], Literal(
            wkt.dumps(json.loads(spatial_centroid), decimals=4), datatype=GSP.wktLiteral)))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['spatial_uri'] == str(spatial_uri)
        assert extras['spatial'] == spatial_geom
        assert extras['spatial_centroid'] == spatial_centroid

    def test_graph_from_resource(self):
        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()
        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset_base, resource_base = self._get_base_dataset_and_resource()
        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]
        extras = self._extras(dataset)
        resources = datasets[0].get('resources')

        assert len(resources) == 1

        resource = resources[0]

        assert extras['identifier'] == dataset_base['id']
        assert dataset['title'] == dataset_base['name']
        assert resource['uri'] == str(distribution_ref)
        assert resource['name'] == resource_base['name']

    if toolkit.check_ckan_version(min_version='2.3'):
        
        def test_distribution_format(self):
            resource_format = 'JSON'
            resource_mimetype = 'application/json'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            EU_format_type_json_ref = URIRef(
                'http://publications.europa.eu/resource/authority/file-type/JSON')
            IANA_media_type_json_ref = URIRef(
                'https://www.iana.org/assignments/media-types/application/json')

            g.add((distribution_ref, DCT['format'], EU_format_type_json_ref))
            g.add((EU_format_type_json_ref, RDF['type'], DCT['MediaTypeOrExtent']))

            g.add((distribution_ref, DCAT['mediaType'], IANA_media_type_json_ref))
            g.add((IANA_media_type_json_ref, RDF['type'], DCT['MediaType']))

            p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            p.g = g

            dataset_base, resource_base = self._get_base_dataset_and_resource()
            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_format
            assert resource['mimetype'] == resource_mimetype

        def test_distribution_format_not_mimetype(self):
            resource_format = 'JSON'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            EU_format_type_json_ref = URIRef(
                'http://publications.europa.eu/resource/authority/file-type/JSON')

            g.add((distribution_ref, DCT['format'], EU_format_type_json_ref))
            g.add((EU_format_type_json_ref, RDF['type'], DCT['MediaTypeOrExtent']))

            p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            p.g = g

            dataset_base, resource_base = self._get_base_dataset_and_resource()
            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_format
            assert not 'mimetype' in resource

        def test_distribution_format_not_format(self):

            resource_mimetype = 'application/json'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            IANA_media_type_json_ref = URIRef(
                'https://www.iana.org/assignments/media-types/application/json')

            g.add((distribution_ref, DCAT['mediaType'], IANA_media_type_json_ref))
            g.add((IANA_media_type_json_ref, RDF['type'], DCT['MediaType']))

            p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            p.g = g

            dataset_base, resource_base = self._get_base_dataset_and_resource()
            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_mimetype
            assert resource['mimetype'] == resource_mimetype

        def test_distribution_format_not_format_found_in_EU(self):

            resource_format = 'NotExists'
            resource_mimetype = 'application/json'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            EU_format_type_json_ref = URIRef(
                'http://publications.europa.eu/resource/authority/file-type/' + resource_format)
            IANA_media_type_json_ref = URIRef(
                'https://www.iana.org/assignments/media-types/application/json')

            g.add((distribution_ref, DCT['format'], EU_format_type_json_ref))
            g.add((EU_format_type_json_ref, RDF['type'], DCT['MediaTypeOrExtent']))

            g.add((distribution_ref, DCAT['mediaType'], IANA_media_type_json_ref))
            g.add((IANA_media_type_json_ref, RDF['type'], DCT['MediaType']))

            p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
            p.g = g

            dataset_base, resource_base = self._get_base_dataset_and_resource()
            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_format
            assert resource['mimetype'] == resource_mimetype

    def test_distribution_license(self):

        license_ref = URIRef(
            'http://publications.europa.eu/resource/authority/licence/CC_BY_4_0')
        license_type = URIRef('http://purl.org/adms/licencetype/PublicDomain')

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add((distribution_ref, DCT['license'], license_ref))
        g.add((license_ref, RDF['type'], DCT['LicenseDocument']))
        g.add(((license_ref, DCT['type'], license_type)))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset_base, resource_base = self._get_base_dataset_and_resource()
        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]
        resource_extras = self._extras(resource)

        assert resource['license'] == str(license_ref)
        assert resource_extras['license_type'] == str(license_type)

    def test_distribution_license_literal(self):

        license_name = 'CC_BY_4_0'
        license_type = 'PublicDomain'

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        license_ref = BNode()

        g.add((distribution_ref, DCT['license'], license_ref))
        g.add((license_ref, RDF['type'], DCT['LicenseDocument']))
        g.add(((license_ref, DCT['title'], Literal(license_name))))
        g.add(((license_ref, DCT['type'], Literal(license_type))))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]
        resource_extras = self._extras(resource)

        assert resource['license'] == license_name
        assert resource_extras['license_type'] == license_type

    def test_distribution_license_only(self):

        license_ref = URIRef(
            'http://publications.europa.eu/resource/authority/licence/CC_BY_4_0')

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add((distribution_ref, DCT['license'], license_ref))
        g.add((license_ref, RDF['type'], DCT['LicenseDocument']))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]
        try:
            resource_extras = self._extras(resource)
        except:
            resource_extras = []

        assert resource['license'] == str(license_ref)
        assert not 'license_type' in resource_extras

    def test_distribution_license_type_only(self):

        license_ref = BNode()
        license_type = URIRef('http://purl.org/adms/licencetype/PublicDomain')

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add((distribution_ref, DCT['license'], license_ref))
        g.add((license_ref, RDF['type'], DCT['LicenseDocument']))
        g.add(((license_ref, DCT['type'], license_type)))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset_base, resource_base = self._get_base_dataset_and_resource()
        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]
        resource_extras = self._extras(resource)

        assert not 'license' in resource
        assert resource_extras['license_type'] == str(license_type)

    def test_distribution_availability(self):

        availability = URIRef(
            'http://dcat-ap.de/def/plannedAvailability/stable')

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add((distribution_ref, DCATAP['availability'], availability))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset_base, resource_base = self._get_base_dataset_and_resource()
        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert resource['availability'] == str(availability)

    def test_distribution_availability_literal(self):

        availability = 'stable'

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add(
            (distribution_ref, DCATAP['availability'], Literal(availability)))

        p = RDFParser(profiles=['euro_dcat_ap', 'edp_dcat_ap'])
        p.g = g

        dataset_base, resource_base = self._get_base_dataset_and_resource()
        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert resource['availability'] == availability


# class TestEDPDCATAPProfileSerializeCatalog(BaseSerializeTest):
#     pass
