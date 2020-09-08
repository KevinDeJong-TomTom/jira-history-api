#!/usr/bin/env python3

# Copyright (c) 2020 - 2020 TomTom N.V. All rights reserved.
#
# This software is the proprietary copyright of TomTom N.V. and its subsidiaries and may be
# used for internal evaluation purposes or commercial use strictly subject to separate
# licensee agreement between you and TomTom. If you are the licensee, you are only permitted
# to use this Software in accordance with the terms of your license agreement. If you are
# not the licensee, then you are not authorized to use this software in any manner and should
# immediately return it to TomTom N.V.

import atlassian
import logging

logger = logging.getLogger(__name__)


class Jira(atlassian.Jira):

    def __init__(self: object, url: str, username: str, password: str):
        self.jira = atlassian.Jira(url=url,
                                   username=username,
                                   password=password)

        self.fields = self._get_fields()
        self.statuses = self._get_from_jira_scheme(self.jira.get_all_statuses)
        self.resolutions = self._get_from_jira_scheme(self.jira.get_all_resolutions)

    def _get_from_jira_scheme(self: object, function: object) -> dict:
        """
        Retrieves Jira schemes and translates them into an dict
        :param function: atlassian.Jira function returning a Jira scheme (dict)
        :returns: Dictionary containing all items by ID
        """
        _data = function()

        _result_dict = {}
        for entry in _data:
            _result_dict[entry['id']] = entry

        return _result_dict

    def _get_fields(self: object) -> dict:
        """
        Retrieves all Jira fields and translates them into an dict.
        NOTE: All aliases will be expanded.
        :returns: Dictionary containing all items by field ID
        """
        _fields = self.jira.get_all_fields()

        _fields_dict = {}
        for field in _fields:
            for clause in field['clauseNames']:
                _fields_dict[clause] = field

        return _fields_dict

    def _get_resoluition(self: object, resolution_id: int) -> dict:
        try:
            return self.resolutions[resolution_id]
        except KeyError:
            logger.warning(f"Unknown status: {resolution_id}")

    def _get_status(self: object, status_id: int) -> dict:
        try:
            return self.statuses[status_id]
        except KeyError:
            logger.warning(f"Unknown status: {status_id}")

    def _get_field(self: object, field: str) -> dict:
        try:
            return self.fields[field]
        except KeyError:
            logger.warning(f"Unknown field: {field}")

    def _update_field(self: object, update, issue):
        field = self._get_field(update['field'])

        if not field:
            logger.error(f"Could not update issue for history: {update}")
            return

        _field_type = field['schema']['type']
        _value = None
        if _field_type == 'string':
            _value = update['toString']
        elif _field_type == 'status':
            _value = self._get_status(update['to'])
        elif _field_type == 'resolution':
            _value = self._get_resoluition(update['to'])
        elif _field_type == 'user':
            _value = self.jira.user(update['to'])
        else:
            logger.warning(f"Unsupported field type: {field['schema']['type']}")
            return

        issue['fields'][field['id']] = _value

    def get_issue(self: object, key: str) -> dict:
        _issues = self.jira.jql(jql=f'key={key}', expand='schema,changelog')['issues']

        for issue in _issues:
            for history in issue['changelog']['histories']:
                for change in history['items']:
                    self._update_field(change, issue)
