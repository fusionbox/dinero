from dinero import exceptions, get_gateway
from dinero.log import log
from dinero.base import DineroObject


class Transaction(DineroObject):
    """
    Transaction is an abstraction over payments in a gateway.  This is the
    interface for creating and dealing with payments.  It interacts with the
    Gateway backend.
    """

    @classmethod
    @log
    def create(cls, price, gateway_name=None, **kwargs):
        """
        Creates a payment.  This method will actually charge your customer.
        This method can be called in several different ways.

        You can call this with the credit card information directly.

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

        If you have a Customer object, you can create a transaction against the
        customer.

            customer = Customer.create(
                ...
            )

            Transaction.create(
                price=200,
                customer=customer,
            )

        Other payment options include card and check.  See CreditCard for more
        information.
        """
        gateway = get_gateway(gateway_name)
        resp = gateway.charge(price, kwargs)
        return cls(gateway_name=gateway.name, **resp)

    @classmethod
    @log
    def retrieve(cls, transaction_id, gateway_name=None):
        """
        Fetches a transaction object from the gateway.
        """
        gateway = get_gateway(gateway_name)
        resp = gateway.retrieve(transaction_id)
        return cls(gateway_name=gateway.name, **resp)

    def __init__(self, gateway_name, price, transaction_id, **kwargs):
        self.gateway_name = gateway_name
        self.price = price
        self.transaction_id = transaction_id
        self.data = kwargs

    @log
    def refund(self, amount=None):
        """
        If `amount` is None dinero will refund the full price of the
        transaction.

        Payment gateways often allow you to refund only a certain amount of
        money from a transaction.  Refund abstracts the difference between
        refunding and voiding a payment so that normally you don't need to
        worry about it.  However, please note that you can only refund the
        entire amount of a transaction before it is settled.
        """
        gateway = get_gateway(self.gateway_name)

        # TODO: can this implementation live in dinero.gateways.AuthorizeNet?
        try:
            return gateway.refund(self, amount or self.price)
        except exceptions.PaymentException:
            if amount is None or amount == self.price:
                return gateway.void(self)
            else:
                raise exceptions.PaymentException(
                    "You cannot refund a transaction that hasn't been settled"
                    " unless you refund it for the full amount."
                )

    @log
    def settle(self, amount=None):
        """
        If you create a transaction without settling it, you can settle it with
        this method.  It is possible to settle only part of a transaction.  If
        `amount` is None, the full transaction price is settled.
        """
        gateway = get_gateway(self.gateway_name)
        return gateway.settle(self, amount or self.price)

    def __setattr__(self, attr, val):
        if attr in ['gateway_name', 'transaction_id', 'price', 'data']:
            self.__dict__[attr] = val
        else:
            self.data[attr] = val

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['gateway_name'],
                   dict['price'],
                   dict['transaction_id'],
                   **dict['data']
                   )

    def __repr__(self):
        return "Transaction({gateway_name!r}, {price!r}, {transaction_id!r}, **{data!r})".format(**self.to_dict())

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self.transaction_id == other.transaction_id
