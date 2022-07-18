import logging
import os
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IConfigurer, IBlueprint
from flask import Blueprint


from ckan.plugins.toolkit import request

from ckan.lib.base import render
from ckanext.dcatapedp.oaipmh_edp.oaipmh_server import CKANOAIPMHWrapper



from ckan.lib.base import render



log = logging.getLogger(__name__)



def oai_action():
    '''Return the result of the handled request of a batching OAI-PMH
    server implementation.
    '''
    log.info('Entres in the action')
    if 'verb' in request.params:
        verb = request.params['verb'] if request.params['verb'] else None
        if verb:            
            serv = CKANOAIPMHWrapper(5)
            res = serv.handleRequest(request.params)
            #log.info('Response: %s', res)
            resProcessed = serv.handleResponse(res)
            #log.info('Response processed: %s', resProcessed )
            
            #response.headers['content-type'] = 'text/html; charset=utf-8'
            return resProcessed
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
