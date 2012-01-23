# dinero
Gateway-agnostic payment processing library for Python.

This library aims to be a minimal, pythonic, and highly usable payment
processing library.  It has a simple API and it hides the differences between
payment processors from the user.

## USAGE
The API for `dinero` is simple to use.

### Configuration
`dinero` allows for more than one payment gateway configuration.

```python
import dinero

dinero.configure({
    'default': { # the default gateway
        'type': 'dinero.gateways.AuthorizeNet' # the gateway path
        # ... gateway-specific configuration
    }})
```

For Django projects, just include this in your `settings.py`.

### Transaction Objects
The following code will charge a customer's credit card.

```python
transaction = dinero.Transaction.create(
    price=2000,
    number='4111111111111111',
    month='12',
    year='2012',
    )
```

`price`, `number`, `month`, and `year` are the only required arguments,
additional optional arguments are

- first_name
- last_name
- zip
- address
- city
- state
- cvv

`dinero.Transaction.create` returns a Transaction object.

Transaction objects contain data about the payment.  Every transaction object
has a `transaction_id` and a `price`.  Additionally, transaction objects have a
`to_dict` method which returns a dictionary of data which can be passed to
`Transaction.from_dict` to restore the Transaction object.  This is useful for
caching the transaction data.

After creating a payment, you can retrieve it using
`dinero.Transaction.retrieve`.

```python
transaction = dinero.Transaction.retrieve(
    transaction_id = '1234567'
    )
```

`dinero.Transaction.retrieve` also returns a Transaction object.

Finally, in order to refund or cancel a payment, there is a `refund` method on
Transaction objects.

```python
transaction.refund()
```
