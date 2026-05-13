from core.config import MERCADO_PAGO_ACCESS_TOKEN
import mercadopago

sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)
def prueba_pago():
    preference_data = {
        "items": [
            {
                "title": "Test Item",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 10.00
            }
        ],
        "back_urls": {
            "success": "https://ooze-crave-yam.ngrok-free.dev/payment/success",
            "failure": "https://ooze-crave-yam.ngrok-free.dev/payment/failure",
            "pending": "https://ooze-crave-yam.ngrok-free.dev/payment/pending"
        },
        "auto_return": "approved"
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        print("Preference created successfully:", preference_response)
        return preference_response
    
    except Exception as e:
        raise Exception("Error creating preference:", e)
        