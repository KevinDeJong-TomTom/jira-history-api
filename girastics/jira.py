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
        self.jira = atlassian.Jira(url=url,
                                   username=username,
                                   password=password)

        self.fields = None
        self.statuses = None
        self.resolutions = None
        self.users = {}
        self.versions = {}

    def _get_user(self: object, username: str) -> dict:
        """
        Retrieves the user associates with the provided username.
        :param username: Username associated with an user
        :returns: User details when user is known or `None` otherwise
        """
        if not username:
            return None

        try:
            _user = self.users[username]
        except KeyError:
            logging.debug(f"Retrieving information for user: '{username}'")
            _user = self.jira.user(username=username)
            self.users[username] = _user

        return _user

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

    def _get_resolution(self: object, resolution_id: int) -> dict:
        if not self.resolutions:
            self.resolutions = utils.get_from_jira_scheme(self.jira.get_all_resolutions)

        try:
            return self.resolutions[resolution_id]
        except KeyError:
            logger.warning(f"Unknown resolution: {resolution_id}")

    def _get_status(self: object, status_id: int) -> dict:
        if not self.statuses:
            self.statuses = utils.get_from_jira_scheme(self.jira.get_all_statuses)

        try:
            return self.statuses[status_id]
        except KeyError:
            logger.warning(f"Unknown status: {status_id}")

    def _get_field(self: object, field: str) -> dict:
        if not self.fields:
            self.fields = self._get_fields()

        try:
            return self.fields[field]
        except KeyError:
            logger.warning(f"Unknown field: {field}")

    def _update_field(self: object, update: dict, issue: dict) -> dict:
        """
        Update the provided issue based on the historical update
        :param update: History item containing the update
        :param issue: Issue to be updated
        :returns: Updated issue
        """
        field = self._get_field(update['field'])

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
        else:
            logger.warning(f"Unsupported field type: {field['schema']['type']}")
            return issue

        logger.info(f"Updating field \"{field['id']}\" to:\n{_value}\n")
        issue['fields'][field['id']] = _value

        return issue

    def _update_issue_at_date(self: object, issue: dict, date: object) -> dict:
        """
        Updates the provided issue to the status of the given date/time.
        :param issue: Issue to update reflecting the status of the given date/time
        :param date: Specific date/time to unwind the issue to
        :returns: Updated issue
        """

        _creation_date = utils.field_to_datetime(issue['fields']['created'])

        if date < _creation_date:
            logger.warning(f"Requesting date ({date})"
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

    def get_issue(self: object, key: str) -> dict:
        """
        Retrieves an issue from Jira and updates it so the status of 01/08/2018
        :param key: Issue key to retrieve
        :returns: Issue reflecting the status of 01/08/2018
        """
        _issues = self.jira.jql(jql=f'key={key}', expand='schema,changelog')['issues']

        for issue in _issues:
            issue = self._update_issue_at_date(issue,  datetime.strptime('2018/08/01', '%Y/%m/%d'))
