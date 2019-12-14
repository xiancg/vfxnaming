# coding=utf-8
from __future__ import absolute_import, print_function

from naming import naming as n
import naming.separators as separators
import naming.rules as rules
import naming.tokens as tokens
from naming import logger

import pytest

# Debug logging
logger.init_logger()
# logger.init_file_logger()

class Test_Token:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()

    def test_add(self):
        result = tokens.add_token('whatAffects')
        assert isinstance(result, tokens.Token) is True

        result = tokens.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        assert isinstance(result, tokens.Token) is True

    def test_reset_tokens(self):
        result = tokens.reset_tokens()
        assert result is True

    def test_remove_token(self):
        tokens.add_token('test')
        result = tokens.remove_token('test')
        assert result is True

        result = tokens.remove_token('test2')
        assert result is False


class Test_TokenNumber:
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
        separators.add_separator('underscore', '_')
        rules.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'number', 'underscore', 'type'
        )

    def test_explicit_solve(self):
        name = 'natural_ambient_chars_024_LGT'
        solved = n.solve(
            category='natural', function='ambient',
            whatAffects='chars', number=24, type='lighting'
            )
        assert solved == name

    def test_implicit_solve(self):
        name = 'natural_custom_chars_032_LGT'
        solved = n.solve('chars', 32)
        assert solved == name

    def test_prefix_suffix_padding_solve(self):
        name = 'natural_custom_chars_v0032rt_LGT'
        tokens.remove_token('number')
        tokens.add_token_number(
            'number', prefix='v', suffix='rt', padding=4
        )
        solved = n.solve('chars', 32)
        assert solved == name

    def test_prefix_suffix_padding_parse(self):
        name = 'natural_custom_chars_v0032rt_LGT'
        tokens.remove_token('number')
        tokens.add_token_number(
            'number', prefix='v', suffix='rt', padding=4
        )
        parsed = n.parse(name)
        assert parsed['category'] == 'natural'
        assert parsed['function'] == 'custom'
        assert parsed['whatAffects'] == 'chars'
        assert parsed['number'] == 32
        assert parsed['type'] == 'lighting'

    def test_prefix_only(self):
        name = 'natural_custom_chars_v0078_LGT'
        tokens.remove_token('number')
        tokens.add_token_number(
            'number', prefix='v', padding=4
        )
        parsed = n.parse(name)
        assert parsed['category'] == 'natural'
        assert parsed['function'] == 'custom'
        assert parsed['whatAffects'] == 'chars'
        assert parsed['number'] == 78
        assert parsed['type'] == 'lighting'

    def test_suffix_only(self):
        name = 'natural_custom_chars_0062rt_LGT'
        tokens.remove_token('number')
        tokens.add_token_number(
            'number', suffix='rt', padding=4
        )
        parsed = n.parse(name)
        assert parsed['category'] == 'natural'
        assert parsed['function'] == 'custom'
        assert parsed['whatAffects'] == 'chars'
        assert parsed['number'] == 62
        assert parsed['type'] == 'lighting'
