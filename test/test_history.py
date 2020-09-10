# Copyright (c) 2020 - 2020 TomTom N.V. All rights reserved.
#
# This software is the proprietary copyright of TomTom N.V. and its subsidiaries and may be
# used for internal evaluation purposes or commercial use strictly subject to separate
# licensee agreement between you and TomTom. If you are the licensee, you are only permitted
# to use this Software in accordance with the terms of your license agreement. If you are
# not the licensee, then you are not authorized to use this software in any manner and should
# immediately return it to TomTom N.V.

import atlassian
import contextlib
import datetime
import unittest
from unittest import mock

from jira_history import jira


class TestJiraUser(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira.Jira(username='ben', password='secret', url='404')

    def test_get_no_user(self):
        assert self.uut._get_user(username=None) is None
        self.uut._jira.user.assert_not_called()

    def test_get_invalid_user(self):
        self.uut._jira.user.return_value = None

        assert self.uut._get_user(username='bert') is None
        self.uut._jira.user.assert_called_once()

    def test_get_valid_user(self):
        self.uut._jira.user.return_value = {'displayName': 'bob'}

        assert self.uut._get_user(username='bob')['displayName'] == 'bob'
        self.uut._jira.user.assert_called_once()

    def test_get_valid_user_from_cache(self):
        self.uut._get_user(username='bill')
        self.uut._get_user(username='bill')

        self.uut._jira.user.assert_called_once()


class TestJiraField(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira.Jira(username='bob', password='secret', url='404')

    def test_get_empty_fields(self):
        self.uut._jira.get_all_fields.return_value = []
        assert self.uut._get_fields() == {}

    def test_get_fields(self):
        _field_001 = {'id': 'customfield_00001', 'name': 'Test Field', 'clauseNames': ['customfield_00001']}
        _field_002 = {'id': 'summary', 'name': 'Summary', 'clauseNames': ['summary']}
        self.uut._jira.get_all_fields.return_value = [_field_001, _field_002]

        assert self.uut._get_fields() == {'customfield_00001': _field_001, 'summary': _field_002}
        self.uut._jira.get_all_fields.assert_called_once()

    def test_get_fields_multiple_clausenames(self):
        _field = {'id': 'customfield_00001', 'name': 'Test Field', 'clauseNames': ['customfield_00001', 'cf[00001]']}
        self.uut._jira.get_all_fields.return_value = [_field]

        assert self.uut._get_fields() == {'customfield_00001': _field, 'cf[00001]': _field}
        self.uut._jira.get_all_fields.assert_called_once()

    def test_get_fields_fixVersion(self):
        _field = {'id': 'fixVersion', 'name': 'Fix Version/s', 'clauseNames': ['fixVersion']}
        self.uut._jira.get_all_fields.return_value = [_field]

        assert self.uut._get_fields() == {'fixVersion': _field, 'Fix Version': _field}
        self.uut._jira.get_all_fields.assert_called_once()

    def test_get_no_field(self):
        _field = {'id': 'customfield_00001', 'name': 'Test Field', 'clauseNames': ['customfield_00001']}
        self.uut._jira.get_all_fields.return_value = [_field]

        assert self.uut._get_field('invalid') is None
        self.uut._jira.get_all_fields.assert_called_once()

    def test_get_invalid_field(self):
        assert self.uut._get_field(None) is None
        self.uut._jira.get_all_fields.assert_not_called()

    def test_get_valid_field(self):
        _field_001 = {'id': 'customfield_00001', 'name': 'Test Field', 'clauseNames': ['customfield_00001']}
        _field_002 = {'id': 'summary', 'name': 'Summary', 'clauseNames': ['summary']}
        self.uut._jira.get_all_fields.return_value = [_field_001, _field_002]

        assert self.uut._get_field('customfield_00001') == _field_001
        self.uut._jira.get_all_fields.assert_called_once()

    def test_get_valid_field_from_cache(self):
        _field_001 = {'id': 'customfield_00001', 'name': 'Test Field', 'clauseNames': ['customfield_00001']}
        _field_002 = {'id': 'summary', 'name': 'Summary', 'clauseNames': ['summary']}
        self.uut._jira.get_all_fields.return_value = [_field_001, _field_002]

        assert self.uut._get_field('customfield_00001') == _field_001
        assert self.uut._get_field('customfield_00001') == _field_001

        self.uut._jira.get_all_fields.assert_called_once()


class TestJiraVersion(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira.Jira(username='bob', password='secret', url='404')

    def test_get_no_version_no_project(self):
        assert self.uut._get_version(project=None, version_id=None) is None
        self.uut._jira.get_project_versions.assert_not_called()

    def test_get_no_version(self):
        assert self.uut._get_version(project='TEST', version_id=None) is None
        self.uut._jira.get_project_versions.assert_not_called()

    def test_get_invalid_version(self):
        self.uut._jira.get_project_versions.return_value = [{
            'self': 'https://jira-instance/rest/api/2/version/61404',
            'id': '61404',
            'name': 'RELEASE 1',
            'archived': False,
            'released': True,
            'startDate': '2017-11-20',
            'releaseDate': '2017-12-01',
            'userStartDate': '20/Nov/17 12:00 AM',
            'userReleaseDate': '01/Dec/17 12:00 AM',
            'projectId': 1
        }]

        assert self.uut._get_version(project='TEST', version_id=666) is None
        self.uut._jira.get_project_versions.assert_called_once()

    def test_get_valid_version(self):
        _version = {
            'self': 'https://jira-instance/rest/api/2/version/61404',
            'id': '61404',
            'name': 'RELEASE 1',
            'archived': False,
            'released': True,
            'startDate': '2017-11-20',
            'releaseDate': '2017-12-01',
            'userStartDate': '20/Nov/17 12:00 AM',
            'userReleaseDate': '01/Dec/17 12:00 AM',
            'projectId': 1
        }

        self.uut._jira.get_project_versions.return_value = [_version]

        assert self.uut._get_version(project='TEST', version_id='61404') == _version
        self.uut._jira.get_project_versions.assert_called_once()

    def test_get_valid_version_from_cache(self):
        self.uut._get_version(project='TEST', version_id='1')
        self.uut._get_version(project='TEST', version_id='1')

        self.uut._jira.get_project_versions.assert_called_once()


class TestJiraResolution(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira.Jira(username='ben', password='secret', url='404')

    def test_get_no_resolution(self):
        assert self.uut._get_resolution(resolution_id=None) is None
        self.uut._jira.get_all_resolutions.assert_not_called()

    def test_get_invalid_resolution(self):
        self.uut._jira.get_all_resolutions.return_value = None

        assert self.uut._get_resolution(resolution_id='1') is None
        self.uut._jira.get_all_resolutions.assert_called_once()

    def test_get_valid_resolution(self):
        self.uut._jira.get_all_resolutions.return_value = [{
            'self': 'https://jira-instance/rest/api/2/resolution/1',
            'id': '1',
            'description': 'A fix for this issue is checked into the tree and tested.',
            'name': 'Fixed'
        }]

        assert self.uut._get_resolution(resolution_id='1')['name'] == 'Fixed'
        self.uut._jira.get_all_resolutions.assert_called_once()

    def test_get_valid_resolution_from_cache(self):
        self.uut._jira.get_all_resolutions.return_value = [{'id': '1'}]
        self.uut._get_resolution(resolution_id='1')
        self.uut._get_resolution(resolution_id='1')

        self.uut._jira.get_all_resolutions.assert_called_once()


class TestJiraStatus(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira.Jira(username='ben', password='secret', url='404')

    def test_get_no_status(self):
        assert self.uut._get_status(status_id=None) is None
        self.uut._jira.get_all_statuses.assert_not_called()

    def test_get_invalid_status(self):
        self.uut._jira.get_all_statuses.return_value = None

        assert self.uut._get_status(status_id='1') is None
        self.uut._jira.get_all_statuses.assert_called_once()

    def test_get_valid_status(self):
        self.uut._jira.get_all_statuses.return_value = [{
            'self': 'https://jira-instance/rest/api/2/status/1',
            'description': 'The issue is open and ready for the assignee to start work on it.',
            'iconUrl': 'https://jira-instance/images/icons/statuses/open.png',
            'name': 'Open',
            'id': '1',
            'statusCategory': {
                'self': 'https://jira-instance/rest/api/2/statuscategory/2',
                'id': 2,
                'key': 'new',
                'colorName': 'blue-gray',
                'name': 'To Do'
            }
        }]

        assert self.uut._get_status(status_id='1')['name'] == 'Open'
        self.uut._jira.get_all_statuses.assert_called_once()

    def test_get_valid_status_from_cache(self):
        self.uut._jira.get_all_statuses.return_value = [{'id': '1'}]
        self.uut._get_status(status_id='1')
        self.uut._get_status(status_id='1')

        self.uut._jira.get_all_statuses.assert_called_once()


class TestJiraUpdate(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira.Jira(username='ben', password='secret', url='404')
            self.issue001 = {
                'expand': 'operations,versionedRepresentations,editmeta,changelog,renderedFields',
                'id': '2109604',
                'self': 'https://jira-instance/rest/api/2/issue/2109604',
                'key': 'TEST-100',
                'fields': {
                    'created': '2018-01-01T12:00:00.000+0000',
                    'fixVersions': [],
                    'resolution': None,
                    'summary': 'Interesting issue to solve',
                    'status': {
                        'self': 'https://jira-instance/rest/api/2/status/1',
                        'description': 'The issue is open and ready for the assignee to start work on it.',
                        'iconUrl': 'https://jira-instance/images/icons/statuses/open.png',
                        'name': 'Open',
                        'id': '1',
                        'statusCategory': {
                            'self': 'https://jira-instance/rest/api/2/statuscategory/2',
                            'id': 2,
                            'key': 'new',
                            'colorName': 'blue-gray',
                            'name': 'To Do'
                        }
                    },
                    'assignee': None
                },
                'changelog': {
                    'histories': []
                }
            }

    def test_update_issue_without_issue(self):
        assert self.uut._update_issue_at_date(issue=None, date=datetime.datetime.now()) is None

    def test_update_issue_without_date(self):
        assert self.uut._update_issue_at_date(issue=self.issue001, date=None) is None

    def test_update_issue_without_changelog(self):
        assert self.uut._update_issue_at_date(issue=self.issue001) == self.issue001


@contextlib.contextmanager
def fake_jira_context():

    def new_fake_client(*_args, **_kwargs):
        # Creates a mock object by using class interface as spec.
        # It creates mocked versions of every method and attribute in interface class.
        fake_client_class = mock.create_autospec(atlassian.Jira, spec_set=True)
        fake_client = fake_client_class()
        return fake_client

    with mock.patch.object(atlassian, "Jira", new=new_fake_client):
        yield
