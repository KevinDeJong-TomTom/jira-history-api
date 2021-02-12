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
# limitations under the License.
import logging
from datetime import datetime
import click

from jira_history_api import jira_history

logger = logging.getLogger(__name__)


@click.command()
@click.option('-u', '--username',
              required=True,
              prompt=True,
              help='Username that is able to query Jira')
@click.option('-p', '--password',
              required=True,
              prompt=True,
              hide_input=True,
              help='Password associated with the Username that is able to query Jira')
@click.option('-s', '--server',
              required=True,
              help='Jira server URL')
@click.option('-k', '--key',
              required=True,
              help='Issue key to analyse')
@click.option('-d', '--date', type=click.DateTime(formats=["%Y-%m-%d"]),
              help='Status of Jira issue key should reflect this date',
              default=str(datetime.now()))
@click.option('--verbose',
              is_flag=True,
              help='Increase verbosity for more logging')
def main(username, password, server, key, date, verbose):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format='%(levelname)s: %(message)s')

    jira = jira_history.Jira(url=server, username=username, password=password)
    print(jira.get_issue(key=key, date=date))

    return 0
