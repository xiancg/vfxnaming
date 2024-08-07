VFX Naming Conventions Docs
========================================

.. image:: https://github.com/xiancg/vfxnaming/actions/workflows/ci_vfxnaming.yml/badge.svg?event=push&branch=master
.. image:: https://readthedocs.org/projects/naming-conventions/badge/?version=latest
.. image:: https://img.shields.io/github/license/readthedocs/actions

Installation
------------

.. code-block:: python

    pip install vfxnaming

A complete suite of tools to manage naming conventions from one or more
"Rule repositories". Structure naming rules with your own custom tokens. Then use the library to solve names following those rules so your naming is consistent, and also to parse metadata from exisiting names (cus a name is basically a collection of metadata, right?)

General Ideas
-----------------

**vfxnaming** consists of three main entities: ``Token``, ``TokenNumber`` and ``Rule``. All of them are saved and read to and from a *repository* that contains their serialized versions.

A Rule is made of Tokens and hardcoded strings too. This is how a Rule pattern looks like. Values between curly braces '{ }' are Token placeholders.

.. note::
    '{category}_{function}_{whatAffects}_{digits}_{type}'

naming module
------------------------
``vfxnaming.naming`` is the main module of **vfxnaming**. Please refer to :doc:`vfxnaming` for further details.

It consists of two key functions:

    1. parse(path)
    2. solve(args, kwargs)

And three working functions:

    1. get_repo()
    2. load_session()
    3. save_session()

logger module
--------------------
``vfxnaming.logger`` uses Python logging to track almost everything that's happening under the hood. This is really useful for debugging. Please refer to :doc:`logger` for further details.

This is going to initialize the logger and output to stdout (console, terminal, etc)

.. code-block:: python

    from vfxnaming import logger
    logger.init_logger()

This is going to initalize a log file where everything will be recorded.

.. code-block:: python

    from vfxnaming import logger
    logger.init_file_logger()

Acknowledgements
--------------------

For more information please check :doc:`credits`

.. toctree::
   :maxdepth: 3
   :caption: Getting Started
   :hidden:
   
   usage/repositories
   usage/solving
   usage/parsing

.. toctree::
   :maxdepth: 3
   :caption: API Reference
   :hidden:
   
   vfxnaming
   rules
   tokens
   logger

.. toctree::
   :maxdepth: 3
   :caption: Changelog, Roadmap and Credits
   :hidden:

   changelog
   roadmap
   credits
