import json
from builtins import str

from ckan.plugins import toolkit
from ckanext.dcat.profiles import RDFProfile, URIRefOrLiteral
from ckanext.dcatapedp.profiles.controlled_vocabularies import *
from ckanext.dcatapedp.profiles.namespaces import *
from ckanext.dcatapedp.profiles.utils import (
    unified_resource_format_ckan)
from geomet import InvalidGeoJSONException, wkt
from rdflib import BNode, Literal, URIRef


class DCATAPProfile_2(RDFProfile):

    def time_interval_edp(self, subject, predicate):
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

    def spatial_edp(self, subject, predicate):
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

    def distribution_format_edp(self, subject, normalize_ckan_format=True):
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

    def conforms_to_edp(self, subject):
        conformsToList = []
        for _, _, conforms_to_ref in self.g.triples((subject, DCT.conformsTo, None)):
            conformsToList.append(self._object_value(
                conforms_to_ref, RDFS.label))
        if len(conformsToList) > 0:
            return json.dumps(conformsToList)
        else:
            return None
    

    def generate_conforms_to_graph(self, subject):
        g = self.g
        for _, _, conforms_to in g.triples((subject, DCT.conformsTo, None)):
            conforms_to_ref = BNode()
            g.remove((subject, DCT.conformsTo, conforms_to))
            g.add((conforms_to_ref, RDF.type, DCT.Standard))
            g.add((conforms_to_ref, RDFS.label, Literal(conforms_to)))
            g.add((subject, DCT.conformsTo, conforms_to_ref))



    def add_rdf_type(self, subject, predicate, new_rdf_type):
        g = self.g
        for _, _, object in g.triples((subject, predicate, None)):
            object_ref = URIRefOrLiteral(object)
            if isinstance(object_ref, URIRef):
                g.add((object_ref, RDF.type, new_rdf_type))

    def replace_ancient(self, subject, predicate):
        g = self.g
        for _, _, object in g.triples((subject, predicate, None)):
            g.remove((subject, predicate, object))
            g.add((subject, predicate, URIRefOrLiteral(object)))

    def add_rdf_type_delete_ancient(self, subject, predicate, new_rdf_tpe):
        self.replace_ancient(subject, predicate)
        self.add_rdf_type(subject, predicate, new_rdf_tpe)

    def generate_dependent_datasets_to_graph(self, subject, predicate):
        self.add_rdf_type_delete_ancient(subject, predicate, DCAT['Dataset'])

    def generate_dependent_distribution_to_graph(self, subject, predicate):
        self.add_rdf_type_delete_ancient(subject, predicate, DCAT['Distribution'])        

    def generate_rights_to_graph(self, subject, predicate):
        g = self.g
        access_rights = g.value(subject, predicate)
        if access_rights:
            license_rights_ref = BNode()
            g.remove((subject, predicate, None))
            g.add((license_rights_ref, RDF.type, DCT.RightsStatement))
            g.add((license_rights_ref, RDFS.label, Literal(access_rights)))
            g.add((subject, predicate, license_rights_ref))
