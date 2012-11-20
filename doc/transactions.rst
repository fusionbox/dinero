Transactions
------------

.. currentmodule:: dinero

Transaction objects contain data about payments.  Every transaction object has
a ``transaction_id`` and a ``price``.


You can create a basic credit card transaction by using
:meth:`Transaction.create`::

    >>> import dinero
    >>> transaction = dinero.Transaction.create(
            price=200,
            number='4111111111111111',
            month='12',
            year='2015',
        )
    >>> transaction.transaction_id
    '0123456789'

This will charge the credit card $200.  If you store the ``transaction_id``,
you can later retrieve the transaction object. ::

    >>> transaction = dinero.Transaction.retrieve('0123456789')
    >>> transaction.price
    200

.. note::
    Like many methods in dinero, :meth:`Transaction.create` and :meth:`Transaction.retrieve`
    accept a ``gateway_name`` parameter.  This parameter corresponds with the
    gateway name that you created when configuring your gateways.

    If you had the following configuration::

        import dinero
        dinero.configure({
            'new-auth.net': {
                'type': 'dinero.gateways.AuthorizeNet',
                'default': True,
                ...
            },
            'old-auth.net': {
                'type': 'dinero.gateways.AuthorizeNet',
                ...
            },
        })

    If you don't specify ``gateway_name``, it will use ``new-auth.net``.  If
    you wanted to use ``old-auth.net``, you could do something like the
    following::

        dinero.Transaction.create(
            gateway_name='old-auth.net',
            price=200,
            ...
        )


When you have a transaction object, you can refund it::

    transaction.refund()

If a transaction has not yet been settled, the transaction will simply be
voided, otherwise an actual refund will take place.  If a transaction has
settled, you can pass refund the optional ``amount`` argument, in case you only
want to give a partial refund. ::

    transaction.refund(100)


Delayed Settlement
==================

By default, dinero will automatically submit a transaction for settlement,
however you can override this by setting the ``settle`` argument to ``False``.
When you need to settle a transaction, you can call
:meth:`Transaction.settle`::

    transaction = dinero.Transaction.create(
        price=200,
        number='4111111111111111',
        month='12',
        year='2015',
        settle=False,
    )

    ...

    transaction.settle()

If you need to cancel a transaction instead of settling it, just call
:meth:`Transaction.refund`.

API
===

.. autoclass:: Transaction

    .. automethod:: create(price, **kwargs)
    .. automethod:: retrieve(transaction_id[, gateway_name=None])
    .. automethod:: refund([amount=None])
    .. automethod:: settle([amount=None])
