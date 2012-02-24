class Gateway(object):
    """
    Implemented payment gateways should implement this interface.
    """

    def charge(self, price, options):
        raise NotImplementedError

    def void(self, transaction):
        raise NotImplementedError

    def refund(self, transaction, amount):
        raise NotImplementedError

    def retrieve(self, transaction_id):
        raise NotImplementedError

    def create_customer(self):
        raise NotImplementedError

    def update_customer(self, customer_id):
        raise NotImplementedError

    def delete_customer(self, customer_id):
        raise NotImplementedError
