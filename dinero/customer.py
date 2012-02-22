from dinero import exceptions, get_gateway


class Customer(object):
    """
    A Customer resource. `Customer.create` uses the gateway to create a
    customer.  You can use this Customer object in calls to
    `Transaction.create`.
    """

    @classmethod
    def create(cls, gateway_name=None, **kwargs):
        gateway = get_gateway(gateway_name)
        resp = gateway.create_customer(kwargs)
        return cls(gateway_name=gateway.name, **resp)

    @classmethod
    def retrieve(cls, customer_id, gateway_name=None):
        gateway = get_gateway(gateway_name)
        resp = gateway.retrieve_customer(customer_id)
        return cls(gateway_name=gateway.name, **resp)

    def __init__(self, gateway_name, customer_id, **kwargs):
        self.gateway_name = gateway_name
        self.customer_id = customer_id
        self.data = kwargs

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['gateway_name'],
                   dict['customer_id'],
                   **dict['data']
                   )

    def __repr__(self):
        return "Customer({gateway_name!r}, {customer_id!r}, **{data!r})".format(**self.to_dict())
