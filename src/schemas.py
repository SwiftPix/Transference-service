from marshmallow import Schema, fields, validate


class PixKeySchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(["cpf", "telefone", "email", "aleatoria"]))
    key = fields.Str(required=False)
    user_id = fields.Str(required=True, error_messages={"required": "O usuário é obrigatório"})

class TransactionSchema(Schema):
    sender_id = fields.Str(required=True, error_messages={"required": "O usuário é obrigatório"})
    receiver_key = fields.Str(required=True, error_messages={"required": "O receptor é obrigatório"})
    currency = fields.Str(required=True, error_messages={"required": "A moeda desejada é obrigatória"})
    value = fields.Float(required=True, error_messages={"required": "O valor a ser transferido é obrigatório"})

class ConvertBalanceSchema(Schema):
    currency = fields.Str(required=True, error_messages={"required": "A moeda é obrigatória"})
    wanted_currency = fields.Str(required=True, error_messages={"required": "A moeda para conversão é obrigatória"})
    value = fields.Float(required=True, error_messages={"required": "O valor a ser convertido é obrigatório"})