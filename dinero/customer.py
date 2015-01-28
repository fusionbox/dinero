from dinero import get_gateway
from dinero.exceptions import InvalidCustomerException
from dinero.log import log
from dinero.card import CreditCard
from dinero.base import DineroObject


class Customer(DineroObject):
    """
    A Customer object stores information about your customers.
    """

    @classmethod
    @log
    def create(cls, gateway_name=None, **kwargs):
        """
        Creates and stores a customer object.  When you first create a
        customer, you are required to also pass in arguments for a credit card.

            Customer.create(
                email='bill@example.com',

                # required for credit card
                number='4111111111111111',
                cvv='900',
                month='12',
                year='2015',
                address='123 Elm St.',
                zip='12345',
            )

        This method also accepts `gateway_name`.
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

    def __init__(self, gateway_name, customer_id, **kwargs):
        self.gateway_name = gateway_name
        self.customer_id = customer_id
        self.data = kwargs
        self.data['cards'] = []

    def update(self, options):
        for key, value in options.iteritems():
            setattr(self, key, value)

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
    def add_card(self, gateway_name=None, **options):
        """
        The first credit card is added when you call create, but you can add
        more cards using this method.

            customer.add_card(
                number='4222222222222',
                cvv='900',
                month='12'
                year='2015'
                address='123 Elm St',
                zip='12345',
            )
        """
        if not self.customer_id:
            raise InvalidCustomerException("Cannot add a card to a customer that doesn't have a customer_id")
        gateway = get_gateway(gateway_name)
        resp = gateway.add_card_to_customer(self, options)
        card = CreditCard(gateway_name=self.gateway_name, **resp)
        self.cards.append(card)
        return card

    def __setattr__(self, attr, val):
        if attr in ['gateway_name', 'customer_id', 'data']:
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
        return "Customer({gateway_name!r}, {customer_id!r}, **{data!r})".format(**self.to_dict())
