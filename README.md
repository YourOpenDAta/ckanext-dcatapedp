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

        pip install ckanext-dcatapedp

5. Active the edp_dcat_ap profile in the `production.ini` file:

        ckanext.dcat.rdf.profiles = euro_dcat_ap edp_dcat_ap

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

## License

ckandext-dcatapedp is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

[http://www.fsf.org/licensing/licenses/agpl-3.0.html](http://www.fsf.org/licensing/licenses/agpl-3.0.html)