from dinero.log import log
from dinero import get_gateway
from dinero.base import DineroObject


class CreditCard(DineroObject):

    def __init__(self, gateway_name, customer_id, **kwargs):
        self.gateway_name = gateway_name
        self.customer_id = customer_id
        self.data = kwargs

    @log
    def save(self):
        gateway = get_gateway(self.gateway_name)
        gateway.update_card(self)

    @log
    def delete(self):
        gateway = get_gateway(self.gateway_name)
        gateway.delete_card(self)
        return True

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
