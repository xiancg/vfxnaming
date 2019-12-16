Naming session creation and loading
====================================

Session Creation
----------------

.. code-block:: python

    import cgx_naming as n

    n.add_token('whatAffects')
    n.add_token_number('digits')
    n.add_token('category', natural='nat', 
                practical='pra', dramatic='dra',
                volumetric='vol', default='nat')
    n.add_token('function', key='key', 
                fill='fil', ambient='amb',
                bounce='bnc', rim='rim',
                kick='kik', custom='cst', default='cst')
    n.add_separator('underscore', '_')
    n.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'digits', 'underscore', 'type'
        )
    n.save_session()

This will result in the following files being created:

    - lights.rule
    - naming.conf
    - category.token
    - function.token
    - digits.token
    - type.token
    - whatAffects.token

Session Loading
----------------

These files can then be read from next time you need to use your new naming rules by passing
the repo location to the load_session function:

    .. code-block:: python

        import cgx_naming as n

        n.load_session()

        all_rules = n.get_rules()
        all_tokens = n.get_tokens()
        all_separators = n.get_separators()
