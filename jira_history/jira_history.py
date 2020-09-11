#!/usr/bin/env python3

# Copyright (c) 2020 - 2020 TomTom N.V. All rights reserved.
#
# This software is the proprietary copyright of TomTom N.V. and its subsidiaries and may be
# used for internal evaluation purposes or commercial use strictly subject to separate
# licensee agreement between you and TomTom. If you are the licensee, you are only permitted
# to use this Software in accordance with the terms of your license agreement. If you are
# not the licensee, then you are not authorized to use this software in any manner and should
# immediately return it to TomTom N.V.

from datetime import datetime
import logging

import atlassian

from . import utils

logger = logging.getLogger(__name__)


class Jira():

    def __init__(self: object, url: str, username: str, password: str):
        self._jira = atlassian.Jira(url=url,
                                    username=username,
                                    password=password)

        self._fields = None
        self._statuses = None
        self._resolutions = None
        self._users = {}
        self._versions = {}

    def _get_user(self: object, username: str) -> dict:
        """
        Retrieves the user associates with the provided username.
        :param username: Username associated with an user
        :returns: User details when user is known or `None` otherwise
        """
        if not username:
            return None

        try:
            return self._users[username]
        except KeyError:
            logging.debug(f"Retrieving information for user: '{username}'")
            self._users[username] = self._jira.user(username=username)

        return self._users[username]

    def _get_fields(self: object) -> dict:
        """
        Retrieves all Jira fields and translates them into an dict.
        NOTE: All aliases will be expanded.
        :returns: Dictionary containing all items by field ID
        """
        _fields = self._jira.get_all_fields()

        _fields_dict = {}
        for field in _fields:
            for clause in field['clauseNames']:
                _fields_dict[clause] = field

        # Special cases
        try:
            _fields_dict['Fix Version'] = _fields_dict['fixVersion']
        except KeyError:
            logger.warning('The field "fixVersion" is not a valid alias')

        return _fields_dict

    def _get_version(self: object, project: str, version_id: str) -> dict:
        """
        Retrieves the version associated with the given version ID
        :param project: Project key associated with the version
        :param version_d: Version ID associated with a version
        :returns: Version when version ID is known or `None` otherwise
        """
        if not project or not version_id:
            return None

        if not self._versions:
            _versions = self._jira.get_project_versions(project)

            self._versions[project] = {}
            for version in _versions:
                self._versions[project][version['id']] = version

        try:
            return self._versions[project][version_id]
        except KeyError:
            logger.warning(f"Unknown version: {version_id}")

    def _get_resolution(self: object, resolution_id: str) -> dict:
        if not resolution_id:
            return None

        if not self._resolutions:
            self._resolutions = utils.get_from_jira_scheme(self._jira.get_all_resolutions)

        try:
            return self._resolutions[resolution_id]
        except KeyError:
            logger.warning(f"Unknown resolution: {resolution_id}")

    def _get_status(self: object, status_id: str) -> dict:
        if not status_id:
            return None

        if not self._statuses:
            self._statuses = utils.get_from_jira_scheme(self._jira.get_all_statuses)

        try:
            return self._statuses[status_id]
        except KeyError:
            logger.warning(f"Unknown status: {status_id}")

    def _get_field(self: object, field: str) -> dict:
        if not field:
            return None

        if not self._fields:
            self._fields = self._get_fields()

        try:
            return self._fields[field]
        except KeyError:
            logger.warning(f"Unknown field: {field}")

    def _update_array(self: object, update: dict, issue: dict):
        if update['field'] == 'Fix Version':
            _project = issue['fields']['project']['key']
            _versions = issue['fields']['fixVersions']

            _from = self._get_version(_project, update['from'])
            _to = self._get_version(_project, update['to'])

            if _from is None:
                return [version for version in _versions if version['id'] != _to['id']]
            else:
                _versions.append(_from)
                return _versions

        logger.error(f"Unsupport array type: {update['field']}")
        return None

    def _update_field(self: object, update: dict, issue: dict) -> dict:
        """
        Update the provided issue based on the historical update
        :param update: History item containing the update
        :param issue: Issue to be updated
        :returns: Updated issue
        """
        field = self._get_field(update['field'])

        # Special cases
        if not field:
            logger.error(f"Could not update issue for history: {update}")
            return issue

        _value = None

        _field_type = field['schema']['type']
        if _field_type == 'string':
            _value = update['fromString']
        elif _field_type == 'status':
            _value = self._get_status(update['from'])
        elif _field_type == 'resolution':
            _value = self._get_resolution(update['from'])
        elif _field_type == 'user':
            _value = self._get_user(update['from'])
        elif _field_type == 'array':
            _value = self._update_array(update, issue)
        else:
            logger.warning(f"Unsupported field type: {field['schema']['type']}")
            return issue

        logger.info(f"Updating field \"{field['id']}\" to:\n{_value}\n")
        issue['fields'][field['id']] = _value

        return issue

    def _update_issue_at_date(self: object, issue: dict, date: object = datetime.now()) -> dict:
        """
        Updates the provided issue to the status of the given date/time.
        :param issue: Issue to update reflecting the status of the given date/time
        :param date: Specific date/time to unwind the issue to (optional)
        :returns: Updated issue
        """
        if not issue or not date:
            return None

        _creation_date = utils.field_to_datetime(issue['fields']['created'])

        if date < _creation_date:
            logger.warning(f"Requesting date ({date}) "
                           f"before issue creation ({issue['fields']['created']}")
            return None

        if not issue['changelog']['histories']:
            logger.info('Issue has not been updated, returning current status')
            return issue

        # We iterate in reverse order to allow simple patches with having
        # to reconstruct the status upon ticket creation
        for history in reversed(issue['changelog']['histories']):
            _history_date = utils.field_to_datetime(history['created'])

            if _history_date < date:
                logger.debug('All updates have been applied!')
                break

            logger.info(f'Next history at: {_history_date}')

            for change in history['items']:
                issue = self._update_field(change, issue)

        return issue

    def jql(self: object, jql: str, date: object = datetime.now()) -> list:
        """
        Retrieves issues from Jira using JQL and updates them to the status of the given date/time
        :param jql: JQL to retrieve issue with
        :param date: Specific date/time to unwind the issue to (optional)
        :returns: Issues reflecting the status of the specified date/time
        """
        _issues = self._jira.jql(jql=jql, expand='changelog')['issues']

        result = []
        for issue in _issues:
            result.append(self._update_issue_at_date(issue, date))

        return result

    def get_issue(self: object, key: str, date: object = datetime.now()) -> dict:
        """
        Retrieves an issue from Jira and updates it to the status of the given date/time
        :param key: Issue key to retrieve
        :param date: Specific date/time to unwind the issue to (optional)
        :returns: Issues reflecting the status of the specified date/time
        """
        _issues = self.jql(f'key={key}', date)
        if len(_issues) > 0:
            return _issues[0]

        return _issues
