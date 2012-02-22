from dinero import exceptions, get_gateway


class Transaction(object):
    """
    A Transaction resource. `Transaction.create` uses the gateway to charge a
    card, and returns an object for future manipulations of the transaction,
    like refunding it.
    """

    @classmethod
    def create(cls, price, gateway_name=None, **kwargs):
        gateway = get_gateway(gateway_name)
        resp = gateway.charge(price, kwargs)
        return cls(gateway_name=gateway.name, **resp)

    @classmethod
    def retrieve(cls, transaction_id, gateway_name=None):
        gateway = get_gateway(gateway_name)
        resp = gateway.retrieve(transaction_id)
        return cls(gateway_name=gateway.name, **resp)

    def __init__(self, gateway_name, price, transaction_id, **kwargs):
        self.gateway_name = gateway_name
        self.price = price
        self.transaction_id = transaction_id
        self.data = kwargs

    def refund(self, amount=None):
        gateway = get_gateway(self.gateway_name)

        try:
            return gateway.refund(self, amount or self.price)
        except exceptions.PaymentException:
            if amount is None or amount == self.price:
                return gateway.void(self)
            else:
                raise exceptions.PaymentException("You cannot refund a "
                        "transaction that hasn't been settled unless you "
                        "refund it for the full amount.")

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['gateway_name'],
                   dict['price'],
                   dict['transaction_id'],
                   **dict['data']
                   )

    def __repr__(self):
        return "Transaction({gateway_name!r}, {price!r}, {transaction_id!r}, **{data!r})".format(**self.to_dict())
