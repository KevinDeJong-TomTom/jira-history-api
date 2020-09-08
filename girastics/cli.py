#!/usr/bin/env python3

# Copyright (c) 2020 - 2020 TomTom N.V. All rights reserved.
#
# This software is the proprietary copyright of TomTom N.V. and its subsidiaries and may be
# used for internal evaluation purposes or commercial use strictly subject to separate
# licensee agreement between you and TomTom. If you are the licensee, you are only permitted
# to use this Software in accordance with the terms of your license agreement. If you are
# not the licensee, then you are not authorized to use this software in any manner and should
# immediately return it to TomTom N.V.
from .jira import Jira

import click
import logging

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
def main(username, password):
    logging.basicConfig(level=logging.DEBUG if True else logging.INFO,
                        format='%(levelname)s: %(message)s')

    jira = Jira(url='https://jira.tomtomgroup.com', username=username, password=password)
    jira.get_issue('PIPE-100')

    return 0
