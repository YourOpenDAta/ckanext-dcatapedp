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
`TODO: Include badges`

CKAN extension for the European Data Portal

- [Requirements](#requirements)
- [Installation](#installation)
- [Development Installation](#development-installation)
- [Running the Tests](#running-the-tests)
- [Mapping CKAN - DCAT AP v 2.0.1](#mapping-ckan---dcat-ap-v-201)
  - [Catalogue - Organization](#catalogue---organization)
  - [Dataset - Package](#dataset---package)
  - [Distribution - Resource](#distribution---resource)
  - [Agent](#agent)
- [OAI-PMH version 2](#oai-pmh-version-2)
- [Examples](#examples)
  - [Dataset (Package) and Distribution (Resource) CKAN metadata](#dataset-package-and-distribution-resource-ckan-metadata)
  - [Dataset (Package) and Distribution (Resource) DCAT-AP v2.0.1 rdf](#dataset-package-and-distribution-resource-dcat-ap-v201-rdf)
  - [Catalogue (Organization) CKAN metadata](#catalogue-organization-ckan-metadata)
  - [Catalogue (Organization) DCAT-AP v2.0.1 rdf](#catalogue-organization-dcat-ap-v201-rdf)
- [License](#license)

## Requirements

- The extension was developed for CKAN 2.8 `TODO: test in other versions`
- It is based on the [ckanext-dcat extension](https://github.com/ckan/ckanext-dcat "ckanext-dcat extension")




## Installation

1. Install the [ckanext-dcat extension](https://github.com/ckan/ckanext-dcat/blob/master/README.md)

2. Activate your CKAN virtual environment, for example::

        . /usr/lib/ckan/default/bin/activate

3. Download the extension in the CKAN path extensions (e.g. `/usr/lib/ckan/venv/src `):

        git clone https://github.com/YourOpenDAta/ckanext-dcatapedp.git

4. Install the ckanext-dcatapedp Python package into your virtual environment::

        pip install -e ckanext-dcatapedp

5. Active the edp_dcat_ap profile and add the oaipmh_edp plugin  in the `production.ini` file:

        ckanext.dcat.rdf.profiles = euro_dcat_ap edp_dcat_ap
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

## Mapping CKAN - DCAT AP v 2.0.1
 - **DCAT prop**: dcat property name
 - **CKAN fields**: field or fields used for the mapping with the DCAT edp profile. CKAN fields are sorted by order of preference in the CKAN metadata
 - **Type**: origin of the dcat mapping being 
   - *O: taken from original profile without modifying it (euro_dcat_ap)*; 
   - *M: taken from the original profile (euro_dcat_ap) modifying it*; 
   - *A: new property added in the edp_dcat_ap profile*
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
| dcat:theme | extra:theme | O | list | http://publications.europa.eu/resource/authority/data-theme | |
| adms:identifier | extra:alternate_identifier | M | list | | |
| adms:sample | extra:sample | M | list | | |
| adms:versionNotes | adms:versionNotes | O | text | | |
| dcat:landingPage | url | M | text | | |
| dct:accessRights | extra:access_rights | M | text | | |
| dct:accrualPeriodicity | extra:frequency | O | text | http://purl.org/cld/freq  | |
| dct:conformsTo | extra:conforms_to | M | list | | |
| dct:hasVersion | extra:has_version | O | list | | |
| dct:isVersionOf | extra:is_version_of | O | list | | |
| dct:issued | extra:issued, metadata_created | O | text | | |
| dct:language | extra:language | O | list | http://publications.europa.eu/resource/authority/language | |
| dct:modified | extra:modified, <br/> metadata_modified | O | text | | |
| dct:provenance | extra:provenance | M | text | | |
| dct:source | extra:source | M | list | | |
| dct:type | extra:dcat_type | M | text | | |
| foaf:page | extra:documentation | M | list  | | |
| owl:versionInfo | version, extra:dcat_version | O | text | | |


### Distribution - Resource

| DCAT prop. | CKAN fields | Type | Stored as | Ref. vocab. | Notes |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| dcat:accessURL | resource:access_url | O | text |  |  |
| dcatap:availability | resource:availability | A | text | http://data.europa.eu/r5r/availability/ <br/> https://www.dcat-ap.de/def/plannedAvailability/1_0.html |  |
| dct:description | resource:description | O | text |  |  |
| dct:format | resource:format | M | text | http://publications.europa.eu/resource/authority/file-type |  |
| dct:license | resource:license + <br/>  resource:license_type | M (license) <br/> A (license_type) | text | http://purl.org/adms/licencetype/ (license_type)  |  |
| adms:status | resource:status | O | text | http://purl.org/adms/status |  |
| dcat:byteSize | resource:size | O | number |  |  |
| dcat:downloadURL | resource:download_url | O | text |  |  |
| dcat:mediaType | resource:mimetype  | M | text | http://www.iana.org/assignments/media-types/media-types.xhtml |  |
| dct:conformsTo | resource:conforms_to | M | list |  |  |
| dct:issued | resource:issued | O | text |  |  |
| dct:language | resource:languague | O | list | http://publications.europa.eu/resource/authority/language |  |
| dct:modified | resource:modified | O | text |  |  |
| dct:rights | resource:rights | M | text |  |  |
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
  - https://{ckan-instance-host}/oai?verb=ListRecords&metadataPrefix=dcat
  - https://{ckan-instance-host}/oai?verb=ListIdentifiers&metadataPrefix=dcat&set=example_org
  - https://{ckan-instance-host}/oai?verb=GetRecord&identifier=ce3f7074-15b7-44ab-a2b9-85e26dc17f67&metadataPrefix=dcat



## Examples

### Dataset (Package) and Distribution (Resource) CKAN metadata

```json
{
  "license_title": "Creative Commons Attribution",
  "maintainer": "",
  "relationships_as_object": [],
  "private": false,
  "maintainer_email": "",
  "num_tags": 2,
  "id": "cf3dcff7-34ae-4fab-a202-2f17e3153b2f",
  "uri": "http://example_dataset",
  "metadata_created": "2021-07-08T11:31:11.500592",
  "metadata_modified": "2021-07-08T12:08:15.177991",
  "author": "",
  "author_email": "",
  "state": "active",
  "version": "2.0",
  "creator_user_id": "e7d900d6-f2f5-4e9e-abbc-ac96cddcb78e",
  "num_resources": 1,
  "tags": [
    {
      "vocabulary_id": null,
      "state": "active",
      "display_name": "newTag",
      "id": "70264ca0-c848-4e84-801a-a3470bcd0127",
      "name": "newTag"
    },
    {
      "vocabulary_id": null,
      "state": "active",
      "display_name": "newTag2",
      "id": "6665c96c-f1a3-4f6c-a4e0-123909f81eb7",
      "name": "newTag2"
    }
  ],
  "groups": [],
  "license_id": "cc-by",
  "relationships_as_subject": [],
  "organization": {
    "description": "",
    "created": "2021-07-08T11:30:34.342878",
    "title": "exampleorg",
    "name": "exampleorg",
    "is_organization": true,
    "state": "active",
    "image_url": "",
    "revision_id": "8f5a5d59-122e-409c-a3ce-f08821699108",
    "type": "organization",
    "id": "fbdbf159-fe3d-4448-b586-421665dff216",
    "approval_status": "approved"
  },
  "name": "examplepackage",
  "isopen": true,
  "url": "http://localhost/landingpageExample.es",
  "notes": "Description example of dataset test",
  "owner_org": "fbdbf159-fe3d-4448-b586-421665dff216",
  "license_url": "http://www.opendefinition.org/licenses/cc-by",
  "title": "examplepackage",
  "revision_id": "4785b854-df04-4a61-b9a5-609fa6f15458",
  "extras": [
    {
      "key": "contact_email",
      "value": "maintainer@email.com"
    },
    {
      "key": "contact_name",
      "value": "MaintainerName ExampleSurname"
    },
    {
      "key": "contact_uri",
      "value": "http://localhost/ContactUri"
    },
    {
      "key": "publisher_type",
      "value": "http://purl.org/adms/publishertype/Academia-ScientificOrganisation"
    },
    {
      "key": "publisher_uri",
      "value": "http://publications.europa.eu/resource/authority/corporate-body/SPC"
    },
    {
      "key": "spatial",
      "value": "{\"type\": \"Polygon\", \"coordinates\": [[[175.0, 17.5], [-65.5, 17.5], [-65.5, 72.0], [175.0, 72.0], [175.0, 17.5]]]}"
    },
    {
      "key": "spatial_uri",
      "value": "http://sws.geonames.org/3114965"
    },
    {
      "key": "spatial_centroid",
      "value": "{\"type\": \"Point\", \"coordinates\": [50.0, 40.0]}"
    },
    {
      "key": "temporal_end",
      "value": "2021-06-25T15:01:07.173973"
    },
    {
      "key": "temporal_start",
      "value": "2021-05-25T15:01:07.173973"
    },
    {
      "key": "theme",
      "value": "[\"http://publications.europa.eu/resource/authority/data-theme/ECON\", \"http://publications.europa.eu/resource/authority/data-theme/EDUC\"]"
    },
    {
      "key": "access_rights",
      "value": "public"
    },
    {
      "key": "conforms_to", 
      "value": "[\"Standard 1\", \"Standard 2\"]"
    },
    {
      "key": "documentation",
      "value": "[\"http://page1\", \"http://page2\"]"
    },
    {
      "key": "frequency",
      "value": "http://purl.org/cld/freq/daily"
    },
    {
      "key": "is_version_of",
      "value": "[\"http://dataset1\", \"http://dataset2\"]"
    },
    {
      "key": "has_version",
      "value": "[\"http://dataset1\", \"http://dataset2\"]"
    },
    {
      "key": "language",
      "value": "[\"http://publications.europa.eu/resource/authority/language/SPA\", \"http://publications.europa.eu/resource/authority/language/GAL\"]"
    },
    {
      "key": "alternate_identifier",
      "value": "[\"alternate_identifier_1\", \"alternate_identifier_2\"]"
    },
    {
      "key": "provenance",
      "value": "provenance info"
    },
    {
      "key": "issued",
      "value": "2022-01-02T11:31:11.500592"
    },
    {
      "key": "modified",
      "value": "2022-01-03T11:31:11.500592"
    },
    {
      "key": "version_notes",
      "value": "2.0.1"
    },
    {
      "key": "sample",
      "value": "[\"http://Distribution1\", \"http://Distribution2\"]"
    },
    {
      "key": "source",
      "value": "[\"http://Dataset1\", \"http://Dataset2\"]"
    },
    {
      "key": "dcat_type",
      "value": "dataset"
    }

  ],
  "resources": [
    {
      "uri": "http://example_distribution",
      "cache_last_updated": null,
      "package_id": "cf3dcff7-34ae-4fab-a202-2f17e3153b2f",
      "datastore_active": false,
      "availability": "http://dcat-ap.de/def/plannedAvailability/stable",
      "size": 200000000,
      "download_url": "http://localhost/downloadURL",
      "id": "9871734c-d261-4d66-96de-cfce6ddf8a31",
      "state": "active",
      "hash": "",
      "description": "Example description of Example Resource",
      "format": "JSON",
      "mimetype_inner": null,
      "url_type": null,
      "revision_id": "22fcd3f6-17a0-49e5-a715-de493e9b3719",
      "mimetype": "application/json",
      "cache_url": null,
      "name": "Example Resource",
      "license": "http://publications.europa.eu/resource/authority/licence/CC_BY_4_0",
      "license_type": "http://purl.org/adms/licencetype/PublicDomain",
      "created": "2021-07-08T11:37:12.760031",
      "url": "",
      "last_modified": null,
      "position": 0,
      "access_url": "http://localhost/accessURL",
      "resource_type": null,
      "status": "http://purl.org/adms/status/Completed",
      "conforms_to": "[\"Standard distribution 1\", \"Standard distribution 2\"]",
      "issued": "2022-01-06T15:01:07.173973",
      "modified": "2022-01-05T15:01:07.173973",
      "language": "[\"http://publications.europa.eu/resource/authority/language/ENG\", \"http://publications.europa.eu/resource/authority/language/FRA\"]",
      "rights": "Some statement about resource rights",
      "documentation": "[\"http://pageDistribution1\", \"http://pageDistribution2\"]"
    }
  ]
}
```

### Dataset (Package) and Distribution (Resource) DCAT-AP v2.0.1 rdf

```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:owl="http://www.w3.org/2002/07/owl#"
  xmlns:dcatap="http://data.europa.eu/r5r/"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:dcat="http://www.w3.org/ns/dcat#"
  xmlns:dct="http://purl.org/dc/terms/"
  xmlns:skos="http://www.w3.org/2004/02/skos/core#"
  xmlns:vcard="http://www.w3.org/2006/vcard/ns#"
  xmlns:adms="http://www.w3.org/ns/adms#"
>
  <dcat:Dataset rdf:about="http://example_dataset">
    <dct:identifier>cf3dcff7-34ae-4fab-a202-2f17e3153b2f</dct:identifier>
    <dcat:theme rdf:resource="http://publications.europa.eu/resource/authority/data-theme/EDUC"/>
    <dcat:keyword>newTag2</dcat:keyword>
    <dcat:contactPoint>
      <vcard:Kind rdf:about="http://localhost/ContactUri">
        <vcard:fn>MaintainerName ExampleSurname</vcard:fn>
        <vcard:hasEmail rdf:resource="mailto:maintainer@email.com"/>
      </vcard:Kind>
    </dcat:contactPoint>
    <dct:title>examplepackage</dct:title>
    <dcat:keyword>newTag</dcat:keyword>
    <dct:temporal>
      <dct:PeriodOfTime rdf:nodeID="N3dd43139d1904f78b2643f9f6003d4da">
        <dcat:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2021-05-25T15:01:07.173973</dcat:startDate>
        <dcat:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2021-06-25T15:01:07.173973</dcat:endDate>
      </dct:PeriodOfTime>
    </dct:temporal>
    <dcat:landingPage>
      <foaf:Document rdf:about="http://localhost/landingpageExample.es"/>
    </dcat:landingPage>
    <dct:spatial>
      <dct:Location rdf:about="http://sws.geonames.org/3114965">
        <dcat:bbox rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">POLYGON ((175.0000 17.5000, -65.5000 17.5000, -65.5000 72.0000, 175.0000 72.0000, 175.0000 17.5000))</dcat:bbox>
        <dcat:centroid rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">POINT (50.0000 40.0000)</dcat:centroid>
        <skos:inScheme rdf:resource="http://sws.geonames.org"/>
      </dct:Location>
    </dct:spatial>
    <dct:description>Description example of dataset test</dct:description>
    <dcat:theme rdf:resource="http://publications.europa.eu/resource/authority/data-theme/ECON"/>
    <dct:publisher>
      <foaf:Agent rdf:about="http://publications.europa.eu/resource/authority/corporate-body/SPC">
        <dct:type rdf:resource="http://purl.org/adms/publishertype/Academia-ScientificOrganisation"/>
        <foaf:name>exampleorg</foaf:name>
      </foaf:Agent>
    </dct:publisher>
    <owl:versionInfo>2.0</owl:versionInfo>
    <dct:accessRights>
      <dct:RightsStatement rdf:nodeID="N17e995e361144470975f58b61608f9f8">
        <rdfs:label>public</rdfs:label>
      </dct:RightsStatement>
    </dct:accessRights>
    <dct:conformsTo>
      <dct:Standard rdf:nodeID="N9d1556258e894185afc7898b8dce9e38">
        <rdfs:label>Standard 1</rdfs:label>
      </dct:Standard>
    </dct:conformsTo>
    <dct:conformsTo>
      <dct:Standard rdf:nodeID="N8473effd710341c899e147263f5201bd">
        <rdfs:label>Standard 2</rdfs:label>
      </dct:Standard>
    </dct:conformsTo>
    <foaf:page>
      <foaf:Document rdf:about="http://page1"/>
    </foaf:page>
    <foaf:page>
      <foaf:Document rdf:about="http://page2"/>
    </foaf:page>
    <dct:accrualPeriodicity rdf:resource="http://purl.org/cld/freq/daily"/>
    <dct:isVersionOf rdf:resource="http://dataset1"/>
    <dct:isVersionOf rdf:resource="http://dataset2"/>
    <dct:hasVersion rdf:resource="http://dataset1"/>
    <dct:hasVersion rdf:resource="http://dataset2"/>
    <dct:language rdf:resource="http://publications.europa.eu/resource/authority/language/SPA"/>
    <dct:language rdf:resource="http://publications.europa.eu/resource/authority/language/GAL"/>
    <adms:identifier>
      <adms:Identifier rdf:nodeID="N7e41687e3b53467c95ba9422fc3e0d5f">
        <skos:notation>alternate_identifier_1</skos:notation>
      </adms:Identifier>
    </adms:identifier>
    <adms:identifier>
      <adms:Identifier rdf:nodeID="N2b5fdfa749c648bb9cc68f03fa157669">
        <skos:notation>alternate_identifier_2</skos:notation>
      </adms:Identifier>
    </adms:identifier>
    <dct:provenance>
      <dct:ProvenanceStatement rdf:nodeID="Nfa10a2292d6c4afaa33fa1956f527e42">
        <rdfs:label>provenance info</rdfs:label>
      </dct:ProvenanceStatement>
    </dct:provenance>
    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2022-01-02T11:31:11.500592</dct:issued>
    <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2022-01-03T11:31:11.500592</dct:modified>
    <adms:versionNotes>2.0.1</adms:versionNotes>
    <adms:sample rdf:resource="http://Distribution1"/>
    <adms:sample rdf:resource="http://Distribution2"/>
    <dct:source rdf:resource="http://Dataset1"/>
    <dct:source rdf:resource="http://Dataset2"/>
    <dct:type>
      <skos:Concept rdf:nodeID="N98d6b58b2ff040a0a9656319d55f5cf9">
        <skos:prefLabel>dataset</skos:prefLabel>
      </skos:Concept>
    </dct:type>
        <dcat:distribution>
    <dcat:Distribution rdf:about="http://example_distribution">
      <dct:title>Example Resource</dct:title>
      <dcat:accessURL rdf:resource="http://localhost/accessURL"/>
      <dct:format rdf:resource="http://publications.europa.eu/resource/authority/file-type/JSON"/>
      <dct:description>Example description of Example Resource</dct:description>
      <dcat:mediaType rdf:resource="https://www.iana.org/assignments/media-types/application/json"/>
      <dcat:downloadURL rdf:resource="http://localhost/downloadURL"/>
      <dct:license rdf:resource="http://publications.europa.eu/resource/authority/licence/CC_BY_4_0"/>
      <dcat:byteSize rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">200000000.0</dcat:byteSize>
      <dcatap:availability rdf:resource="http://dcat-ap.de/def/plannedAvailability/stable"/>
      <adms:status rdf:resource="http://purl.org/adms/status/Completed"/>
      <dct:conformsTo>
        <dct:Standard rdf:nodeID="Nc765b218145049b08a5fef3e384393d4">
          <rdfs:label>Standard distribution 1</rdfs:label>
        </dct:Standard>
      </dct:conformsTo>
      <dct:conformsTo>
        <dct:Standard rdf:nodeID="Nc765b218145049b08a5fef3e384393d2">
          <rdfs:label>Standard distribution 2</rdfs:label>
        </dct:Standard>
      </dct:conformsTo>,
      <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2022-01-05T15:01:07.173973</dct:modified>
      <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2022-01-06T15:01:07.173973</dct:issued>
      <dct:language rdf:resource="http://publications.europa.eu/resource/authority/language/ENG"/>
      <dct:language rdf:resource="http://publications.europa.eu/resource/authority/language/FRA"/>
      <dct:rights>
        <dct:RightsStatement rdf:nodeID="Neaf6c525097e4b2cbdb974f615437e28">
          <rdfs:label>Some statement about resource rights</rdfs:label>
        </dct:RightsStatement>
      </dct:rights>
      <foaf:page>
        <foaf:Document rdf:about="http://pageDistribution1"/>
      </foaf:page>
      <foaf:page>
        <foaf:Document rdf:about="http://pageDistribution2"/>
      </foaf:page>
    </dcat:Distribution>
  </dcat:distribution>
  </dcat:Dataset>
  <dct:MediaType rdf:about="https://www.iana.org/assignments/media-types/application/json"/>
  <dct:MediaTypeOrExtent rdf:about="http://publications.europa.eu/resource/authority/file-type/JSON"/>
  <dct:LicenseDocument rdf:about="http://publications.europa.eu/resource/authority/licence/CC_BY_4_0">
    <dct:type rdf:resource="http://purl.org/adms/licencetype/PublicDomain"/>
  </dct:LicenseDocument>
</rdf:RDF>
```

### Catalogue (Organization) CKAN metadata

### Catalogue (Organization) DCAT-AP v2.0.1 rdf


## License

ckandext-dcatapedp is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

[http://www.fsf.org/licensing/licenses/agpl-3.0.html](http://www.fsf.org/licensing/licenses/agpl-3.0.html)