Validating
=====================

Many times the only thing we need is to know if a name is valid or not for a given rule. Each Rule validates the name according to next criteria:

- The name must have the same number of tokens as the rule.
- The tokens must be in the same order as the rule.
- The number of expected separators must match with the rule.
- If tokens have options, the given name must use one of those options.
- If token is a number, validates suffix, prefix and padding.