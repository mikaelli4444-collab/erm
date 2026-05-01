import mercadopago

sdk = mercadopago.SDK("TEST-3803429070564960-043020-684e1b988c9c9198df8e1979cec7297d-1253879127")

request_options = mercadopago.config.RequestOptions()
request_options.custom_headers = {
    'x-idempotency-key': '<SOME_UNIQUE_VALUE>'
}

payment_data = {
    "transaction_amount": 100,
    "token": "123123",
    "description": "Payment description",
    "payment_method_id": 'visa',
    "installments": 1,
    "payer": {
        "email": 'test_user_123456@testuser.com'
    }
}
result = sdk.payment().create(payment_data, request_options)
payment = result["response"]

print(payment)