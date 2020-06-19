Tokens module
================
Tokens are the meaningful parts of a template. A token can be required, meaning fully typed by the user, or can have a set of default options preconfigured.

If options are present, then one of them is the default one. Each option follows a {full_name:abbreviation} schema, so that names can be short but meaning can be recovered easily.

.. code-block:: python
    :linenos:

    n.add_token('whatAffects')
    n.add_token_number('digits')
    n.add_token('category', natural='nat', 
                practical='pra', dramatic='dra',
                volumetric='vol', default='nat')

In line 1 we're creating a **Required Token**. This means that for solving the user has to provide a value. This is a explicit solve.

In line 2 we're creating a **Number Token**. This is a special Token really useful for working with version like or counting parts of a name. It's always required.

In line 3 we're creating an **Optional Token**, which means that for solving the user can pass one of the options in the Token or simply ignore passing a value and the Token will solve to it's default option. This is an implicit solve, which helps to greatly reduce the amount of info that needs to be passed to solve for certain cases.

For more information on implicit and explicit solving please check :doc:`usage/solving`

.. automodule:: vfxnaming.tokens
   :members:
