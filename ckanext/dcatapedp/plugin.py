import logging
import os
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IConfigurer, IBlueprint
from flask import Blueprint

import oaipmh.metadata as oaimd
import oaipmh.server as oaisrv
from ckan.plugins.toolkit import request


from ckan.lib.base import render
from ckanext.dcatapedp.oaipmh_edp.oaipmh_server import CKANServer
from ckanext.dcatapedp.oaipmh_edp.rdftools import rdf_reader, dcat2rdf_writer

import six


from ckan.lib.base import render



log = logging.getLogger(__name__)

def mixed(multi_dict):
    u'''Return a dict with values being lists if they have more than one
        item or a string otherwise
    '''
    out = {}
    for key, value in six.iteritems(multi_dict.to_dict(flat=False)):
        out[key] = value[0] if len(value) == 1 else value
    return out

def oai_action():
    '''Return the result of the handled request of a batching OAI-PMH
    server implementation.
    '''
    log.error('Entra')
    if 'verb' in request.params:
        verb = request.params['verb'] if request.params['verb'] else None
        if verb:            
            client = CKANServer()
            metadata_registry = oaimd.MetadataRegistry()
            metadata_registry.registerReader('oai_dc', oaimd.oai_dc_reader)
            metadata_registry.registerWriter('oai_dc', oaisrv.oai_dc_writer)
            metadata_registry.registerReader('rdf', rdf_reader)
            metadata_registry.registerWriter('rdf', dcat2rdf_writer)
            metadata_registry.registerReader('dcat', rdf_reader)
            metadata_registry.registerWriter('dcat', dcat2rdf_writer)
            serv = oaisrv.BatchingServer(client,
                                            metadata_registry=metadata_registry,
                                            resumption_batch_size=10)
            parms = mixed(request.params)
            res = serv.handleRequest(parms)
            #response.headers['content-type'] = 'text/html; charset=utf-8'
            return res
    else:
        #TODO: return error no verb try with no verb
        return render('oaipmh_edp/oaipmh.html')


class OAIPMHPlugin(SingletonPlugin):
    '''OAI-PMH plugin, maps the controller and uses the template configuration
    stanza to have the template render in case there is no parameters to the
    interface.
    '''
    implements(IBlueprint)
    implements(IConfigurer)

    def update_config(self, config):
        """This IConfigurer implementation causes CKAN to look in the
        ```public``` and ```templates``` directories present in this
        package for any customisations.

        It also shows how to set the site title here (rather than in
        the main site .ini file), and causes CKAN to use the
        customised package form defined in ``package_form.py`` in this
        directory.
        """
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        template_dir = os.path.join(rootdir, 'ckanext',
                                    'dcatapedp', 'templates')
        config['extra_template_paths'] = ','.join([template_dir, config.get('extra_template_paths', '')])

    def get_blueprint(self):
        '''Map the controller to be used for OAI-PMH.
        '''
        
        blueprint = Blueprint('oaipmh_edp', self.__module__)
        rules = [
            ('/oai', 'oai_action', oai_action),
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
