import uuid

import requests
from database.models import PixKey, Transaction
from utils.exceptions import BalanceInsuficient, BalanceNotFound, ConversionNotFound, GeoLocServiceError, KeyAlreadyExistsException, KeyNotFound, TaxNotFound, TransactionNotFound, UserNotFound, UserServiceError
from settings import settings
from utils.index import transaction_to_payload

class TransferenceController:
    @staticmethod
    def create_key(key):
        type = key.get("type")
        pix_key = key.get("key")

        keys = PixKey.find()

        if type == "aleatoria":
            key["key"] = str(uuid.uuid4())

        for existent_key in keys:
            if existent_key.get("type") == type and existent_key.get("key") == pix_key:
                raise KeyAlreadyExistsException("Chave já está em uso")

        new_key = PixKey(
            type=type,
            key=key.get("key"),
            user_id=key.get("user_id")
        )

        key_id = new_key.save()

        return key_id

    @staticmethod
    def get_user_keys(user_id):
        keys = PixKey.find_by_user_id(user_id)
        if not keys:
            raise KeyNotFound("Chave não encontrada")
        keys = list(keys)
        for key in keys:
            key["_id"] = str(key["_id"])
        return keys
    
    @staticmethod
    def get_key_by_id(key_id):
        key = PixKey.find_by_id(key_id)

        if not key:
            raise KeyNotFound("Chave não encontrada")
        key["_id"] = str(key["_id"])
        return key
    
    @staticmethod
    def get_user_by_key(key):
        user = PixKey.find_by_key(key)
        if not user:
            raise UserNotFound(f"Usuário não encontrado para chave {key}")
        user["_id"] = str(user["_id"])
        return user
    
    @staticmethod
    def transaction(transference):

        receiver_user_key = transference.get("receiver_key")
        sender_id = transference.get("sender_id")
        sended_value = transference.get("value")
        transference_currency = transference.get("currency")

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
            conversion = TransferenceController.get_conversion(sender_user_currency, transference_currency, sended_value)
            sended_value_to_receiver = conversion["result"]
            sended_value_to_sender = conversion["result"]
        elif transference_currency == receiver_user_currency:
            conversion = TransferenceController.get_conversion(sender_user_currency, transference_currency, sended_value)
            sended_value_to_receiver = sended_value
            sended_value_to_sender = conversion["result"]

        new_sender_user_balance = sender_user_balance["balance"] - sended_value_to_sender

        if new_sender_user_balance < 0:
            raise BalanceInsuficient("Usuário não possui saldo suficiente")

        new_receiver_balance = receiver_user_balance["balance"] + sended_value_to_receiver

        TransferenceController.updated_balance(receiver_user_id, new_receiver_balance)
        TransferenceController.updated_balance(sender_id, new_sender_user_balance)

        new_transaction = Transaction(
            sender_id = sender_id,
            receiver_key = receiver_user_key,
            currency = transference_currency,
            value = sended_value
        )

        transaction_id = new_transaction.save()

        transaction = Transaction.find_by_id(transaction_id)

        receiver_user = TransferenceController.get_user_by_id(receiver_user_id)

        sender_user = TransferenceController.get_user_by_id(sender_id)

        transaction = transaction_to_payload(transaction, sender_user, receiver_user)
        
        return transaction
    
    @staticmethod
    def get_user_transactions(user_id):
        transactions = Transaction.find_by_user_id(user_id)
        transactions = list(transactions)

        if not transactions:
            raise TransactionNotFound("Sem nenhuma transação realizada")
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        return transactions
    
    @staticmethod
    def get_transaction_by_id(transaction_id):
        transaction = Transaction.find_by_id(transaction_id)

        if not transaction:
            raise TransactionNotFound("Sem nenhuma transação realizada")
        transaction["_id"] = str(transaction["_id"])
        return transaction
    
    @staticmethod
    def get_user_balance(user_id):
        url = f"{settings.USER_API}/balance/{user_id}"
        response = requests.get(url)
        if response.status_code != 200:
            raise UserServiceError("Serviço de usuário indisponível")
        response = response.json()
        if not response:
            raise BalanceNotFound("Saldo indisponível")
        return response
    
    @staticmethod
    def updated_balance(user_id, balance):
        url = f"{settings.USER_API}/balance/{user_id}"
        payload = {
            "balance": balance
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.patch(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise UserServiceError("Serviço de usuário indisponível")
        response = response.json()
        if not response:
            raise BalanceNotFound("Saldo indisponível")
        return response
    
    @staticmethod
    def get_user_by_id(user_id):
        url = f"{settings.USER_API}/user/{user_id}"
        response = requests.get(url)
        if response.status_code != 200:
            raise UserServiceError("Serviço de usuário indisponível")
        response = response.json()
        if not response:
            raise UserNotFound("Usuário não encontrado")
        return response
    
    @staticmethod
    def get_tax(latitude, longitude, sender_currency):
        url = f"{settings.GEOLOC_API}/tax_coords"
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "sender_currency": sender_currency
        }
        response = requests.post(url, payload)
        if response.status_code != 200:
            raise GeoLocServiceError("Serviço de geolocalização indisponível")
        response = response.json()
        if not response:
            raise TaxNotFound("Taxa de conversão não encontrada")
        return response
    
    @staticmethod
    def get_conversion(sender_currency, receiver_currency, value):
        url = f"{settings.GEOLOC_API}/conversion"
        payload = {
            "sender_currency": sender_currency,
            "receiver_currency": receiver_currency,
            "value": value
        }
        response = requests.post(url, payload)
        if response.status_code != 200:
            raise GeoLocServiceError("Serviço de geolocalização indisponível")
        response = response.json()
        if not response:
            raise ConversionNotFound("Conversão não encontrada")
        return response