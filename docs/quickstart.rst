Quickstart
----------

1. Configure
============

The first thing you need to do in order to use dinero is to configure your
gateways(s).  The following example would be configuration for an Authorize.Net gateway::

    import dinero

    dinero.configure({
        # a name that you can remember
        'auth.net': {
            'type': 'dinero.gateways.authorizenet.Gateway',
            'default': True,
            # Gateway specific configuration
            'login_id': 'XXX',
            'transaction_key': 'XXX',
        }
    })


2. Make Transactions
====================

Now that you have a gateway configured, you can create transactions. ::

    transcation = dinero.Transaction.create(
        price=2000,
        number='4111111111111111',
        month='12',
        year='2012',
    )

3. Profit
=========

Well that's up to you now isn't it.
