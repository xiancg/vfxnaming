import vfxnaming.rules as rules

import pytest


class Test_Rule:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()

    @pytest.mark.parametrize(
        "name,pattern,expected",
        [
            ("lights", "{category}_{function}_{whatAffects}_{digits}_{type}", True),
            ("filename", "{side}-{region}_{side}-{region}_{side}-{region}", True),
            ("nope", "", False),  # TODO: Working here, this shouldn't be passing
        ],
    )
    def test_add(self, name: str, pattern: str, expected: bool):
        result = rules.add_rule(name, pattern)
        assert isinstance(result, rules.Rule) is expected

    def test_reset_rules(self):
        result = rules.reset_rules()
        assert result is True

    def test_remove_rule(self):
        rules.add_rule("test", "{category}_{function}_{digits}_{type}")
        result = rules.remove_rule("test")
        assert result is True

        result = rules.remove_rule("test2")
        assert result is False

    def test_active(self):
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{digits}_{type}")
        rules.add_rule("test", "{category}_{function}_{digits}_{type}")
        rules.set_active_rule("test")
        result = rules.get_active_rule()
        assert result is not None
