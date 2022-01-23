from iso639 import languages

from ckan.plugins import toolkit
import ckan.model as model

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

