import unittest

import dinero
from dinero.configure import (
    _configured_gateways, get_default_gateway, get_gateway
)


class ConfigureTest(unittest.TestCase):
    def setUp(self):
        self._gateways = _configured_gateways.copy()
        _configured_gateways.clear()

    def tearDown(self):
        _configured_gateways.clear()
        _configured_gateways.update(self._gateways)

    def test_get_default_gateway(self):
        dinero.configure({
            'a': {
                'type': 'dinero.gateways.authorizenet.Gateway',
                'login_id': 'XXX',
                'transaction_key': 'XXX',
            },
            'b': {
                'type': 'dinero.gateways.authorizenet.Gateway',
                'login_id': 'XXX',
                'transaction_key': 'XXX',
                'default': True,
            },
        })
        b = get_gateway('b')
        self.assertEqual(get_default_gateway(), b)

        dinero.configure({
            'c': {
                'type': 'dinero.gateways.authorizenet.Gateway',
                'login_id': 'XXX',
                'transaction_key': 'XXX',
                'default': True,
            }
        })
        self.assertEqual(get_default_gateway(), get_gateway('c'))

        self.assertFalse(b.default)

    def test_backwards_compatibility_import_paths(self):
        dinero.configure({
            'a': {
                'type': 'dinero.gateways.AuthorizeNet',
                'login_id': 'XXX',
                'transaction_key': 'XXX',
            },
        })
