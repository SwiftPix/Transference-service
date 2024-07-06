payload_create_key = {
    "type": "telefone",
    "key": "11999888156", 
    "user_id": "665e0069183ce834954a2f44"
}

payload_transaction = {
    "sender_id": "665dff9c183ce834954a2f42",
    "receiver_key": "11999888156",
    "currency": "BRL",
    "value": 15.0
}

payload_transaction_other_currency = {
    "sender_id": "665dff9c183ce834954a2f42",
    "receiver_key": "11999888156",
    "currency": "USD",
    "value": 15.0
}

response_transaction = {
    "currency": "BRL",
    "date": "Mon, 01 Jan 2024 03:00:00 GMT",
    "from": {
        "account": "000",
        "agency": "0001",
        "cpf": "284.438.920-13",
        "id": "665dff9c183ce834954a2f42",
        "institution": "001",
        "name": "Teste1"
    },
    "to": {
        "account": "000",
        "agency": "0001",
        "cpf": "785.188.920-07",
        "id": "665e0069183ce834954a2f44",
        "institution": "001",
        "name": "Teste2"
    },
    "value": 15.0
}

response_get_key = {
    "result": [
        {
            "created_at": "Mon, 01 Jan 2024 03:00:00 GMT",
            "key": "11999888156",
            "type": "telefone",
            "updated_at": "Mon, 01 Jan 2024 03:00:00 GMT",
            "user_id": "665e0069183ce834954a2f44"
        }
    ]
}
