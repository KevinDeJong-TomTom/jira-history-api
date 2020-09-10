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
        self.uut._jira.get_all_fields.assert_called_once()

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
