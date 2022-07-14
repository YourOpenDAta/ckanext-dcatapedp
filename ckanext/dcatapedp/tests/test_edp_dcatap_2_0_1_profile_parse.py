from builtins import str
from builtins import object
import json

from dateutil.parser import parse as parse_date

from geomet import wkt

from rdflib import Graph, URIRef, BNode, Literal

from ckan.plugins import toolkit

from ckanext.dcat.processors import RDFParser

from ckanext.dcatapedp.profiles.namespaces import *
from ckanext.dcatapedp.profiles.controlled_vocabularies.links import *


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
        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
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

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]

        assert dataset['url'] == str(landing_page_ref)

    def test_publisher(self):

        organization_ref = URIRef(
            'http://publications.europa.eu/resource/authority/corporate-body/SPC')
        organization_type = URIRef(
            'http://purl.org/adms/publishertype/Academia-ScientificOrganisation')
            
        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['publisher'], organization_ref))
        g.add((organization_ref, RDF['type'], FOAF.Agent))
        g.add((organization_ref, DCT['type'], organization_type))
        g.add((organization_type, RDF['type'], SKOS['Concept']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['publisher_uri'] == str(organization_ref)
        assert extras['publisher_type'] == str(organization_type)


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

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
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

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
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

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['spatial_uri'] == str(spatial_uri)
        assert extras['spatial'] == spatial_geom
        assert extras['spatial_centroid'] == spatial_centroid

    def test_access_rights(self):

        access_rights_ref = URIRef('http://publications.europa.eu/resource/authority/access-right/RESTRICTED')

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['accessRights'], access_rights_ref))
        g.add((access_rights_ref, RDF.type, DCT['RightsStatement']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]

        extras = self._extras(dataset)
        assert extras['access_rights'] == str(access_rights_ref)

    def test_conforms_to(self):
        conforms_to = '[\"Standard 1\", \"Standard 2\"]'
        conforms_to_list = json.loads(conforms_to)
        conforms_to_ref_0 = BNode()
        conforms_to_ref_1 = BNode()

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT.conformsTo, conforms_to_ref_0))
        g.add((conforms_to_ref_0, RDF.type, DCT.Standard))
        g.add((conforms_to_ref_0, RDFS.label,
               Literal(conforms_to_list[0])))

        g.add((dataset_ref, DCT.conformsTo, conforms_to_ref_1))
        g.add((conforms_to_ref_1, RDF.type, DCT.Standard))
        g.add((conforms_to_ref_1, RDFS.label,
               Literal(conforms_to_list[1])))
        
        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g
        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert len(json.loads(extras['conforms_to'])) == 2
        assert sorted(json.loads(extras['conforms_to'])) == conforms_to_list

    def test_page_documentation(self):
        page_refs = '[\"http://page1\", \"http://page2\"]'
        page_identifier_list = json.loads(page_refs)

        g, dataset_ref = self._get_base_graph()

        for page_ref in page_identifier_list:
            page_ref = URIRef(page_ref)
            g.add((dataset_ref, FOAF['page'], page_ref))
            g.add((page_ref, RDF.type, FOAF['Document']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert len(json.loads(extras['documentation'])) == 2
        assert sorted(json.loads(extras['documentation'])) == page_identifier_list


    def test_language(self):
        language_refs = '[\"http://publications.europa.eu/resource/authority/language/ENG", \"http://publications.europa.eu/resource/authority/language/FRA"]'
        language_identifier_list = json.loads(language_refs)

        g, dataset_ref = self._get_base_graph()

        for language_ref in language_identifier_list:
            language_ref = URIRef(language_ref)
            g.add((dataset_ref, DCT['language'], language_ref))
            g.add((language_ref, RDF.type, DCT['LinguisticSystem']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert len(json.loads(extras['language'])) == 2
        assert sorted(json.loads(extras['language'])) == language_identifier_list

    def test_theme(self):
        theme_refs = '[\"http://publications.europa.eu/resource/authority/data-theme/EDUC", \"http://publications.europa.eu/resource/authority/data-theme/TECH"]'
        theme_identifier_list = json.loads(theme_refs)

        g, dataset_ref = self._get_base_graph()

        for theme_ref in theme_identifier_list:
            theme_ref = URIRef(theme_ref)
            g.add((dataset_ref, DCAT['theme'], theme_ref))
            g.add((theme_ref, RDF.type, SKOS['Concept']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert len(json.loads(extras['theme'])) == 2
        assert sorted(json.loads(extras['theme'])) == theme_identifier_list


    def test_dependent_dataset_distribution(self):
        # test dct:isVersion dct:hasVersion dct:source adms:sample 
        dataset_refs = '[\"http://dataset1\", \"http://dataset2\"]'
        dataset_identifier_list = json.loads(dataset_refs)
        distribution_refs = '[\"http://distribution1\", \"http://distribution2\"]'
        distribution_identifier_list = json.loads(distribution_refs)

        test_itmes = [
            (DCT['isVersionOf'], 'is_version_of', DCAT['Dataset'], dataset_identifier_list),
            (DCT['hasVersion'], 'has_version', DCAT['Dataset'], dataset_identifier_list),
            (DCT['source'], 'source', DCAT['Dataset'], dataset_identifier_list),
            (ADMS['sample'], 'sample', DCAT['Distribution'], distribution_identifier_list)
        ] 

        g, dataset_ref = self._get_base_graph()

        for dcat_object, dataset_dict_prop, rdf_type, values in test_itmes:
            for value_ref in values:
                value_ref = URIRef(value_ref)
                g.add((dataset_ref, dcat_object, value_ref))
                g.add((value_ref, RDF.type, rdf_type))
    
        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g
        datasets = [d for d in p.datasets()]
        # There hare 3 Dataset type: 2 dataset_refs, the main dataset
        assert len(datasets) == len(dataset_identifier_list) + 1
        extraPropsFoundInDictionary = 0
        for dataset in datasets:
            extras = self._extras(dataset)
            for _, dataset_dict_prop, _, values in test_itmes: 
                if dataset_dict_prop in extras:
                    assert len(json.loads(extras[dataset_dict_prop])) == len(values)
                    assert sorted(json.loads(extras[dataset_dict_prop])) == values
                    extraPropsFoundInDictionary += 1
        assert extraPropsFoundInDictionary == len(test_itmes)


    def test_adms_identifier(self):
        adms_identifier = '[\"alternate_identifier_0\", \"alternate_identifier_1\"]'
        adms_identifier_list = json.loads(adms_identifier)
        adms_identifier_ref_0 = BNode()
        adms_identifier_ref_1 = BNode()

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, ADMS.identifier, adms_identifier_ref_0))
        g.add((adms_identifier_ref_0, RDF.type, ADMS.Identifier))
        g.add((adms_identifier_ref_0, SKOS.notation,
               Literal(adms_identifier_list[0])))

        g.add((dataset_ref, ADMS.identifier, adms_identifier_ref_1))
        g.add((adms_identifier_ref_1, RDF.type, ADMS.Identifier))
        g.add((adms_identifier_ref_1, SKOS.notation,
               Literal(adms_identifier_list[1])))
        
        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g
        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert sorted(json.loads(extras['alternate_identifier'])) == adms_identifier_list

    def test_provenance(self):
        provenance_ref = BNode()
        provenance = 'provenance info'

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT.provenance, provenance_ref))
        g.add((provenance_ref, RDF.type, DCT.ProvenanceStatement))
        g.add((provenance_ref, RDFS.label, Literal(provenance)))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['provenance'] == str(provenance)

    # sample: tested in euro_dcat_ap profile
    # source: tested in euro_dcat_ap profile

    def test_dct_type(self):
        dct_type_ref = BNode()
        dct_type = 'dataset'

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['type'], dct_type_ref))
        g.add((dct_type_ref, RDF.type, SKOS.Concept))
        g.add((dct_type_ref, SKOS.prefLabel, Literal(dct_type)))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)

        assert extras['dcat_type'] == str(dct_type)        

    def test_accrual_periodicity(self):

        accrual_periodicity_ref = URIRef('http://purl.org/cld/freq/daily')

        g, dataset_ref = self._get_base_graph()

        g.add((dataset_ref, DCT['accrualPeriodicity'], accrual_periodicity_ref))
        g.add((accrual_periodicity_ref, RDF.type, DCT['Frequency']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]

        extras = self._extras(dataset)
        assert extras['frequency'] == str(accrual_periodicity_ref)
 

    # Resources
    def test_graph_from_resource(self):
        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()
        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
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
            resource_format = 'JSON_LD'
            resource_mimetype = 'application/ld+json'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            EU_format_type_json_ref = URIRef(
                'http://publications.europa.eu/resource/authority/file-type/JSON_LD')
            IANA_media_type_json_ref = URIRef(
                'https://www.iana.org/assignments/media-types/application/ld+json')

            g.add((distribution_ref, DCT['format'], EU_format_type_json_ref))
            g.add((EU_format_type_json_ref, RDF['type'], DCT['MediaTypeOrExtent']))

            g.add((distribution_ref, DCAT['mediaType'], IANA_media_type_json_ref))
            g.add((IANA_media_type_json_ref, RDF['type'], DCT['MediaType']))

            p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
            p.g = g

            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_format
            assert resource['mimetype'] == resource_mimetype

        def test_distribution_format_not_mimetype(self):
            resource_format = 'JSON_LD'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            EU_format_type_json_ref = URIRef(
                'http://publications.europa.eu/resource/authority/file-type/JSON_LD')

            g.add((distribution_ref, DCT['format'], EU_format_type_json_ref))
            g.add((EU_format_type_json_ref, RDF['type'], DCT['MediaTypeOrExtent']))

            p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
            p.g = g

            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_format
            assert not 'mimetype' in resource

        def test_distribution_format_not_format(self):

            resource_mimetype = 'application/ld+json'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            IANA_media_type_json_ref = URIRef(
                'https://www.iana.org/assignments/media-types/application/ld+json')

            g.add((distribution_ref, DCAT['mediaType'], IANA_media_type_json_ref))
            g.add((IANA_media_type_json_ref, RDF['type'], DCT['MediaType']))

            p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
            p.g = g

            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_mimetype
            assert resource['mimetype'] == resource_mimetype

        def test_distribution_format_not_format_found_in_EU(self):

            resource_format = 'NotExists'
            resource_mimetype = 'application/ld+json'

            g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

            EU_format_type_json_ref = URIRef(
                'http://publications.europa.eu/resource/authority/file-type/' + resource_format)
            IANA_media_type_json_ref = URIRef(
                'https://www.iana.org/assignments/media-types/application/ld+json')

            g.add((distribution_ref, DCT['format'], EU_format_type_json_ref))
            g.add((EU_format_type_json_ref, RDF['type'], DCT['MediaTypeOrExtent']))

            g.add((distribution_ref, DCAT['mediaType'], IANA_media_type_json_ref))
            g.add((IANA_media_type_json_ref, RDF['type'], DCT['MediaType']))

            p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
            p.g = g

            dataset = [d for d in p.datasets()][0]
            resource = dataset.get('resources')[0]

            assert resource['format'] == resource_format
            assert resource['mimetype'] == resource_mimetype

    def test_distribution_availability(self):

        availability = URIRef(
            'http://dcat-ap.de/def/plannedAvailability/stable')

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add((distribution_ref, DCATAP['availability'], availability))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert resource['availability'] == str(availability)

    def test_distribution_availability_literal(self):

        availability = 'stable'

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add(
            (distribution_ref, DCATAP['availability'], Literal(availability)))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert resource['availability'] == availability

    def test_distribution_conforms_to(self):
        conforms_to = '[\"Standard distribution 1\", \"Standard distribution 2\"]'
        conforms_to_list = json.loads(conforms_to)
        conforms_to_ref_0 = BNode()
        conforms_to_ref_1 = BNode()

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add((distribution_ref, DCT.conformsTo, conforms_to_ref_0))
        g.add((conforms_to_ref_0, RDF.type, DCT.Standard))
        g.add((conforms_to_ref_0, RDFS.label,
               Literal(conforms_to_list[0])))

        g.add((distribution_ref, DCT.conformsTo, conforms_to_ref_1))
        g.add((conforms_to_ref_1, RDF.type, DCT.Standard))
        g.add((conforms_to_ref_1, RDFS.label,
               Literal(conforms_to_list[1])))
        
        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g
        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert sorted(json.loads(resource['conforms_to'])) == conforms_to_list
    
    def test_distribution_rights(self):

        rights_ref = URIRef('http://publications.europa.eu/resource/authority/access-right/RESTRICTED')

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        g.add((distribution_ref, DCT['rights'], rights_ref))
        g.add((rights_ref, RDF.type, DCT['RightsStatement']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g
        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert resource['rights'] == str(rights_ref)

    def test_distribution_page_documentation(self):
        page_refs = '[\"http://pageDistribution1\", \"http://pageDistribution2\"]'
        page_identifier_list = json.loads(page_refs)

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        for page_ref in page_identifier_list:
            page_ref = URIRef(page_ref)
            g.add((distribution_ref, FOAF['page'], page_ref))
            g.add((page_ref, RDF.type, FOAF['Document']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert len(json.loads(resource['documentation'])) == 2
        assert sorted(json.loads(resource['documentation'])) == page_identifier_list

    def test_distribution_language(self):
        language_refs = '[\"http://publications.europa.eu/resource/authority/language/ENG", \"http://publications.europa.eu/resource/authority/language/FRA"]'
        language_identifier_list = json.loads(language_refs)

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        for language_ref in language_identifier_list:
            language_ref = URIRef(language_ref)
            g.add((distribution_ref, DCT['language'], language_ref))
            g.add((language_ref, RDF.type, DCT['LinguisticSystem']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert len(json.loads(resource['language'])) == 2
        assert sorted(json.loads(resource['language'])) == language_identifier_list

    def test_distribution_status(self):
        status = "http://purl.org/adms/status/Completed"

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        status_ref = URIRef(status)
        g.add((distribution_ref, ADMS['status'], status_ref))
        g.add((status_ref, RDF.type, SKOS['Concept']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert resource['status'] == status

    def test_distribution_license(self):
        license = "http://publications.europa.eu/resource/authority/licence/CC_BY_4_0"

        g, dataset_ref, distribution_ref = self._get_base_graph_with_resource()

        license_ref = URIRef(license)
        g.add((distribution_ref, DCT['license'], license_ref))
        g.add((license_ref, RDF.type, DCT['LicenseDocument']))

        p = RDFParser(profiles=['euro_dcat_ap', 'dcat_ap_2.0.1'])
        p.g = g

        dataset = [d for d in p.datasets()][0]
        resource = dataset.get('resources')[0]

        assert resource['license'] == license

# class TestEDPDCATAPProfileSerializeCatalog(BaseSerializeTest):
#     pass
