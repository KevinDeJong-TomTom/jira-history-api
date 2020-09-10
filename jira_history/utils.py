#!/usr/bin/env python3

# Copyright (c) 2020 - 2020 TomTom N.V. All rights reserved.
#
# This software is the proprietary copyright of TomTom N.V. and its subsidiaries and may be
# used for internal evaluation purposes or commercial use strictly subject to separate
# licensee agreement between you and TomTom. If you are the licensee, you are only permitted
# to use this Software in accordance with the terms of your license agreement. If you are
# not the licensee, then you are not authorized to use this software in any manner and should
# immediately return it to TomTom N.V.

import datetime


def field_to_datetime(field):
    """Converts a JIRA field to a datetime object"""
    return datetime.datetime.strptime(field[:19], '%Y-%m-%dT%H:%M:%S')


def datetime_to_field(date):
    """Convert a datetime object to JIRA data format"""
    return date.strftime('%Y-%m-%dT%H:%M:%S')


def get_from_jira_scheme(function: object) -> dict:
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
