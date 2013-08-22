Gateways
--------

A payment gateway is what takes the credit card information and changes that
into money in your bank account.  Dinero currently supports Authorize.Net and
has some support for Braintree Payments.

In order to use dinero, you must first configure a gateway.  The basic configuration looks like::

    import dinero
    
    dinero.configure({
        'foo': {
            'type': 'XXX',
            'default': True,
            # ...
        },
    })

where ``foo`` is a reference name for you to remember.  The ``type`` is the
class that implements the gateway.  Dinero currently has the following gateway types:

- :class:`dinero.gateways.authorizenet.Gateway`
- :class:`dinero.gateways.Braintree` (incomplete implementation)

The gateway marked ``default`` will be used by default when creating transactions.


.. py:class:: dinero.gateways.authorizenet.Gateway

The Authorize.Net gateway requires the following packages.

- requests
- lxml

In order to configure the Authorize.Net gateway, you need the Login ID and the
Transaction Key. ::

    import dinero

    dinero.configure({
        'foo': {
            'type': 'dinero.gateways.authorizenet.Gateway',
            'default': True,
            'login_id': 'XXX',
            'transaction_key': 'XXX',
        },
    })
