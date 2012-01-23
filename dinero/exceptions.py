class DineroException(Exception):
    pass

class PaymentException(DineroException):
    pass

class GatewayException(DineroException):
    pass
