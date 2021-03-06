#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cwam
----------------------------------

Tests for `cwam` module.
"""


import unittest
from click.testing import CliRunner

from cwam import cli


class TestCwam(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_something(self):
        pass

    def test_command_line_interface(self):
        runner = CliRunner()
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '-h, --help                      Show this message and exit.' in help_result.output  # noqa E501
