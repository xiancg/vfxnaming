from typing import List

from vfxnaming import naming as n
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens

import pytest


class Test_Token:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()

    @pytest.mark.parametrize(
        "name,fallback,kwargs",
        [
            ("test", "", {}),
            (
                "category",
                "",
                {
                    "natural": "natural",
                    "practical": "practical",
                    "dramatic": "dramatic",
                    "volumetric": "volumetric",
                    "default": "natural",
                },
            ),
            ("fallbacktest", "imfallback", {}),
        ],
    )
    def test_add(self, name: str, fallback: str, kwargs):
        result = tokens.add_token(name, fallback, **kwargs)
        assert isinstance(result, tokens.Token) is True

    def test_reset_tokens(self):
        result = tokens.reset_tokens()
        assert result is True

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("test", True),
            ("test2", False),
        ],
    )
    def test_remove_token(self, name: str, expected: bool):
        tokens.add_token("test")
        result = tokens.remove_token(name)
        assert result is expected


class Test_Token_Options:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        self.light_category = tokens.add_token(
            "category",
            natural="natural",
            practical="practical",
            dramatic="dramatic",
            volumetric="volumetric",
            default="natural",
        )

    @pytest.mark.parametrize(
        "key,abbreviation,expected",
        [
            ("extra", "extra", True),
            ("dramatic", "DRA", False),
        ],
    )
    def test_add_option(self, key: str, abbreviation: str, expected: bool):
        result = self.light_category.add_option(key, abbreviation)
        assert result is expected

    @pytest.mark.parametrize(
        "key,expected",
        [
            ("natural", True),
            ("non_existent", False),
        ],
    )
    def test_remove_option(self, key: str, expected: bool):
        result = self.light_category.remove_option(key)
        assert result is expected

    @pytest.mark.parametrize(
        "old_key,new_key,expected",
        [
            ("natural", "unnatural", True),
            ("non_existent", "unnatural", False),
        ],
    )
    def test_update_option(self, old_key: str, new_key: str, expected: bool):
        result = self.light_category.update_option(old_key, new_key)
        assert result is expected

    @pytest.mark.parametrize(
        "full_name,expected",
        [
            ("dramatic", True),
            ("default", False),
        ],
    )
    def test_has_option_fullname(self, full_name: str, expected: bool):
        result = self.light_category.has_option_fullname(full_name)
        assert result is expected

    @pytest.mark.parametrize(
        "abbreviation,expected",
        [
            ("volumetric", True),
            ("VOL", False),
        ],
    )
    def test_has_option_abbreviation(self, abbreviation: str, expected: bool):
        result = self.light_category.has_option_abbreviation(abbreviation)
        assert result is expected


class Test_TokenFallback:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()
        tokens.reset_tokens()
        tokens.add_token("whatAffects", fallback="nothing")
        tokens.add_token_number("number")
        tokens.add_token(
            "category",
            natural="natural",
            practical="practical",
            dramatic="dramatic",
            volumetric="volumetric",
            default="natural",
        )
        tokens.add_token(
            "function",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            kick="kick",
            custom="custom",
            default="custom",
        )
        tokens.add_token("type", lighting="LGT", default="LGT")
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{number}_{type}")

    def test_token_has_fallback(self):
        assert tokens.get_token("whatAffects").fallback == "nothing"

    @pytest.mark.parametrize(
        "name,data,expected",
        [
            (
                "natural_ambient_chars_024_LGT",
                {
                    "category": "natural",
                    "function": "ambient",
                    "whatAffects": "chars",
                    "number": 24,
                    "type": "lighting",
                },
                True,
            ),
            (
                "natural_ambient_nothing_003_LGT",
                {
                    "category": "natural",
                    "function": "ambient",
                    "number": 3,
                    "type": "lighting",
                },
                True,
            ),
        ],
    )
    def test_fallback_solve(self, name: str, data: dict, expected: bool):
        solved = n.solve(**data)
        assert (name == solved) is expected


class Test_TokenNumber:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()
        tokens.reset_tokens()
        tokens.add_token("whatAffects")
        tokens.add_token_number("number")
        tokens.add_token(
            "category",
            natural="natural",
            practical="practical",
            dramatic="dramatic",
            volumetric="volumetric",
            default="natural",
        )
        tokens.add_token(
            "function",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            kick="kick",
            custom="custom",
            default="custom",
        )
        tokens.add_token("type", lighting="LGT", default="LGT")
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{number}_{type}")

    @pytest.mark.parametrize(
        "name,data,expected",
        [
            (
                "natural_ambient_chars_024_LGT",
                {
                    "category": "natural",
                    "function": "ambient",
                    "whatAffects": "chars",
                    "number": 24,
                    "type": "lighting",
                },
                True,
            ),
            (
                "natural_ambient_chars_3_LGT",
                {
                    "category": "natural",
                    "function": "ambient",
                    "whatAffects": "chars",
                    "number": 3,
                    "type": "lighting",
                },
                False,
            ),
        ],
    )
    def test_explicit_solve(self, name: str, data: dict, expected: bool):
        solved = n.solve(**data)
        assert (solved == name) is expected

    @pytest.mark.parametrize(
        "name,data,expected",
        [
            (
                "natural_custom_chars_032_LGT",
                ["chars", 32],
                True,
            ),
            (
                "natural_custom_chars_3_LGT",
                ["chars", 3],
                False,
            ),
        ],
    )
    def test_implicit_solve(self, name: str, data: List, expected: bool):
        solved = n.solve(*data)
        assert (solved == name) is expected

    @pytest.mark.parametrize(
        "name,prefix,suffix,padding",
        [
            ("natural_custom_chars_v0032rt_LGT", "v", "rt", 4),
            ("natural_custom_chars_ver32X_LGT", "ver", "X", 2),
        ],
    )
    def test_prefix_suffix_padding_solve(
        self, name: str, prefix: str, suffix: str, padding: int
    ):
        tokens.remove_token("number")
        tokens.add_token_number("number", prefix=prefix, suffix=suffix, padding=padding)
        solved = n.solve("chars", 32)
        assert solved == name

    @pytest.mark.parametrize(
        "name,prefix,suffix,padding,num",
        [
            ("natural_custom_chars_v0076rt_LGT", "v", "rt", 4, 76),
            ("natural_custom_chars_ver1850X_LGT", "ver", "X", 2, 1850),
        ],
    )
    def test_prefix_suffix_padding_parse(
        self, name: str, prefix: str, suffix: str, padding: int, num: int
    ):
        tokens.remove_token("number")
        tokens.add_token_number("number", prefix=prefix, suffix=suffix, padding=padding)
        parsed = n.parse(name)
        assert parsed["category"] == "natural"
        assert parsed["function"] == "custom"
        assert parsed["whatAffects"] == "chars"
        assert parsed["number"] == num
        assert parsed["type"] == "lighting"

    def test_prefix_only(self):
        name = "natural_custom_chars_v0078_LGT"
        tokens.remove_token("number")
        tokens.add_token_number("number", prefix="W", padding=4)
        parsed = n.parse(name)
        assert parsed["category"] == "natural"
        assert parsed["function"] == "custom"
        assert parsed["whatAffects"] == "chars"
        assert parsed["number"] == 78
        assert parsed["type"] == "lighting"

    def test_suffix_only(self):
        name = "natural_custom_chars_0062rt_LGT"
        tokens.remove_token("number")
        tokens.add_token_number("number", suffix="rt", padding=4)
        parsed = n.parse(name)
        assert parsed["category"] == "natural"
        assert parsed["function"] == "custom"
        assert parsed["whatAffects"] == "chars"
        assert parsed["number"] == 62
        assert parsed["type"] == "lighting"
