import unittest
import datetime
import uuid

import dinero


class CardTest(unittest.TestCase):
    def setUp(self):
        options = {
            'email': '{0}@example.com'.format(uuid.uuid4()),

            'first_name': 'Joey',
            'last_name': 'Shabadoo',
            'company': 'Shabadoo, Inc.',
            'phone': '000-000-0000',
            'fax': '000-000-0001',
            'address': '123 somewhere st',
            'state': 'SW',
            'city': 'somewhere',
            'zip': '12345',
            'country': 'US',

            'number': '4' + '1' * 15,
            'month': '12',
            'year': str(datetime.date.today().year + 1),
        }
        self.customer = dinero.Customer.create(gateway_name='authorize.net', **options)

    def tearDown(self):
        self.customer.delete()

    def refetch_customer(self):
        return dinero.Customer.retrieve(self.customer.customer_id)

    def test_add_card(self):
        card = self.customer.add_card({
            'number': '4222222222222',
            'month': '12',
            'year': str(datetime.date.today().year + 1),
            'zip': '12345',
            'cvv': '900',
            'first_name': 'Test',
            'last_name': 'Test',
            'address': '123 Elm St',
        })

        customer = self.refetch_customer()

        assert len(customer.cards) == 2
        assert card in customer.cards

    def test_update_card(self):
        customer = self.refetch_customer()
        card = customer.cards[0]
        assert card.last_4 == '1111'
        card.number = '4222222222222'
        card.save()

        customer2 = self.refetch_customer()
        card2 = customer2.cards[0]
        assert card2.last_4 == '2222'

    def test_delete_card(self):
        customer = self.refetch_customer()
        card = customer.cards[0]
        card.delete()

        customer = self.refetch_customer()
        assert len(customer.cards) == 0

    def test_charge_card(self):
        customer = self.refetch_customer()
        card = customer.cards[0]

        transaction = dinero.Transaction.create(
            price='2.00',
            cc=card,
        )
        assert transaction.price == '2.00'
