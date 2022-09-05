
from ckanext.dcatapedp.profiles.versions.dcat_ap_2_0_1_profile import DCATAPProfile_2_0_1


class DCATAPProfile_2_1_0(DCATAPProfile_2_0_1):
    '''
    An RDF profile for the EDP DCAT-AP recommendation for data portals

    It requires the European DCAT-AP profile (`euro_dcat_ap`)
    '''

    # CKAN metadata from GRAPH

    def parse_dataset(self, dataset_dict, dataset_ref):
       super().parse_dataset(dataset_dict, dataset_ref)

    # GRAPH from CKAN metadata

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        super().graph_from_dataset(dataset_dict, dataset_ref)

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        super().graph_from_catalog(catalog_dict, catalog_ref)
