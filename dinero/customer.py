from dinero import get_gateway
from dinero.exceptions import InvalidCustomerException
from dinero.log import log
from dinero.card import CreditCard
from dinero.base import DineroObject


class Customer(DineroObject):
    """
    A Customer object stores information about your customers.
    """

    def __init__(self, gateway_name, customer_id, **kwargs):
        self.gateway_name = gateway_name
        self.customer_id = customer_id
        self.data = kwargs
        self.data['cards'] = []

    def __setattr__(self, attr, val):
        if attr in ['gateway_name', 'customer_id', 'data']:
            self.__dict__[attr] = val
        else:
            self.data[attr] = val

    def __repr__(self):
        return "Customer({gateway_name!r}, {customer_id!r}, **{data!r})".format(**self.to_dict())

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['gateway_name'],
                   dict['customer_id'],
                   **dict['data']
                   )

    def update(self, options):
        for key, value in options.iteritems():
            setattr(self, key, value)

    @classmethod
    @log
    def create(cls, gateway_name=None, **kwargs):
        """
        Creates a customer.  You are required to include payment information
        when you create a customer.
        """
        gateway = get_gateway(gateway_name)
        resp = gateway.create_customer(kwargs)
        return cls(gateway_name=gateway.name, **resp)

    @classmethod
    @log
    def retrieve(cls, customer_id, gateway_name=None):
        """
        Fetches a customer object from the gateway.
        """
        gateway = get_gateway(gateway_name)
        resp, cards = gateway.retrieve_customer(customer_id)
        # resp must have customer_id in it
        customer = cls(gateway_name=gateway.name, **resp)
        for card in cards:
            customer.cards.append(CreditCard(
                gateway_name=gateway.name,
                **card
                ))
        return customer

    @log
    def save(self):
        """
        Saves changes to a customer object.
        """
        if not self.customer_id:
            raise InvalidCustomerException("Cannot save a customer that doesn't have a customer_id")
        gateway = get_gateway(self.gateway_name)
        gateway.update_customer(self.customer_id, self.data)
        return True

    @log
    def delete(self):
        """
        Deletes a customer object from the gateway.
        """
        if not self.customer_id:
            raise InvalidCustomerException("Cannot delete a customer that doesn't have a customer_id")
        gateway = get_gateway(self.gateway_name)
        gateway.delete_customer(self.customer_id)
        self.customer_id = None
        return True

    @log
    def add_card(self, options, gateway_name=None):
        """
        Interface for storing a CreditCard.
        """
        if not self.customer_id:
            raise InvalidCustomerException("Cannot add a card to a customer that doesn't have a customer_id")
        gateway = get_gateway(gateway_name)
        resp = gateway.add_card_to_customer(self, options)
        card = CreditCard(gateway_name=self.gateway_name, **resp)
        self.cards.append(card)
        return card
