============
Jira History
============
|version| |license| |coverage| |qualitygate| 

The Jira History library allows you to retrieve issues from JIRA in (almost) the same
state as they were on the requested date/time.

In addition, a simple CLI is added to retrieve the status of a singular issue.

.. |coverage| image:: https://sonarcloud.io/api/project_badges/measure?project=KevinDeJong-TomTom_girastics&metric=coverage
.. |qualitygate| image:: https://sonarcloud.io/api/project_badges/measure?project=KevinDeJong-TomTom_girastics&metric=alert_status
.. |version| image:: https://badge.fury.io/py/jira-history-api.svg
   :target: https://badge.fury.io/py/jira-history-api
.. |license| image:: https://img.shields.io/pypi/l/jira-history-api.svg
   :target: https://pypi.python.org/pypi/jira-history-api


Installation
------------
.. code-block:: console

   $ pip install jira-history-api

Example
-------

.. code-block:: python

    from jira_history import Jira
    from datetime import datetime

    jira = Jira(url='https://jira-instance.com',
                username='bob',
                password='secret')

    jira.get_issue(key='ISSUE-100',
                   datetime.strptime('12/11/2018 09:15:32', '%d/%m/%Y %H:%M:%S'))

Usage
-----

.. code-block:: console

    Usage: jira-history [OPTIONS]

    Options:
    -u, --username TEXT    Username that is able to query Jira  [required]
    -p, --password TEXT    Password associated with the Username that is able to
                            query Jira  [required]

    -s, --server TEXT      Jira server URL  [required]
    -k, --key TEXT         Issue key to analyse  [required]
    -d, --date [%Y-%m-%d]  Status of Jira issue key should reflect this date.
    --verbose              Increase verbosity for more logging
    --help                 Show this message and exit.

Credits
-------

- The `atlassian-python-api`_ project, providing the Jira REST API calls used by this project.

.. _atlassian-python-api: https://pypi.org/project/atlassian-python-api/