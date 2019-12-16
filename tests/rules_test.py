# coding=utf-8
from __future__ import absolute_import, print_function

import cgx_naming.rules as rules
from cgx_naming import logger

import pytest

# Debug logging
logger.init_logger()
# logger.init_file_logger()


class Test_Rule:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()

    def test_add(self):
        result = rules.add_rule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        assert isinstance(result, rules.Rule) is True

    def test_reset_rules(self):
        result = rules.reset_rules()
        assert result is True

    def test_remove_rule(self):
        rules.add_rule('test', 'category', 'function', 'digits', 'type')
        result = rules.remove_rule('test')
        assert result is True

        result = rules.remove_rule('test2')
        assert result is False

    def test_active(self):
        # pattern = '{category}_{function}_{digits}_{type}'
        rules.add_rule('lights', 'category', 'function', 'whatAffects', 'digits', 'type')
        rules.add_rule('test', 'category', 'function', 'digits', 'type')
        rules.set_active_rule('test')
        result = rules.get_active_rule()
        assert result is not None
