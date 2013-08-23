docs:
	cd docs && $(MAKE) html

coverage:
	coverage run --source=dinero setup.py test
	coverage html --omit='dinero/gateways/braintree*,dinero/ordereddict*'


.PHONY: docs coverage
