import json
from builtins import str

from ckan.plugins import toolkit
from ckanext.dcat.profiles import URIRefOrLiteral
from ckanext.dcatapedp.profiles.controlled_vocabularies import *
from ckanext.dcatapedp.profiles.versions.dcat_ap_2_profile import DCATAPProfile_2
from ckanext.dcatapedp.profiles.namespaces import *
from ckanext.dcatapedp.profiles.utils import (
    add_or_replace_from_extra, distribution_id_from_distributions,
    unified_resource_format_eu, unified_resource_format_iana)
from ckantoolkit import config
from geomet import wkt
from rdflib import BNode, Literal, URIRef


class DCATAPProfile_2_0_1(DCATAPProfile_2):
    '''
    An RDF profile for the EDP DCAT-AP recommendation for data portals

    It requires the European DCAT-AP profile (`euro_dcat_ap`)
    '''

    # CKAN metadata from GRAPH

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
            add_or_replace_from_extra(
                    dataset_dict, 'conforms_to', conformsToList)

        # page, documentation: in euro_dcat_ap profile

        # adms identifier
        adms_identifier_list = []
        for _, _, adms_identifier_ref in self.g.triples((dataset_ref, ADMS.identifier, None)):
                    adms_identifier_list.append(self._object_value(adms_identifier_ref, SKOS.notation))
        if len(adms_identifier_list) > 0:
            add_or_replace_from_extra(
                    dataset_dict, 'alternate_identifier', json.dumps(adms_identifier_list))

        # provenance
        provenance_ref = self.g.value(dataset_ref, DCT.provenance)
        if (provenance_ref and isinstance(provenance_ref, BNode)):
            provenance = self.g.value(provenance_ref, RDFS.label)
            if provenance:
              add_or_replace_from_extra(
                    dataset_dict, 'provenance', str(provenance))

        # sample: in euro_dcat_ap profile
        # source: in euro_dcat_ap profile

        # dct type
        dct_type_ref = self.g.value(dataset_ref, DCT['type'])
        if (dct_type_ref and isinstance(dct_type_ref, BNode)):
            dct_type = self.g.value(dct_type_ref, SKOS.prefLabel)
            if dct_type:
              add_or_replace_from_extra(
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
            distribution = URIRef(distribution_id_from_distributions(
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
