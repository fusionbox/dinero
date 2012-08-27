from dinero.log import log
from dinero import get_gateway

class CreditCard(object):
    """
    A Customer resource. `Customer.create` uses the gateway to create a
    customer.  You can use this Customer object in calls to
    `Transaction.create`.
    """

    def __init__(self, gateway_name, customer_id, **kwargs):
        self.gateway_name = gateway_name
        self.customer_id = customer_id
        self.data = kwargs
    @log
    def save(self):
        raise NotImplemented

    @log
    def delete(self, ):
        gateway = get_gateway(self.gateway_name)
        gateway.delete_card(self)
        return True

    def to_dict(self):
        return vars(self)

    def __getattr__(self, attr):
        try:
            return self.data[attr]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, attr, val):
        if attr in ['customer_id', 'data', 'gateway_name']:
            self.__dict__[attr] = val
        else:
            self.data[attr] = val

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['gateway_name'],
                   dict['customer_id'],
                   **dict['data']
                   )

    def __repr__(self):
        return "CreditCard(({customer_id!r}, **{data!r})".format(**self.to_dict())
