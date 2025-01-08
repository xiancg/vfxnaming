Tokens module
================
Tokens are the meaningful parts of a template. A token can be required, meaning fully typed by the user, or can have a set of options preconfigured.

If options are present, then one of them is the default one. Each option follows a {full_name:abbreviation} schema, so that names can be short but meaning can be recovered easily. The default option might be passed explicitly by the user by passing a *default* argument (it must match one of the options in the Token). If no default options is explicitly passed, the Token will sort options alphabetically and pick the first one. Please notice if you pass the *default* option explicitly, you can use the abbreviation or the full option name.

If fallback is defined, it will be used on required tokens if nothing is passed by the user.

.. code-block:: python
    :linenos:

    n.add_token('whatLights')
    n.add_token('shadowType', fallback='soft')
    n.add_token_number('digits')
    n.add_token('category', natural='nat', 
                practical='pra', dramatic='dra',
                volumetric='vol', default='nat')

In line 1 we're creating a **Required Token**. This means that in order to solve the user must provide a value, else an error will be raised. This is a explicit solve.

In line 2 we're creating a **Required Token** with a fallback. This means that if the user doesn't provide a value, the Token will solve to the fallback value. This is an implicit solve.

In line 3 we're creating a **Number Token**. This is a special Token really useful for working with version like or counting parts of a name. It's always required.

In line 4 we're creating an **Optional Token**, which means that for solving the user can pass one of the options in the Token or simply ignore passing a value and the Token will solve to it's default option. This is an implicit solve, which helps to greatly reduce the amount of info that needs to be passed to solve for certain cases.

For more information on implicit and explicit solving please check :doc:`usage/solving`

.. automodule:: vfxnaming.tokens
   :members:
