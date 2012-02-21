from dinero import gateways, exceptions


def fancy_import(name):
    """
    This takes a fully qualified object name, like
    'dinero.gateways.AuthorizeNet', and turns it into the
    dinero.gateways.AuthorizeNet object.
    """

    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


_configured_gateways = {}


def configure(options):
    """
    Takes a dictionary of name -> gateway configuration pairs.
    configure({
        'auth.net': { # the name for this gateway
            'default': True, # register as the default gateway
            'type': 'dinero.gateways.AuthorizeNet' # the gateway path
            # ... gateway-specific configuration
        }})

    `settings.py` is a great place to put this call in a Django project.
    """
    for name, conf in options.iteritems():
        _configured_gateways[name] = fancy_import(conf['type'])(conf)


def get_gateway(gateway_name=None):
    """
    Returns a configured gateway.  If no gateway name is provided, it returns
    the config marked as 'default'.
    """
    if gateway_name is None:
        return get_default_gateway()
    return _configured_gateways[gateway_name]


def get_default_gateway():
    """
    Returns the default gateway name.  If no gateway is found, a KeyError is thrown.

    Why KeyError?  That is the same error that would be thrown if _configured_gateways
    was accessed with a gateway name that doesn't exist.
    """
    for name, conf in _configured_gateways.iteritems():
        if 'default' in conf and conf['default']:
            return conf
    raise KeyError("Could not find a gateway configuration that is assigned as 'default'")


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
        return cls(gateway_name=gateway_name, **resp)

    @classmethod
    def retrieve(cls, transaction_id, gateway_name=None):
        gateway = get_gateway(gateway_name)
        resp = gateway.retrieve(transaction_id)
        return cls(gateway_name=gateway_name, **resp)

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
