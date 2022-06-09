import ckan.model as model
from ckan.plugins import toolkit
from ckanext.dcat.utils import dataset_id_from_resource, resource_uri
from iso639 import languages
from ckanext.dcatapedp.profiles.namespaces import DCAT, RDF


def unified_resource_format_iana(format):
    '''
    Finds the canonical IANA mimetype for the format
    Returns None if not found 
    '''
    if toolkit.check_ckan_version(min_version='2.3'):
        import ckan.config
        from ckan.lib import helpers
        formats = helpers.resource_formats()
        format_clean = format.lower()
        if format_clean in formats:
            return formats[format_clean][0]
        else:
            return None
    return None

def unified_resource_format_eu(format):
    '''
    Finds the EUROPE file type format (http://publications.europa.eu/resource/authority/file-type/)
    Returns None if not found 
    '''
    if toolkit.check_ckan_version(min_version='2.3'):
        import ckan.config
        from ckan.lib import helpers
        formats = helpers.resource_formats()
        format_clean = format.lower()
        if format_clean in formats:
            # TODO: Extend. Not all the formats fit 
            return formats[format_clean][1]
        else:
            return None
    return None

def unified_resource_format_ckan(format):
    '''
    Finds the ckan format
    Returns None if not found 
    '''
    if toolkit.check_ckan_version(min_version='2.3'):
        import ckan.config
        from ckan.lib import helpers
        formats = helpers.resource_formats()
        format_clean = format.lower()
        if format_clean in formats:
            # TODO: Extend. Not all the formats fit 
            return formats[format_clean][1]
        else:
            return None
    return None


def convert_language(lang):
    '''
    Convert alpha2 language (eg. 'en') to terminology language (eg. 'eng')
    '''

    if not lang:
        return "und"

    try:
        lang_object = languages.get(part1=lang)
        return lang_object.terminology
    except KeyError as ke:
        try:
            lang_object = languages.get(part2b=lang)
            return lang_object.terminology
        except KeyError as ke:
            return ''

def get_earliest_datestamp():
    '''
    Return earliest datestamp of packages as defined in:
    http://www.openarchives.org/OAI/openarchivesprotocol.html#Identify
    '''

    return model.Session.query(model.Package.metadata_modified).\
        order_by(model.Package.metadata_modified).first()[0]


def distribution_id_from_distributions(g, resource_dict):
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


def add_or_replace_from_extra(dictionary, key, value):
    if not 'extras' in dictionary:
        dictionary['extras'] = []
    for extra in dictionary.get('extras', []):
        if extra['key'] == key:
            extra['value'] = value
            return

    dictionary['extras'].append({'key': key, 'value': value})
