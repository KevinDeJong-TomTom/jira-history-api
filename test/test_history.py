# Copyright (c) 2020 - 2021 TomTom N.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atlassian
import contextlib
from datetime import datetime
import unittest
from unittest import mock

from jira_history_api import jira_history
from jira_history_api import utils


class TestJiraUser(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira_history.Jira(username='ben', password='secret', url='404')

    def test_get_no_user(self):
        assert not self.uut._get_user(username=None)
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
            self.uut = jira_history.Jira(username='bob', password='secret', url='404')

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
        assert not self.uut._get_field(None)
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
            self.uut = jira_history.Jira(username='bob', password='secret', url='404')

    def test_get_no_version_no_project(self):
        assert not self.uut._get_version(project=None, version_id=None)
        self.uut._jira.get_project_versions.assert_not_called()

    def test_get_no_version(self):
        assert not self.uut._get_version(project='TEST', version_id=None)
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


class TestJiraComponent(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira_history.Jira(username='bob', password='secret', url='404')

    def test_get_no_component_no_project(self):
        assert not self.uut._get_component(project=None, component_id=None)
        self.uut._jira.component.assert_not_called()

    def test_get_no_component(self):
        assert not self.uut._get_component(project='TEST', component_id=None)
        self.uut._jira.component.assert_not_called()

    def test_get_invalid_component(self):
        self.uut._jira.component.return_value = {
            'errorMessages': ['The component with id 666 does not exist.'],
            'errors': {}
        }

        assert not self.uut._get_component(project='TEST', component_id='666')
        self.uut._jira.component.assert_called_once()

    def test_get_valid_component(self):
        _component = {
            'self': 'https://jira-instance/rest/api/2/component/52336',
            'id': '52336',
            'name': 'COMPONENT 1',
            'assigneeType': 'PROJECT_DEFAULT',
            'realAssigneeType': 'PROJECT_DEFAULT',
            'isAssigneeTypeValid': False,
            'project': 'TEST',
            'projectId': 22694,
            'archived': False
        }
        self.uut._jira.component.return_value = _component

        assert self.uut._get_component(project='TEST', component_id=52336) == {
            'self': _component['self'],
            'id': _component['id'],
            'name': _component['name']
        }
        self.uut._jira.component.assert_called_once()

    def test_get_valid_component_invalid_project(self):
        _component = {
            'self': 'https://jira-instance/rest/api/2/component/52336',
            'id': '52336',
            'name': 'COMPONENT 1',
            'assigneeType': 'PROJECT_DEFAULT',
            'realAssigneeType': 'PROJECT_DEFAULT',
            'isAssigneeTypeValid': False,
            'project': 'TEST',
            'projectId': 22694,
            'archived': False
        }
        self.uut._jira.component.return_value = _component

        assert not self.uut._get_component(project='FAIL', component_id=52336)
        self.uut._jira.component.assert_called_once()

    def test_get_valid_component_from_cache(self):
        self.uut._get_component(project='TEST', component_id='1')
        self.uut._get_component(project='TEST', component_id='1')

        self.uut._jira.component.assert_called_once()


class TestJiraResolution(unittest.TestCase):
    def setUp(self):
        with fake_jira_context():
            self.uut = jira_history.Jira(username='ben', password='secret', url='404')

    def test_get_no_resolution(self):
        assert not self.uut._get_resolution(resolution_id=None)
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
            self.uut = jira_history.Jira(username='ben', password='secret', url='404')

    def test_get_no_status(self):
        assert not self.uut._get_status(status_id=None)
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
            self.uut = jira_history.Jira(username='ben', password='secret', url='404')
            self.test_issue = {
                'expand': 'operations,versionedRepresentations,editmeta,changelog,renderedFields',
                'id': '2109604',
                'self': 'https://jira-instance/rest/api/2/issue/2109604',
                'key': 'TEST-100',
                'fields': {
                    'created': '2018-01-01T12:00:00.000+0000',
                    'fixVersions': [],
                    'resolution': {
                        'name': "Won't Fix",
                        'id': '2'
                    },
                    'description': '*Fixed* my typo (_with_ text formatting)',
                    'summary': 'Interesting issue to solve',
                    'status': {
                        'name': 'Done',
                        'id': '2'
                    },
                    'assignee': {'displayName': 'bob'},
                    'project': {'key': 'TEST'}
                },
                'changelog': {
                    'histories': []
                }
            }

    def test_update_issue_without_issue(self):
        assert not self.uut._update_issue_at_date(issue=None, date=datetime.now())

    def test_update_issue_without_date(self):
        assert not self.uut._update_issue_at_date(issue=self.test_issue, date=None)

    def test_update_issue_without_changelog(self):
        assert self.uut._update_issue_at_date(issue=self.test_issue) == self.test_issue

    def test_update_issue_before_creation_date(self):
        assert not self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2000-01-01T09:00:00.000+0000'))

    def test_update_issue_future_date(self):
        assert self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('3000-01-01T09:00:00.000+0000')) == self.test_issue

    def test_update_issue_invalid_field(self):
        self.test_issue['changelog']['histories'] = [
            {
                'id': '1',
                'created': '2018-06-01T09:00:00.000+0000',
                'items': [{'field': 'invalid', 'fieldtype': 'string', 'from': '', 'fromString': 'Does not exist', 'to': '', 'toString': 'Still does not exist'}]
            }
        ]

        assert self.uut._update_issue_at_date(issue=self.test_issue) == self.test_issue

    def test_update_issue_multiple_dates(self):
        _summary_field = {'id': 'summary', 'name': 'Summary', 'clauseNames': ['summary'], 'schema': {'type': 'string', 'system': 'description'}}
        _description_field = {'id': 'description', 'name': 'Description', 'clauseNames': ['description'], 'schema': {'type': 'string', 'system': 'description'}}
        self.uut._jira.get_all_fields.return_value = [_summary_field, _description_field]

        self.test_issue['changelog']['histories'] = [
            {
                'id': '1',
                'created': '2018-06-01T09:00:00.000+0000',
                'items': [{'field': 'description', 'fieldtype': 'string', 'from': '', 'fromString': 'I made a typo', 'to': '', 'toString': 'Fixed my typo'}]
            },
            {
                'id': '2',
                'created': '2018-12-01T12:00:00.000+0000',
                'items': [{
                    'field': 'description',
                    'fieldtype': 'string',
                    'from': '',
                    'fromString': 'Fixed my typo',
                    'to': '',
                    'toString': '*Fixed* my typo (_with_ text formatting)'
                }, {
                    'field': 'summary',
                    'fieldtype': 'string',
                    'from': '',
                    'fromString': 'Uninteresting issue to solve',
                    'to': '',
                    'toString': 'Interesting issue to solve'
                }]
            },
        ]
        assert self.uut._update_issue_at_date(issue=self.test_issue) == self.test_issue

        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-11-30T09:00:00.000+0000'))
        assert _issue['fields']['description'] == 'Fixed my typo'
        assert _issue['fields']['summary'] == 'Uninteresting issue to solve'

        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T09:01:00.000+0000'))
        assert _issue['fields']['description'] == 'Fixed my typo'

        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T08:59:00.000+0000'))
        assert _issue['fields']['description'] == 'I made a typo'

    def test_update_issue_status_field(self):
        self.uut._jira.get_all_fields.return_value = [{
            'id': 'status',
            'name': 'Status',
            'clauseNames': ['status'],
            'schema': {'type': 'status', 'system': 'status'}
        }]
        self.uut._jira.get_all_statuses.return_value = [{'name': 'Open', 'id': '1'},
                                                        {'name': 'Done', 'id': '2'}]

        self.test_issue['changelog']['histories'] = [
            {
                'id': '1',
                'created': '2018-06-01T09:00:00.000+0000',
                'items': [{'field': 'status', 'fieldtype': 'jira', 'from': '1', 'fromString': 'Open', 'to': '2', 'toString': 'Done'}]
            }
        ]

        assert self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T09:01:00.000+0000')) == self.test_issue
        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T08:59:00.000+0000'))
        assert _issue['fields']['status']['name'] == 'Open'

    def test_update_issue_resolution_field(self):
        self.uut._jira.get_all_fields.return_value = [{
            'id': 'resolution',
            'name': 'Resolution',
            'clauseNames': ['resolution'],
            'schema': {'type': 'resolution', 'system': 'resolution'}
        }]
        self.uut._jira.get_all_resolutions.return_value = [{'id': '1', 'name': 'Fixed'},
                                                           {'id': '2', 'name': "Won't Fix"}]

        self.test_issue['changelog']['histories'] = [
            {
                'id': '1',
                'created': '2018-06-01T09:00:00.000+0000',
                'items': [{'field': 'resolution', 'fieldtype': 'jira', 'from': None, 'fromString': None, 'to': '1', 'toString': 'Fixed'}]
            },
            {
                'id': '2',
                'created': '2018-12-01T09:00:00.000+0000',
                'items': [{'field': 'resolution', 'fieldtype': 'jira', 'from': '1', 'fromString': 'Fixed', 'to': '2', 'toString': "Won't Fix"}]
            }
        ]

        assert self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T09:01:00.000+0000')) == self.test_issue

        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T08:59:00.000+0000'))
        assert not _issue['fields']['resolution']

        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T09:01:00.000+0000'))
        assert _issue['fields']['resolution']['name'] == 'Fixed'

    def test_update_issue_user_field(self):
        self.uut._jira.get_all_fields.return_value = [{
            'id': 'assignee',
            'name': 'Assignee',
            'clauseNames': ['assignee'],
            'schema': {'type': 'user', 'system': 'assignee'}
        }]
        self.uut._jira.user.return_value = {'displayName': 'bob'}

        self.test_issue['changelog']['histories'] = [
            {
                'id': '1',
                'created': '2018-06-01T09:00:00.000+0000',
                'items': [{'field': 'assignee', 'fieldtype': 'jira', 'from': 'bob', 'fromString': 'bob', 'to': 'bill', 'toString': 'bill'}]
            }
        ]

        assert self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T09:01:00.000+0000')) == self.test_issue
        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T08:59:00.000+0000'))
        assert _issue['fields']['assignee']['displayName'] == 'bob'

    def test_update_issue_fix_version(self):
        self.uut._jira.get_all_fields.return_value = [{
            'id': 'fixVersions',
            'name': 'Fix Version/s',
            'clauseNames': ['fixVersion'],
            'schema': {'type': 'array', 'items': 'version', 'system': 'fixVersions'}
        }]

        self.test_issue['changelog']['histories'] = [
            {
                'id': '1',
                'created': '2018-06-01T09:00:00.000+0000',
                'items': [{'field': 'Fix Version', 'fieldtype': 'jira', 'from': '1', 'fromString': '1.0.0', 'to': None, 'toString': None},
                          {'field': 'Fix Version', 'fieldtype': 'jira', 'from': None, 'fromString': None, 'to': '2', 'toString': '1.0.1'}]
            }
        ]

        self.uut._jira.get_project_versions.return_value = [{'id': '1', 'name': '1.0.0'},
                                                            {'id': '2', 'name': '1.0.1'}]

        assert self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T09:01:00.000+0000')) == self.test_issue

        _issue = self.uut._update_issue_at_date(issue=self.test_issue, date=utils.field_to_datetime('2018-06-01T08:59:00.000+0000'))
        assert len(_issue['fields']['fixVersions']) == 1
        assert _issue['fields']['fixVersions'][0]['name'] == '1.0.0'


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
