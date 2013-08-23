coverage:
	coverage run --source=dinero setup.py test
	coverage html --omit='dinero/gateways/braintree*,dinero/ordereddict*'
	@echo "Please visit file://$(PWD)/htmlcov/index.html in your browser of choice"


.PHONY: coverage
