Customers
---------

.. currentmodule:: dinero

Payment gateways allow you to store information about your customers.  They let
you store credit cards securely so that you can remember cards without actually
storing the sensitive information on your server.  If your database is
compromised you won't leak all of your customers' information.

We have two classes that you can use to manage your customers' data.

Customers
=========

The :class:`Customer` class provides an interface quite similar to
:class:`Transaction`.  To create a customer, you use :meth:`Customer.create`::

    >>> customer = Customer.create(
            email='bill@example.com',
            number='4111111111111111',
            cvv='900',
            address='123 Elm St',
            zip='12345',
        )
    >>> customer.customer_id
    '1234567890'
    >>> customer.card_id
    '0000101010'

.. note::

    Are the credit card fields required when creating a Customer?  Dinero
    doesn't really require it, but Authorize.Net seems to require you put
    either a credit card or a bank account (see page 14 of Authorize.Net's `CIM
    XML Guide`_).

.. _CIM XML Guide: http://www.authorize.net/support/CIM_XML_guide.pdf

Similarly, you can also retrieve customers.  However, whereas transactions are
not really editable, if you want to update a customer's information you can.
Just call the :meth:`Customer.save` method when you have made your changes.

    >>> customer = Customer.retrieve('1234567890')
    >>> customer.email = 'fred@example.com'
    >>> customer.save()

You wouldn't really have a use for storing a customer's payment data if you
weren't actually going to use it.  If you want to charge a customer,
:meth:`Transaction.create` accepts a :class:`Customer` object::

    customer = Customer.retrieve('1234567890')

    transaction = Transaction.create(
        price=200,
        customer=customer,
    )

Credit Cards
============

Every :class:`Customer` also has list of credit cards that can be accessed at
``customer.cards``.

When you create your Customer, it will create the first card::


    >>> customer = Customer.create(
            email='bill@example.com',
            number='4111111111111111',
            cvv='900',
            address='123 Elm St',
            zip='12345',
        )
    >>> card = customer.cards[0]
    >>> card.last_4
    '1111'

If you have a secondary card, you can add it using :meth:`Customer.add_card`. ::

    customer.add_card({
        'first_name': 'John',
        'last_name': 'Smith',
        'number': '4222222222222',
        'cvv': '900',
        'address': '123 Elm St',
        'zip': '12345',
    })

The :class:`CreditCard` class is editable like :class:`Customer`::

    card.first_name = 'Fred'
    card.save()

.. note::
    When you create a :class:`CreditCard`, it will be validated.  This is quite
    useful if you are going to store a credit card and charge it later when you
    don't have access to the user to fix the information.

    ``address`` and ``zip`` are required by Visa when doing a Zero-Dollar
    Authorization.  This is a special process for validating that a card is
    real without actually charging money to it.  For other credit card types,
    1¢ is usually charged and immediately voided when validating a credit card.

    When you are testing your payments application, you may need to input
    credit cards that validate.  Here is a list of `test credit card numbers`_.

.. _test credit card numbers: http://www.paypalobjects.com/en_US/vhelp/paypalmanager_help/credit_card_numbers.htm
