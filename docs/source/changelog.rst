Changelog
================================

1.2.4-beta
---------------------------------------

**Bug fixes:**
    -Fix creation of logging handlers

1.2.3-beta
---------------------------------------

**Bug fixes:**
    -Checks for naming.conf existance when loading a repo and resets both rules and tokens

1.2.2-beta
---------------------------------------

**Improvements:**
    -Added remove_option(), update_option(), has_option_fullname(), has_option_abbreviation() methods to Token

1.2.1-beta
---------------------------------------

**Changes:**
    - Default option when adding Tokens must now be one the options passed for the Token.
    - Default option can now be explicitly passed as the full name option or its abbreviation.
    - When Parsing, if no value matches with the Token options and Token is Optional, raise TokenError.
    - IMPORTANT NOTE: This version might require updates on old Tokens that accepted any default value before. Quick and simple fix is to add that value as an option for the Token.


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