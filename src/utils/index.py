from datetime import datetime, timezone

def default_datetime():
    return datetime.now().astimezone(timezone.utc)

def transaction_to_payload(transaction, sender, receiver):
    transaction["_id"] = str(transaction["_id"])
    result = {
        "_id": transaction["_id"],
        "value": transaction["value"],
        "currency": transaction["currency"],
        "date": transaction["created_at"],
        "to": {
            "id": receiver["_id"],
            "name": receiver.get("name"),
            "cpf": receiver.get("cpf"),
            "institution": receiver.get("institution"),
            "agency": receiver.get("agency"),
            "account": receiver.get("account"),
        },
        "from":{
            "id": sender["_id"],
            "name": sender.get("name"),
            "cpf": sender.get("cpf"),
            "institution": sender.get("institution"),
            "agency": sender.get("agency"),
            "account": sender.get("account"),
        }
    }
    return result