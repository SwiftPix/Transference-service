import uuid
from database.models import PixKey
from utils.exceptions import KeyAlreadyExistsException, KeyNotFound

class TransferenceController:
    @staticmethod
    def create_key(key):
        type = key.get("type")
        pix_key = key.get("key")

        keys = PixKey.find()

        if type == "aleatoria":
            key["key"] = uuid.uuid4()

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
        return keys
    
    @staticmethod
    def get_key(key_id):
        key = PixKey.find_by_id(key_id)

        if not key:
            raise KeyNotFound("Chave não encontrada")
        return key
