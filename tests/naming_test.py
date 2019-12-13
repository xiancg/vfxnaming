# coding=utf-8
from __future__ import absolute_import, print_function

from naming import naming as n
from naming.naming import Token, Rule

import pytest
import tempfile


class Test_Solve:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.reset_tokens()
        n.add_token('whatAffects')
        n.add_token_number('digits')
        n.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.add_token(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )
        n.add_separator('underscore', '_')
        n.reset_rules()
        n.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'digits', 'underscore', 'type'
        )

    def test_explicit(self):
        name = 'natural_ambient_chars_001_LGT'
        solved = n.solve(category='natural', function='ambient',
                         whatAffects='chars', digits=1, type='lighting')
        assert solved == name

    def test_no_match_for_token(self):
        with pytest.raises(Exception) as exception:
            n.solve(
                category='natural', function='sarasa',
                whatAffects='chars', digits=1, type='lighting'
            )
        assert str(exception.value).startswith("name") is True

    def test_missing_required_token(self):
        with pytest.raises(Exception) as exception:
            n.solve(
                category='natural', function='key', digits=1, type='lighting'
            )
        assert str(exception.value).startswith("Token") is True

    def test_missing_not_required_token(self):
        with pytest.raises(IndexError) as exception:
            n.solve('chars')
        assert str(exception.value).startswith("Missing argument for field") is True

    def test_defaults(self):
        name = 'natural_custom_chars_001_LGT'
        solved = n.solve(category='natural', whatAffects='chars',
                         digits=1, type='lighting')
        assert solved == name

        name = 'natural_custom_chars_001_LGT'
        solved = n.solve(whatAffects='chars', digits=1)
        assert solved == name

    def test_implicit(self):
        name = 'natural_custom_chars_001_ANI'
        solved = n.solve('chars', 1, type='animation')
        assert solved == name

        name = 'natural_custom_chars_001_LGT'
        solved = n.solve('chars', 1)
        assert solved == name


class Test_Parse:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.reset_tokens()
        n.add_token('whatAffects')
        n.add_token_number('digits')
        n.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.add_token(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )

    def test_parsing_with_separators(self):
        n.add_separator('underscore', '_')
        n.reset_rules()
        n.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'digits', 'underscore', 'type'
        )
        name = 'dramatic_bounce_chars_001_LGT'
        parsed = n.parse(name)
        assert parsed['category'] == 'dramatic'
        assert parsed['function'] == 'bounce'
        assert parsed['whatAffects'] == 'chars'
        assert parsed['digits'] == 1
        assert parsed['type'] == 'lighting'

    def test_parsing_without_separators_returns_none(self):
        n.reset_rules()
        n.add_rule(
            'lights',
            'category', 'function', 'whatAffects', 'digits', 'type'
        )
        name = 'dramatic_bounce_chars_001_LGT'
        parsed = n.parse(name)
        assert parsed is None


class Test_Token:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.reset_tokens()

    def test_add(self):
        result = n.add_token('whatAffects')
        assert isinstance(result, Token) is True

        result = n.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        assert isinstance(result, Token) is True

    def test_reset_tokens(self):
        result = n.reset_tokens()
        assert result is True

    def test_remove_token(self):
        n.add_token('test')
        result = n.remove_token('test')
        assert result is True

        result = n.remove_token('test2')
        assert result is False


class Test_Rule:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.reset_rules()

    def test_add(self):
        result = n.add_rule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        assert isinstance(result, Rule) is True

    def test_reset_rules(self):
        result = n.reset_rules()
        assert result is True

    def test_remove_rule(self):
        n.add_rule('test', 'category', 'function', 'digits', 'type')
        result = n.remove_rule('test')
        assert result is True

        result = n.remove_rule('test2')
        assert result is False

    def test_active(self):
        # pattern = '{category}_{function}_{digits}_{type}'
        n.add_rule('lights', 'category', 'function', 'whatAffects', 'digits', 'type')
        n.add_rule('test', 'category', 'function', 'digits', 'type')
        n.set_active_rule('test')
        result = n.get_active_rule()
        assert result is not None


class Test_Serialization:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.reset_rules()
        n.reset_tokens()

    def test_tokens(self):
        token1 = n.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        token2 = n.Token.from_data(token1.data())
        assert token1.data() == token2.data()

    def test_rules(self):
        rule1 = n.add_rule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        rule2 = n.Rule.from_data(rule1.data())
        assert rule1.data() == rule2.data()

    def test_validation(self):
        token = n.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        rule = n.add_rule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        assert n.Rule.from_data(token.data()) is None
        assert n.Token.from_data(rule.data()) is None

    def test_save_load_rule(self):
        n.add_rule('test', 'category', 'function', 'whatAffects', 'digits', 'type')
        filepath = tempfile.mktemp()
        n.save_rule('test', filepath)

        n.reset_rules()
        n.load_rule(filepath)
        assert n.has_rule('test') is True

    def test_save_load_token(self):
        n.add_token(
            'test', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        filepath = tempfile.mktemp()
        n.save_token('test', filepath)

        n.reset_tokens()
        n.load_token(filepath)
        assert n.has_token('test') is True

    def test_save_load_session(self):
        n.add_token('whatAffects')
        n.add_token_number('digits')
        n.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.add_token(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )
        n.add_rule('lights', 'category', 'function', 'whatAffects', 'digits', 'type')
        n.add_rule('test', 'category', 'function')
        n.set_active_rule('lights')

        repo = tempfile.mkdtemp()
        n.save_session(repo)

        n.reset_rules()
        n.reset_tokens()

        n.load_session(repo)
        assert n.has_token('whatAffects') is True
        assert n.has_token('digits') is True
        assert n.has_token('category') is True
        assert n.has_token('function') is True
        assert n.has_token('type') is True
        assert n.has_rule('lights') is True
        assert n.has_rule('test') is True
        assert n.get_active_rule().name == 'lights'


class Test_TokenNumber:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.reset_tokens()
        n.add_token('whatAffects')
        n.add_token_number('number')
        n.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.add_token('type', lighting='LGT', default='LGT')
        n.add_separator('underscore', '_')
        n.add_rule(
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


class Test_Separator:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.reset_tokens()
        n.add_token('whatAffects')
        n.add_token_number('number')
        n.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.add_token('type', lighting='LGT', default='LGT')

    def test_add_underscore(self):
        n.add_separator('underscore', '_')
        n.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'number', 'underscore', 'type'
        )
        name = 'natural_custom_chars_032_LGT'
        solved = n.solve('chars', 32)
        assert solved == name

    def test_rule_multiple_separators(self):
        n.add_separator('underscore', '_')
        n.add_separator('dot', '.')
        n.add_separator('hyphen', '-')
        n.add_rule(
            'lights',
            'category', 'underscore', 'function', 'dot', 'whatAffects',
            'hyphen', 'number', 'underscore', 'type'
        )
        name = 'natural_custom.chars-032_LGT'
        solved = n.solve('chars', 32)
        assert solved == name

    def test_rule_without_separators(self):
        n.add_rule(
            'lights',
            'category', 'function', 'whatAffects', 'number','type'
        )
        name = 'naturalcustomchars032LGT'
        solved = n.solve('chars', 32)
        print(solved)
        assert solved == name
