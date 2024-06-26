from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from database.models import PixKey, Transaction
from utils.exceptions import (BalanceInsuficient, BalanceNotFound, ConversionNotFound, 
                              GeoLocServiceError, KeyAlreadyExistsException, KeyNotFound, 
                              TaxNotFound, TransactionNotFound, UserNotFound, UserServiceError)
from settings import settings
from utils.index import transaction_to_payload

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  

headers = {
    "Content-Type": "application/json"
}

@app.route('/create_key', methods=['POST'])
def create_key():
    key = request.json
    type = key.get("type")
    pix_key = key.get("key")

    keys = PixKey.find()

    if type == "aleatoria":
        key["key"] = str(uuid.uuid4())

    for existent_key in keys:
        if existent_key.get("type") == type and existent_key.get("key") == pix_key:
            return jsonify({"error": "Chave já está em uso"}), 400

    new_key = PixKey(
        type=type,
        key=key.get("key"),
        user_id=key.get("user_id")
    )

    key_id = new_key.save()

    return jsonify({"key_id": key_id})

@app.route('/get_user_keys/<user_id>', methods=['GET'])
def get_user_keys(user_id):
    keys = PixKey.find_by_user_id(user_id)
    if not keys:
        return jsonify({"error": "Chave não encontrada"}), 404
    keys = list(keys)
    for key in keys:
        key["_id"] = str(key["_id"])
    return jsonify(keys)

@app.route('/get_key_by_id/<key_id>', methods=['GET'])
def get_key_by_id(key_id):
    key = PixKey.find_by_id(key_id)
    if not key:
        return jsonify({"error": "Chave não encontrada"}), 404
    key["_id"] = str(key["_id"])
    return jsonify(key)

@app.route('/get_user_by_key', methods=['POST'])
def get_user_by_key():
    key = request.json.get("key")
    user = PixKey.find_by_key(key)
    if not user:
        return jsonify({"error": f"Usuário não encontrado para chave {key}"}), 404
    user["_id"] = str(user["_id"])
    return jsonify(user)

@app.route('/transaction', methods=['POST'])
def transaction():
    transference = request.json
    receiver_user_key = transference.get("receiver_key")
    sender_id = transference.get("sender_id")
    sended_value = transference.get("value")
    transference_currency = transference.get("currency")

    try:
        receiver_user = TransferenceController.get_user_by_key(receiver_user_key)
        receiver_user_id = receiver_user.get("user_id")
        receiver_user_balance = TransferenceController.get_user_balance(receiver_user_id)
        sender_user_balance = TransferenceController.get_user_balance(sender_id)

        receiver_user_currency = receiver_user_balance["currency"]
        sender_user_currency = sender_user_balance["currency"]

        if receiver_user_currency == sender_user_currency and transference_currency == sender_user_currency:
            sended_value_to_receiver = sended_value
            sended_value_to_sender = sended_value
        elif receiver_user_currency == sender_user_currency and transference_currency != sender_user_currency:
            conversion = TransferenceController.get_conversion(transference_currency, sender_user_currency, sended_value)
            sended_value_to_receiver = conversion["result"]
            sended_value_to_sender = conversion["result"]
        elif transference_currency == receiver_user_currency:
            conversion = TransferenceController.get_conversion(transference_currency, sender_user_currency, sended_value)
            sended_value_to_receiver = sended_value
            sended_value_to_sender = conversion["result"]

        new_sender_user_balance = sender_user_balance["balance"] - sended_value_to_sender

        if new_sender_user_balance < 0:
            raise BalanceInsuficient("Usuário não possui saldo suficiente")

        new_receiver_balance = receiver_user_balance["balance"] + sended_value_to_receiver

        TransferenceController.updated_balance(receiver_user_id, new_receiver_balance)
        TransferenceController.updated_balance(sender_id, new_sender_user_balance)

        receiver_user = TransferenceController.get_user_by_id(receiver_user_id)
        sender_user = TransferenceController.get_user_by_id(sender_id)

        new_transaction = Transaction(
            user_id=sender_id,
            receiver_key=receiver_user_key,
            sender=sender_user.get("name"),
            currency=transference_currency,
            value=sended_value,
            type="sended"
        )

        new_transaction_to_receiver = Transaction(
            user_id=receiver_user_id,
            receiver_key=receiver_user_key,
            sender=sender_user.get("name"),
            currency=transference_currency,
            value=sended_value,
            type="received"
        )

        transaction_id = new_transaction.save()
        new_transaction_to_receiver.save()

        transaction = Transaction.find_by_id(transaction_id)
        transaction = transaction_to_payload(transaction, sender_user, receiver_user)

        return jsonify(transaction)

    except UserNotFound as e:
        return jsonify({"error": str(e)}), 404
    except (BalanceInsuficient, BalanceNotFound, ConversionNotFound, GeoLocServiceError, TaxNotFound, TransactionNotFound, UserServiceError) as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get_user_transactions/<user_id>', methods=['GET'])
def get_user_transactions(user_id):
    transactions = Transaction.find_by_user_id(user_id)
    if not transactions:
        return jsonify({"error": "Sem nenhuma transação realizada"}), 404
    transactions = list(transactions)
    for transaction in transactions:
        transaction["_id"] = str(transaction["_id"])
    return jsonify(transactions)

@app.route('/get_transaction_by_id/<transaction_id>', methods=['GET'])
def get_transaction_by_id(transaction_id):
    transaction = Transaction.find_by_id(transaction_id)
    if not transaction:
        return jsonify({"error": "Sem nenhuma transação realizada"}), 404
    transaction["_id"] = str(transaction["_id"])
    return jsonify(transaction)

@app.route('/get_user_balance/<user_id>', methods=['GET'])
def get_user_balance(user_id):
    url = f"{settings.USER_API}/balance/{user_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Serviço de usuário indisponível"}), 503
    response = response.json()
    if not response:
        return jsonify({"error": "Saldo indisponível"}), 404
    return jsonify(response)

@app.route('/updated_balance/<user_id>', methods=['PATCH'])
def updated_balance(user_id):
    balance = request.json.get("balance")
    url = f"{settings.USER_API}/balance/{user_id}"
    payload = {
        "balance": balance
    }
    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Serviço de usuário indisponível"}), 503
    response = response.json()
    if not response:
        return jsonify({"error": "Saldo indisponível"}), 404
    return jsonify(response)

@app.route('/get_user_by_id/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    url = f"{settings.USER_API}/user/{user_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Serviço de usuário indisponível"}), 503
    response = response.json()
    if not response:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(response)

@app.route('/get_tax', methods=['POST'])
def get_tax():
    latitude = request.json.get("latitude")
    longitude = request.json.get("longitude")
    sender_currency = request.json.get("sender_currency")
    url = f"{settings.GEOLOC_API}/tax_coords"
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "sender_currency": sender_currency
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Serviço de geolocalização indisponível"}), 503
    response = response.json()
    if not response:
        return jsonify({"error": "Taxa de conversão não encontrada"}), 404
    return jsonify(response)

@app.route('/get_conversion', methods=['POST'])
def get_conversion():
    sender_currency = request.json.get("sender_currency")
    receiver_currency = request.json.get("receiver_currency")
    value = request.json.get("value")
    url = f"{settings.GEOLOC_API}/conversion"
    payload = {
        "sender_currency": sender_currency,
        "receiver_currency": receiver_currency,
        "value": value
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Serviço de geolocalização indisponível"}), 503
    response = response.json()
    if not response:
        return jsonify({"error": "Conversão não encontrada"}), 404
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
