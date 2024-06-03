from marshmallow import Schema, fields, validate


class PixKeySchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(["cpf", "telefone", "email", "aleatoria"]))
    
    key = fields.Str(required=False)

    user_id = fields.Str(required=True, error_messages={"required": "O usuário é obrigatório"})

class TransactionSchema(Schema):
    sender_id = fields.Str(required=True, error_messages={"required": "O usuário é obrigatório"})
    receiver_key = fields.Str(required=True, error_messages={"required": "O receptor é obrigatório"})
    currency = fields.Str(required=True, error_messages={"required": "A moeda é obrigatória"})
    # values = fields.