# Naming Conventions Library

[![Build Status](https://travis-ci.org/xiancg/naming.svg?branch=master)](https://travis-ci.org/xiancg/naming)
[![Documentation Status](https://readthedocs.org/projects/naming-conventions/badge/?version=latest)](https://naming-conventions.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/xiancg/naming/badge.svg?branch=master)](https://coveralls.io/github/xiancg/naming?branch=master)

# Documentation
[Naming Conventions Docs](http://naming-conventions.rtfd.io/)

A complete suite of tools to manage naming conventions from one or more "Rules repositories". Structure naming rules with your own custom tokens and separators. Then use the library to solve names following those rules so your naming is consistent, and also to parse metadata from exisiting names (cus a name is basically a collection of metadata right?)

This is completely based on [Copyright (c) 2017 Cesar Saez](https://www.cesarsaez.me/) work. I highly recommend his [Website-Blog](https://www.cesarsaez.me/) and the video tutorial series on his [YouTube Channel](https://www.youtube.com/channel/UCRjk6bi_1ZQ9sL69agz0xMg)

Why no fork from [Cesar's Repo](https://github.com/csaez/naming)?
I found myself using and modifying his code to fit my needs. Not only that, but he has an AMAZING video tutorial series on this topic and my code deviated a bit too much from what he shows in the videos.

What are the main differences from Cesar's?
1. Implemented a special Token for numbers with the ability to handle pure digits and version like strings (e.g.: v0025) with padding settings.
2. Implemented Separators, so not only underscores can be used, but also hyphens, dots, etc, in any combination.
3. Switched the entire test suite to pytest which is what I use.
4. Refactored the code to make it a bit more modular. Which in turn makes it less portable, but it was getting too long otherwise with my modifications.