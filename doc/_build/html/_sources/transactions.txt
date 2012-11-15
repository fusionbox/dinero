Transactions
------------

.. py:currentmodule:: dinero.transaction

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
    >>> transaction

This will charge the credit card $200.  If you store the ``transaction_id``,
you can later retrieve the transaction object. ::

    >>> transaction = dinero.Transaction.retrieve('0123456789')

When you have a transaction object, you can refund it::

    transaction.refund()

Refund takes an optional ``amount`` argument, in case you only wish to give a
partial refund. ::

    transaction.refund(100)


Delayed Settlement
==================

By default, dinero will automatically submit a transaction for settlement,
however you can override this by setting the ``settle`` argument to ``False``.
When you need to settle a transaction, you can call :meth:`Transaction.settle`::

    transaction = dinero.Transaction.create(
            price=200,
            number='4111111111111111',
            month='12',
            year='2015',
            settle=False,
        )
    ...
    transaction.settle()



API
===

.. autoclass:: Transaction

    .. automethod:: create(price, **kwargs)
    .. automethod:: retrieve(transaction_id[, gateway_name=None])
    .. automethod:: refund([amount=None])
    .. automethod:: settle([amount=None])
