import functools
import logging
import re
import time

from dinero import gateways, exceptions

logger = logging.getLogger('dinero.Transaction')


def args_kwargs_to_call(args, kwargs):
    ret = []
    for arg in args:
        if ret:
            ret.append(", ")
        ret.append(repr(arg))
    for k, v in kwargs.iteritems():
        if ret:
            ret.append(", ")
        ret.append("%s=%r" % (k, v))
    return ''.join(ret)


def log(fn):
    """
    Wraps fn in logging calls
    """
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        start_time = time.time()

        def logit(exception=None):
            if exception:
                exception_message = ' and raised %r' % exception
            else:
                exception_message = ''

            end_time = time.time()
            message = '%s(%s) took %s seconds%s' % (
                    fn.__name__,
                    args_kwargs_to_call(args, kwargs),
                    end_time - start_time,
                    exception_message)
            # remove any credit card numbers
            message = re.sub(r"\b([0-9])[0-9- ]{9,16}([0-9]{4})\b", r'\1XXXXXXXXX\2', message)
            logger.info(message)

        try:
            value = fn(*args, **kwargs)
            logit()
            return value
        except Exception as e:
            logit(e)
            raise

    return inner


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
        'default': { # the default gateway
            'type': 'dinero.gateways.AuthorizeNet' # the gateway path
            # ... gateway-specific configuration
        }})

    `settings.py` is a great place to put this call in a Django project.
    """
    for name, conf in options.iteritems():
        _configured_gateways[name] = fancy_import(conf['type'])(conf)


def get_gateway(gateway_name='default'):
    """
    Returns a configured gateway.  If no gateway name is provided, it defaults
    to the name 'default'.
    """
    return _configured_gateways[gateway_name]


class Transaction(object):
    """
    A Transaction resource. `Transaction.create` uses the gateway to charge a
    card, and returns an object for future manipulations of the transaction,
    like refunding it.
    """

    @classmethod
    @log
    def create(cls, price, gateway_name='default', **kwargs):
        gateway = get_gateway(gateway_name)
        resp = gateway.charge(price, kwargs)
        return cls(gateway_name=gateway_name, **resp)

    @classmethod
    @log
    def retrieve(cls, transaction_id, gateway_name='default'):
        gateway = get_gateway(gateway_name)
        resp = gateway.retrieve(transaction_id)
        return cls(gateway_name=gateway_name, **resp)

    def __init__(self, gateway_name, price, transaction_id, **kwargs):
        self.gateway_name = gateway_name
        self.price = price
        self.transaction_id = transaction_id
        self.data = kwargs

    @log
    def refund(self, amount=None):
        gateway = get_gateway(self.gateway_name)

        try:
            return gateway.refund(self, amount or self.price)
        except exceptions.PaymentException as e:
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
