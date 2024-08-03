from vfxnaming import naming as n
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens

import pytest


class Test_Token:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()

    def test_add(self):
        result = tokens.add_token("whatAffects")
        assert isinstance(result, tokens.Token) is True

        result = tokens.add_token(
            "category",
            natural="natural",
            practical="practical",
            dramatic="dramatic",
            volumetric="volumetric",
            default="natural",
        )
        assert isinstance(result, tokens.Token) is True

    def test_reset_tokens(self):
        result = tokens.reset_tokens()
        assert result is True

    def test_remove_token(self):
        tokens.add_token("test")
        result = tokens.remove_token("test")
        assert result is True

        result = tokens.remove_token("test2")
        assert result is False


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

    def test_add_option(self):
        result = self.light_category.add_option("extra", "extra")
        assert result is True
        assert "extra" in self.light_category.options.keys()

        result = self.light_category.add_option("dramatic", "DRA")
        assert result is False

    def test_remove_option(self):
        result = self.light_category.remove_option("natural")
        assert result is True
        assert "natural" not in self.light_category.options.keys()

        result = self.light_category.remove_option("non_existent")
        assert result is False

    def test_update_option(self):
        result = self.light_category.update_option("natural", "unnatural")
        assert result is True
        assert "unnatural" in self.light_category.options.values()

        result = self.light_category.update_option("non_existent", "unnatural")
        assert result is False

    def test_has_option_fullname(self):
        result = self.light_category.has_option_fullname("dramatic")
        assert result is True

        result = self.light_category.has_option_fullname("default")
        assert result is False

    def test_has_option_abbreviation(self):
        result = self.light_category.has_option_abbreviation("volumetric")
        assert result is True

        result = self.light_category.has_option_abbreviation("VOL")
        assert result is False


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

    def test_explicit_solve(self):
        name = "natural_ambient_chars_024_LGT"
        solved = n.solve(
            category="natural",
            function="ambient",
            whatAffects="chars",
            number=24,
            type="lighting",
        )
        assert solved == name

    def test_implicit_solve(self):
        name = "natural_custom_chars_032_LGT"
        solved = n.solve("chars", 32)
        assert solved == name

    def test_prefix_suffix_padding_solve(self):
        name = "natural_custom_chars_v0032rt_LGT"
        tokens.remove_token("number")
        tokens.add_token_number("number", prefix="v", suffix="rt", padding=4)
        solved = n.solve("chars", 32)
        assert solved == name

    def test_prefix_suffix_padding_parse(self):
        name = "natural_custom_chars_v0032rt_LGT"
        tokens.remove_token("number")
        tokens.add_token_number("number", prefix="v", suffix="rt", padding=4)
        parsed = n.parse(name)
        assert parsed["category"] == "natural"
        assert parsed["function"] == "custom"
        assert parsed["whatAffects"] == "chars"
        assert parsed["number"] == 32
        assert parsed["type"] == "lighting"

    def test_prefix_only(self):
        name = "natural_custom_chars_v0078_LGT"
        tokens.remove_token("number")
        tokens.add_token_number("number", prefix="v", padding=4)
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
