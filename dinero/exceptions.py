class DineroException(Exception):
    pass

class GatewayException(DineroException):
    """
    Exceptions resulting from malformed requests to the gateway.  For example,
    if you do not have the correct login credentials, or if your request has
    malformed data.
    """
    pass

class PaymentException(DineroException):
    """
    This is how errors are reported when submitting a transaction.
    PaymentException has an `errors` property that stores a list of
    `PaymentError` instances, one for each error that occured. The `in`
    operator is overrided to provide a subclass-like interface, so if `a` is an
    instance of `Foo`, `Foo in PaymentException([a])` will be True.
    """

    def __init__(self, errors=None):
        self.errors = errors or []

    def has(self, error):
        return any(isinstance(i, error) for i in self.errors)

    def __contains__(self, key):
        return self.has(key)

    def __repr__(self):
        return "PaymentException(%r)" % (self.errors,)


class PaymentError(DineroException):
    """
    These exceptions are never actually raised, they always belong to a
    PaymentException.
    """
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.args[0])

class VerificationError(PaymentError):
    pass

class CVVError(VerificationError):
    pass

class AVSError(VerificationError):
    pass

class InvalidCardError(PaymentError):
    pass

class InvalidAmountError(PaymentError):
    pass

class ExpiryError(PaymentError):
    pass

class CardDeclinedError(PaymentError):
    pass

class DuplicateTransactionError(PaymentError):
    pass

class RefundError(PaymentError):
    pass

class InvalidTransactionError(PaymentError):
    pass

class RoutingNumberError(PaymentError):
    pass

class RefundTooMuchError(PaymentError):
    "The sum of credits against the referenced transaction would exceed the original debit amount."


##|
##|  CUSTOMER
##|
class CustomerError(DineroException):
    pass


class InvalidCustomerException(CustomerError):
    pass


class DuplicateCustomerError(CustomerError):
    def __init__(self, *args, **kwargs):
        if 'customer_id' in kwargs:
            self.customer_id = kwargs.pop('customer_id')
        else:
            self.customer_id = None
        super(DuplicateCustomerError, self).__init__(*args, **kwargs)


class CustomerNotFoundError(CustomerError):
    pass
