Changelog
================================

1.2.0-beta
---------------------------------------

**Features:**
    - Adds anchoring, so each Rule may be able to parse and solve from right to left, or left to right. Useful for Rules with hardcoded values (not only Tokens)
    - Solving and parsing now use Regular Expressions under the hood.
    - A lot of updates to docs.

**Changes:**
    - Removes Separator entity
    - IMPORTANT NOTE: This version is not backwards compatible

1.1.6-beta
---------------------------------------

**Features:**
    - Adds support for parsing and solving repeated tokens within the same rule.

**Improvements:**
    - Added documentation for the entire package
    - Added custom errors

1.0.0-alpha
---------------------------------------

**Features:**
    - Parsing of metadata from names (Including version like strings with digits)
    - Solving names using pre-established Rules and Tokens
    - Repository saving and loading of serialized Rules and Tokens in json format