#!/usr/bin/env python3

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
# limitations under the License.V.

import datetime
import logging
from typing import Callable

logger = logging.getLogger(__name__)


def field_to_datetime(field):
    """Converts a JIRA field to a datetime object"""
    return datetime.datetime.strptime(field[:19], '%Y-%m-%dT%H:%M:%S')


def datetime_to_field(date):
    """Convert a datetime object to JIRA data format"""
    return date.strftime('%Y-%m-%dT%H:%M:%S')


def get_from_jira_scheme(function: Callable) -> dict:
    """
    Retrieves Jira schemes and translates them into an dict
    :param function: atlassian.Jira function returning a Jira scheme (dict)
    :returns: Dictionary containing all items by ID
    """
    _data = function()
    _result_dict = {}

    if _data:
        for entry in _data:
            _result_dict[entry['id']] = entry
    else:
        logger.error(f"Could not retrieve scheme for {function}")

    return _result_dict


def set_field_alias(data: dict, field: str, alias: str) -> dict:
    """
    Creates an alias for a field and adds it to the dict
    :param data: dict containing the current fields
    :param field: name of the field to add to the dict
    :param alias: name of the field to use as its alias
    :returns: Dictionary containing all fields and the new alias
    """
    try:
        data[field] = data[alias]
    except KeyError:
        logger.warning(f'The field "{alias}" is not a valid alias')

    return data
