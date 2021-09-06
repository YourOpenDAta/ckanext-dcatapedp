from ckan.plugins import toolkit

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
