Customers
---------

Payment gateways allow you to store information about your customers.  They let
you store credit cards securely so that you can remember cards without actually
storing the sensitive information on your server.  If your database is
compromised you won't leak all of your customer's information.


.. currentmodule:: dinero.customer

.. autoclass:: Customer(customer_id, **kwargs)

.. currentmodule:: dinero.card

.. autoclass:: CreditCard(customer_id, card_id, **kwargs)
