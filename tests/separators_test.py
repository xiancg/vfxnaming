# coding=utf-8
from __future__ import absolute_import, print_function

from vfxnaming import naming as n
import vfxnaming.separators as separators
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens
from vfxnaming import logger

import pytest

# Debug logging
logger.init_logger()
# logger.init_file_logger()


class Test_Separator:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()
        separators.reset_separators()
        tokens.reset_tokens()
        tokens.add_token('whatAffects')
        tokens.add_token_number('number')
        tokens.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        tokens.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        tokens.add_token('type', lighting='LGT', default='LGT')

    def test_add_underscore(self):
        separators.add_separator('underscore', '_')
        rules.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'number', 'underscore', 'type'
        )
        name = 'natural_custom_chars_032_LGT'
        solved = n.solve('chars', 32)
        assert solved == name

    def test_rule_multiple_separators(self):
        separators.add_separator('underscore', '_')
        separators.add_separator('dot', '.')
        separators.add_separator('hyphen', '-')
        rules.add_rule(
            'lights',
            'category', 'underscore', 'function', 'dot', 'whatAffects',
            'hyphen', 'number', 'underscore', 'type'
        )
        name = 'natural_custom.chars-032_LGT'
        solved = n.solve('chars', 32)
        assert solved == name

    def test_rule_without_separators(self):
        rules.add_rule(
            'lights',
            'category', 'function', 'whatAffects', 'number', 'type'
        )
        name = 'naturalcustomchars032LGT'
        solved = n.solve('chars', 32)
        assert solved == name

    def test_remove_separator(self):
        separators.add_separator('underscore', '_')
        result = separators.remove_separator('underscore')
        assert result is True

        result = separators.remove_separator('test2')
        assert result is False
