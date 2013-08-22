dinero
======

Gateway-agnostic payment processing library for Python.

This library aims to be a minimal, pythonic, and highly usable payment
processing library.  It has a simple API and it hides the differences between
payment processors from the user.

You can read the documentation for Dinero at <http://dinero.readthedocs.org>.

Contributing
------------

First you need to write a file in ``test/.env`` that looks like the following::

    AUTHNET_LOGIN_ID=xxxxxxxxxxx
    AUTHNET_TRANSACTION_KEY=xxxxxxxxxxxxxxxx

Then you can run the tests using::

    $ python setup.py test

or you can run them directly with::

    $ py.test

The tests require ``py.test`` and ``django-dotenv``.
