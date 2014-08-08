API Reference
-------------

.. class:: dinero.Transaction

    :class:`.` is an abstraction over payments in a gateway.  This is the
    interface for creating and interacting with payments.

    .. classmethod:: create(price, gateway_name=None, **kwargs)

        Creates a payment.  This method will actually charge your customer.
        :meth:`.` can be called in several different ways.

        You can call this with the credit card information directly. ::

            Transaction.create(
                price=200,
                number='4111111111111111',
                year='2015',
                month='12',

                # optional
                first_name='John',
                last_name='Smith,'
                zip='12345',
                address='123 Elm St',
                city='Denver',
                state='CO',
                cvv='900',
                email='johnsmith@example.com',
            )

        If you have a :class:`dinero.Customer` object, you can create a
        transaction against the customer. ::

            customer = Customer.create(
                # ...
            )

            Transaction.create(
                price=200,
                customer=customer,
            )

        Other payment options include ``card`` and ``check``.  See
        :class:`dinero.CreditCard` for more information.

    .. classmethod:: retrieve(transaction_id[, gateway_name=None])

        Fetches a transaction object from the gateway.

    .. method:: refund([amount=None])

        Payment gateways often allow you to refund only a certain amount of
        money from a transaction.  Refund abstracts the difference between
        refunding and voiding a payment so that normally you don't need to
        worry about it.  However, please note that you can't do a partial
        refund if the transaction hasn't settled.

        If ``amount`` is None dinero will refund the full price of the
        transaction.

    .. method:: settle([amount=None])

        If you create a transaction without settling it, you can settle it with
        this method.  It is possible to settle only part of a transaction.  If
        ``amount`` is ``None``, the full transaction price is settled.


.. class:: dinero.Customer

    A class for managing customer information.

    .. attributes:: customer_id

        This is the gateway-specific ID for the customer object.

    .. attributes:: first_name
    .. attributes:: last_name
    .. attributes:: email

    .. classmethod:: create(email, **kwargs)

        Creates and stores a customer object.  When you first create a
        customer, you are required to also pass in arguments for a credit card. ::

            Customer.create(
                email='bill@example.com',

                # required for credit card
                number='4111111111111111',
                cvv='900',
                month='12',
                year='2015',
                address='123 Elm St.',
                zip='12345',
            )

        This method also accepts ``gateway_name``.

    .. classmethod:: retrieve(customer_id[, gateway_name=None])

        Fetches a customer object from the gatewayi using the customer_id.
        This optionally accepts a ``gateway_name`` parameter.

    .. method:: save()

        Store the current state of a customer back to the gateway.

    .. method:: delete()

        Delete a customer from the gateway.

    .. rubric:: Card Management

    .. attribute:: cards

        Contains a list of all the cards associated with a customer.  This is
        populated by :meth:`create` and :meth:`retrieve` and appended to by
        :meth:`add_card`.

    .. method:: add_card(card_options)

        The first credit card is added when you call :meth:`create`, but you
        can add more cards using this method. ::

            customer.add_card({
                'number': '4222222222222',
                'cvv': '900',
                'month': '12'
                'year': '2015'
                'address': '123 Elm St',
                'zip': '12345',
            })

.. class:: dinero.CreditCard

    A class for storing and managing credit card numbers for a customer in the
    gateway.

    This class doesn't have a create method because the cards need to be
    associated with a customer.  Use :class:`Customer.add_card` to create a new
    :class:`CreditCard`.

    .. attribute:: customer_id

        The gateway ID of the customer that owns this credit card.

    .. attribute:: card_id

        The gateway ID of this card.

    .. attribute:: last_4

        The last four numbers of the credit card.  This is useful in a
        situation where you are storing more than one card.

    .. method:: save()

        Save changes to a card to the gateway.

    .. method:: delete()

        Delete a card from the gateway.
