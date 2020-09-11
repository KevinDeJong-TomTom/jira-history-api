============
Jira History
============

The Jira History library allows you to retrieve issues from JIRA in (almost) the same
state as they were on the requested date/time.

In addition, a simple CLI is added to retrieve the status of a singular issue.


Installation
------------
.. code-block:: console

   $ pip install jira-history

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