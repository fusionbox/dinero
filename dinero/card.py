from dinero.log import log
from dinero.base import DineroObject


class CreditCard(DineroObject):
    """
    A representation of a credit card to be stored in the gateway.
    """
    required_attributes = ['customer_id', 'card_id']

    def __repr__(self):
        return "CreditCard(({customer_id!r}, **{data!r})".format(**self.to_dict())

    def __eq__(self, other):
        return isinstance(other, CreditCard) and other.card_id == self.card_id

    @log
    def save(self):
        """
        Save changes to a card to the gateway.
        """
        self.gateway.update_card(self)

    @log
    def delete(self):
        """
        Delete a card from the gateway.
        """
        self.gateway.delete_card(self)
