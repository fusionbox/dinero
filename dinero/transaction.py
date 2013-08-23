from dinero import exceptions, get_gateway
from dinero.log import log
from dinero.base import DineroObject


class Transaction(DineroObject):
    """
    Transaction is an abstraction over payments in a gateway.  This is the
    interface for creating and dealing with payments.  It interacts with the
    Gateway backend.
    """
    required_attributes = ['transaction_id', 'price']

    def __repr__(self):
        return "Transaction({gateway_name!r}, {price!r}, {transaction_id!r}, **{data!r})".format(**self.to_dict())

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self.transaction_id == other.transaction_id

    @classmethod
    @log
    def create(cls, price, gateway_name=None, **kwargs):
        """
        This method will charge your customer.  You can pass in credit card
        information, a customer, or a card.
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

    @log
    def refund(self, amount=None):
        """
        Refund will either void a transaction or refund it depending on whether
        or not it has been settled.
        """
        # TODO: can this implementation live in dinero.gateways.authorizenet.Gateway?
        try:
            return self.gateway.refund(self, amount or self.price)
        except exceptions.PaymentException:
            if amount is None or amount == self.price:
                return self.gateway.void(self)
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
        amount is None, the full transaction price is settled.
        """
        return self.gateway.settle(self, amount or self.price)
