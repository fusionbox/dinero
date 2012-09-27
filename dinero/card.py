from dinero.log import log
from dinero.base import DineroObject

class CreditCard(DineroObject):
    """
    A Customer resource. `Customer.create` uses the gateway to create a
    customer.  You can use this Customer object in calls to
    `Transaction.create`.
    """

    def __init__(self, customer_id, **kwargs):
        self.customer_id = customer_id
        self.data = kwargs

    @log
    def save(self):
        raise NotImplemented

    @log
    def delete(self):
        raise NotImplemented

    def __setattr__(self, attr, val):
        if attr in ['customer_id', 'data']:
            self.__dict__[attr] = val
        else:
            self.data[attr] = val

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['customer_id'],
                   **dict['data']
                   )

    def __repr__(self):
        return "CreditCard(({customer_id!r}, **{data!r})".format(**self.to_dict())
