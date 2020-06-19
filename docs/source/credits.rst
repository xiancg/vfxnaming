Credits
========================================

Chris Granados - Xian
-----------------------

I'm the author and mantainer of **vfxnaming**.

Cesar Saez
---------------
**vfxnaming** is completely based on `Copyright (c) 2017 Cesar Saez <https://www.cesarsaez.me/>`_
work. I highly recommend his `Website-Blog <https://www.cesarsaez.me/>`_ and
the video tutorial series on his `YouTube Channel <https://www.youtube.com/channel/UCRjk6bi_1ZQ9sL69agz0xMg>`_ 

-Why no fork from `Cesar's Repo <https://github.com/csaez/naming>`_?

    I found myself using and modifying his code to fit my needs. Not only that,
    but he has an AMAZING video tutorial series on this topic and my code deviated
    a bit too much from what he shows in the videos.

-What are the main differences from Cesar's?

    1. Implemented a special Token for numbers with the ability to handle pure
    digits and version like strings (e.g.: v0025) with padding settings.

    2. Implemented Separators. Used to be a completely separate object in older versions, but now separators are simply inferred from the regular expressions used.

    3. Switched the entire test suite to pytest which is what I use for standalone stuff.

    4. Refactored the code to make it a bit more modular. Which in turn makes it
    less portable, but it was getting too long otherwise with my modifications. To compensate for portability, it's pip installable now.

Martin Pengelly-Phillips
---------------------------

The regular expressions logic was taken in part from the work Martin Pengelly-Phillips did on Lucidity. Also tweaked and modified a lot to fit my needs, so don't expect the same Lucidity behaviour.