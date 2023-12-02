<!--

. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.  

.. image:: https://travis-ci.org/YourOpenDAta/ckanext-dcatapedp.svg?branch=master
    :target: https://travis-ci.org/YourOpenDAta/ckanext-dcatapedp

.. image:: https://coveralls.io/repos/YourOpenDAta/ckanext-dcatapedp/badge.svg
  :target: https://coveralls.io/r/YourOpenDAta/ckanext-dcatapedp

.. image:: https://pypip.in/download/ckanext-dcatapedp/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-dcatapedp/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-dcatapedp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dcatapedp/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-dcatapedp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dcatapedp/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-dcatapedp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dcatapedp/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-dcatapedp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dcatapedp/
    :alt: License
-->

# ckanext-dcatapedp <!-- omit in toc -->

CKAN extension for the European Data Portal

- [Requirements](#requirements)
- [DCAT versions included](#dcat-versions-included)
- [Installation](#installation)
- [Development Installation](#development-installation)
- [Running the Tests](#running-the-tests)
- [Mapping CKAN - DCAT AP v x.x.x](#mapping-ckan---dcat-ap-v-xxx)
  - [Catalogue - Organization](#catalogue---organization)
  - [Dataset - Package](#dataset---package)
  - [Distribution - Resource](#distribution---resource)
  - [Agent](#agent)
- [OAI-PMH version 2](#oai-pmh-version-2)
- [Examples](#examples)
  - [Dataset (Package) and Distribution (Resource) CKAN metadata](#dataset-package-and-distribution-resource-ckan-metadata)
  - [Dataset (Package) and Distribution (Resource) DCAT-AP rdf](#dataset-package-and-distribution-resource-dcat-ap-rdf)
  - [Catalogue (Organization) CKAN metadata](#catalogue-organization-ckan-metadata)
  - [Catalogue (Organization) DCAT-AP vx.x.x rdf](#catalogue-organization-dcat-ap-vxxx-rdf)
- [License](#license)

## Requirements

- The extension was developed for CKAN 2.9
- It is based on the [ckanext-dcat extension](https://github.com/ckan/ckanext-dcat "ckanext-dcat extension") v1.1.3


## DCAT versions included

1. 2.0.1
2. 2.1.0

## Installation

1. Install the [ckanext-dcat extension](https://github.com/ckan/ckanext-dcat/blob/master/README.md)

2. Activate your CKAN virtual environment, for example::

        . /usr/lib/ckan/default/bin/activate

3. Download the extension in the CKAN path extensions (e.g. `/usr/lib/ckan/venv/src `):

        git clone https://github.com/YourOpenDAta/ckanext-dcatapedp.git

4. Install the ckanext-dcatapedp Python package into your virtual environment::

        pip install -e ckanext-dcatapedp

5. Active the dcat_ap_x.x.x profile and add the oaipmh_edp plugin  in the `production.ini` file:

        ckanext.dcat.rdf.profiles = euro_dcat_ap dcat_ap_x.x.x (dcat_ap_2.1.0 or dcat_ap.2.0.1)
        ckan.plugins = (other plugins) oaipmh_edp

6. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

         sudo service apache2 reload


<!--## Config Settings

Document any optional config settings here. For example::

    # The minimum number of hours to wait before re-checking a resource
    # (optional, default: 24).
    ckanext.dcatapedp.some_setting = some_default_value
-->



## Development Installation


To install ckanext-dcatapedp for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/YourOpenDAta/ckanext-dcatapedp.git
    cd ckanext-dcatapedp
    python setup.py develop
    pip install -r dev-requirements.txt


## Running the Tests

To run the tests, do::

    pytest --ckan-ini=test.ini ckanext/dcatapedp/tests/


<!--

## Registering ckanext-dcatapedp on PyPI


ckanext-dcatapedp should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-dcatapedp. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags

-->

<!--
## Releasing a New Version of ckanext-dcatapedp

ckanext-dcatapedp is availabe on PyPI as https://pypi.python.org/pypi/ckanext-dcatapedp.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags

-->

## Mapping CKAN - DCAT AP v x.x.x
 - **DCAT prop**: dcat property name
 - **CKAN fields**: field or fields used for the mapping with the DCAT edp profile. CKAN fields are sorted by order of preference in the CKAN metadata
 - **Type**: origin of the dcat mapping being 
   - *O: taken from original profile without modifying it (euro_dcat_ap)*; 
   - *M: taken from the original profile (euro_dcat_ap) modifying it*; 
   - *A: new property added in the dcat_ap_x.x.x profile*
 - **Stored as**: way it is stored in the CKAN instance
 - **Ref. vocab.**: reference vocabularies recommended to use
 - **Notes**: additional information 

### Catalogue - Organization
| DCAT prop. | CKAN fields | Type | Stored as | Ref. vocab. | Notes |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
|   |   |   |   |   |   |
|   |   |   |   |   |   |


### Dataset - Package
| DCAT prop. | CKAN fields | Type | Stored as | Ref. vocab. | Notes |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| dct:identifier | extra:identifier, guid, id | O | text | | |
| dct:description | notes | O | text | | |
| dct:title | title | O | text | | |
| dcat:contactPoint | extra:contact_uri | M | text | | |
| dcat:distribution | resources | O | text | | |
| dcat:keyword | tags | O | list | | |
| dct:publisher | extra:publisher_uri | M | text  | http://publications.europa.eu/resource/authority/corporate-body | |
| dct:spatial | extra:spatial_uri | M | text | http://publications.europa.eu/resource/authority/continent <br/> http://publications.europa.eu/resource/authority/country <br/> http://publications.europa.eu/resource/authority/place <br/> http://sws.geonames.org/ <br/> | |
| dct:temporal | extra:temporal_start + <br/> extra:temporal_end | M | text | | |
| dcat:theme | extra:theme | M | list | http://publications.europa.eu/resource/authority/data-theme | |
| adms:identifier | extra:alternate_identifier | M | list | | |
| adms:sample | extra:sample | M | list | | |
| adms:versionNotes | adms:versionNotes | O | text | | |
| dcat:landingPage | url | M | text | | |
| dct:accessRights | extra:access_rights | M | text | https://publications.europa.eu/resource/authority/access-right (not in the specification) [2.0.1] -> <br/> http://publications.europa.eu/resource/authority/access-right [2.1.0] | |
| dct:accrualPeriodicity | extra:frequency | O | text | http://purl.org/cld/freq  | |
| dct:conformsTo | extra:conforms_to | M | list | | |
| dct:hasVersion | extra:has_version | O | list | | |
| dct:isVersionOf | extra:is_version_of | O | list | | |
| dct:issued | extra:issued, metadata_created | O | text | | |
| dct:language | extra:language | M | list | http://publications.europa.eu/resource/authority/language | |
| dct:modified | extra:modified, <br/> metadata_modified | O | text | | |
| dct:provenance | extra:provenance | M | text | | |
| dct:source | extra:source | M | list | | |
| dct:type | extra:dcat_type | M | text | () -> http://publications.europa.eu/resource/dataset/dataset-type [2.1.0] | |
| foaf:page | extra:documentation | M | list  | | |
| owl:versionInfo | version, extra:dcat_version | O | text | | |


### Distribution - Resource

| DCAT prop. | CKAN fields | Type | Stored as | Ref. vocab. | Notes |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| dcat:accessURL | resource:access_url | O | text |  |  |
| dcatap:availability | resource:availability | A | text | http://data.europa.eu/r5r/availability/ <br/> https://www.dcat-ap.de/def/plannedAvailability/1_0.html -> [2.0.1] <br/> http://publications.europa.eu/resource/authority/planned-availability -> [2.1.0] |  |
| dct:description | resource:description | O | text |  |  |
| dct:format | resource:format | M | text | http://publications.europa.eu/resource/authority/file-type |  |
| dct:license | resource:license | M | text | TODO:include |  |
| adms:status | resource:status | M | text | http://purl.org/adms/status |  |
| dcat:byteSize | resource:size | O | number |  |  |
| dcat:downloadURL | resource:download_url | O | text |  |  |
| dcat:mediaType | resource:mimetype  | M | text | http://www.iana.org/assignments/media-types/media-types.xhtml |  |
| dct:conformsTo | resource:conforms_to | M | list |  |  |
| dct:issued | resource:issued | O | text |  |  |
| dct:language | resource:languague | M | list | http://publications.europa.eu/resource/authority/language |  |
| dct:modified | resource:modified | O | text |  |  |
| dct:rights | resource:rights | M | text | https://publications.europa.eu/resource/authority/access-right (not in the specification)  |  |
| dct:title | resource:name | O | text |  |  |
| foaf:page | resurce:documentation | M | list |  |  |
  |  |


### Agent

| DCAT prop. | CKAN fields | Type | Stored as | Ref. vocab. | Notes |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
|   |   |   |   |   |   |
|   |   |   |   |   |   |

## OAI-PMH version 2 

1. Create example of data
   
      git ckan -c /etc/ckan/production.ini seed basic

  
2. Examples of petitions
  - https://{ckan-instance-host}/oai?verb=Identify
  - https://{ckan-instance-host}/oai?verb=ListMetadataFormats
  - https://{ckan-instance-host}/oai?verb=ListSets
  - **https://{ckan-instance-host}/oai?verb=ListRecords&metadataPrefix=dcat**
  - https://{ckan-instance-host}/oai?verb=ListIdentifiers&metadataPrefix=dcat&set=example_org
  - https://{ckan-instance-host}/oai?verb=GetRecord&identifier=ce3f7074-15b7-44ab-a2b9-85e26dc17f67&metadataPrefix=dcat



## Examples

### Dataset (Package) and Distribution (Resource) CKAN metadata

- Original profile (`euro_dcat_ap`): 

- DCAT-AP v x.x.x (`euro_dcat_ap` `dcat_ap_x.x.x`): [ckan_dataset_edp_x_x_x.json](examples/ckan_dataset_edp_x_x_x.json)


### Dataset (Package) and Distribution (Resource) DCAT-AP rdf
- Original profile (`euro_dcat_ap`): [ckan_dataset_edp_original.rdf](examples/ckan_dataset_edp_original.rdf)

- DCAT-AP vx.x.x (`euro_dcat_ap` `dcat_ap_x.x.x`): [ckan_dataset_edp_2_0_1.rdf](examples/ckan_dataset_edp_2_0_1.rdf)


### Catalogue (Organization) CKAN metadata

### Catalogue (Organization) DCAT-AP vx.x.x rdf


## License

ckandext-dcatapedp is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

[http://www.fsf.org/licensing/licenses/agpl-3.0.html](http://www.fsf.org/licensing/licenses/agpl-3.0.html)
