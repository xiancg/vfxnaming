# coding=utf-8
from __future__ import absolute_import, print_function

from naming import naming as n
from naming.naming import Token, Rule

import pytest
import tempfile


class Test_Solve:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.resetTokens()
        n.addToken('whatAffects')
        n.addTokenNumber('digits')
        n.addToken(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.addToken(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.addToken(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )
        n.resetRules()
        n.addRule('lights', 'category', 'function', 'whatAffects', 'digits', 'type')

    def test_explicit(self):
        name = 'natural_ambient_chars_001_LGT'
        solved = n.solve(category='natural', function='ambient',
                         whatAffects='chars', digits=1, type='lighting')
        assert solved == name

    def test_noMatchForToken(self):
        name = 'natural_ambient_chars_001_LGT'
        solved = n.solve(category='natural', function='sarasa',
                         whatAffects='chars', digits=1, type='lighting')
        assert name != solved

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
        n.resetTokens()
        n.addToken('whatAffects')
        n.addTokenNumber('digits')
        n.addToken(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.addToken(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.addToken(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )
        n.resetRules()
        n.addRule('lights', 'category', 'function', 'whatAffects', 'digits', 'type')

    def test_parsing(self):
        name = 'dramatic_bounce_chars_001_LGT'
        parsed = n.parse(name)
        assert parsed['category'] == 'dramatic'
        assert parsed['function'] == 'bounce'
        assert parsed['whatAffects'] == 'chars'
        assert parsed['digits'] == 1
        assert parsed['type'] == 'lighting'


class Test_Token:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.resetTokens()

    def test_add(self):
        result = n.addToken('whatAffects')
        assert isinstance(result, Token) is True

        result = n.addToken(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        assert isinstance(result, Token) is True

    def test_resetTokens(self):
        result = n.resetTokens()
        assert result is True

    def test_removeToken(self):
        n.addToken('test')
        result = n.removeToken('test')
        assert result is True

        result = n.removeToken('test2')
        assert result is False


class Test_Rule:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.resetRules()

    def test_add(self):
        result = n.addRule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        assert isinstance(result, Rule) is True

    def test_resetRules(self):
        result = n.resetRules()
        assert result is True

    def test_removeRule(self):
        n.addRule('test', 'category', 'function', 'digits', 'type')
        result = n.removeRule('test')
        assert result is True

        result = n.removeRule('test2')
        assert result is False

    def test_active(self):
        # pattern = '{category}_{function}_{digits}_{type}'
        n.addRule('lights', 'category', 'function', 'whatAffects', 'digits', 'type')
        n.addRule('test', 'category', 'function', 'digits', 'type')
        n.setActiveRule('test')
        result = n.getActiveRule()
        assert result is not None


class Test_Serialization:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.resetRules()
        n.resetTokens()

    def test_tokens(self):
        token1 = n.addToken(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        token2 = n.Token.fromData(token1.data())
        assert token1.data() == token2.data()

    def test_rules(self):
        rule1 = n.addRule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        rule2 = n.Rule.fromData(rule1.data())
        assert rule1.data() == rule2.data()

    def test_validation(self):
        token = n.addToken(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        rule = n.addRule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        assert n.Rule.fromData(token.data()) is None
        assert n.Token.fromData(rule.data()) is None

    def test_save_load_rule(self):
        n.addRule('test', 'category', 'function', 'whatAffects', 'digits', 'type')
        filepath = tempfile.mktemp()
        n.saveRule('test', filepath)

        n.resetRules()
        n.loadRule(filepath)
        assert n.hasRule('test') is True

    def test_save_load_token(self):
        n.addToken(
            'test', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        filepath = tempfile.mktemp()
        n.saveToken('test', filepath)

        n.resetTokens()
        n.loadToken(filepath)
        assert n.hasToken('test') is True

    def test_save_load_session(self):
        n.addToken('whatAffects')
        n.addTokenNumber('digits')
        n.addToken(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.addToken(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.addToken(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )
        n.addRule('lights', 'category', 'function', 'whatAffects', 'digits', 'type')
        n.addRule('test', 'category', 'function')
        n.setActiveRule('lights')

        repo = tempfile.mkdtemp()
        n.saveSession(repo)

        n.resetRules()
        n.resetTokens()

        n.loadSession(repo)
        assert n.hasToken('whatAffects') is True
        assert n.hasToken('digits') is True
        assert n.hasToken('category') is True
        assert n.hasToken('function') is True
        assert n.hasToken('type') is True
        assert n.hasRule('lights') is True
        assert n.hasRule('test') is True
        assert n.getActiveRule().name == 'lights'


class Test_TokenNumber:
    @pytest.fixture(autouse=True)
    def setup(self):
        n.resetTokens()
        n.addToken('whatAffects')
        n.addTokenNumber('number')
        n.addToken(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        n.addToken(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        n.addToken('type', lighting='LGT', default='LGT')
        n.addRule('lights', 'category', 'function', 'whatAffects', 'number', 'type')

    def test_explicitSolve(self):
        name = 'natural_ambient_chars_024_LGT'
        solved = n.solve(
            category='natural', function='ambient',
            whatAffects='chars', number=24, type='lighting'
            )
        assert solved == name

    def test_implicitSolve(self):
        name = 'natural_custom_chars_032_LGT'
        solved = n.solve('chars', 32)
        assert solved == name
