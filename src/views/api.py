from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from schemas import ConvertBalanceSchema, PixKeySchema, TransactionSchema
from controllers.transference_controller import TransferenceController
from utils.exceptions import BalanceInsuficient, BalanceNotFound, KeyAlreadyExistsException, KeyNotFound, TransactionNotFound, UserNotFound, UserServiceError

bp = Blueprint("transference", __name__)

@bp.route("/health", methods=["GET"])
def health_check():
    return {"status":"ok", "message":"Service is healthy"}

@bp.route("/create_key", methods=["POST"])
def create_key():
    try:
        payload = request.get_json()
        validated_key = PixKeySchema().load(payload)
        id = TransferenceController.create_key(validated_key)

        return jsonify({"status": "success", "message": f"Chave criada com sucesso. ID: {id}"})
    except KeyAlreadyExistsException as e:
        return jsonify({"status": 409, "message": str(e)}), 409
    except ValidationError as e:
        return jsonify({"status": 422, "message": str(e)}), 422
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/my_keys/<user_id>", methods=["GET"])
def get_user_keys(user_id):
    try:
        keys = TransferenceController.get_user_keys(user_id)
        return {"result": keys}
    except KeyNotFound as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/key/<key_id>", methods=["GET"])
def get_key_by_id(key_id):
    try:
        key = TransferenceController.get_key_by_id(key_id)
        return key
    except KeyNotFound as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/user_keys/<key>", methods=["GET"])
def get_user_by_key(key):
    try:
        key = TransferenceController.get_user_by_key(key)
        return key
    except UserNotFound as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/transference", methods=["POST"])
def create_transference():
    try:
        payload = request.get_json()
        validated_transference = TransactionSchema().load(payload)
        transaction = TransferenceController.transaction(validated_transference)
        return transaction
    except (UserNotFound, BalanceNotFound) as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except ValidationError as e:
        return jsonify({"status": 422, "message": str(e)}), 422
    except (BalanceInsuficient, UserServiceError, Exception) as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/my_transferences/<user_id>", methods=["GET"])
def get_user_transactions(user_id):
    try:
        transactions = TransferenceController.get_user_transactions(user_id)
        return {"result": transactions}
    except TransactionNotFound as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/transferences/<transaction_id>", methods=["GET"])
def get_transaction_by_id(transaction_id):
    try:
        transaction = TransferenceController.get_transaction_by_id(transaction_id)
        return transaction
    except TransactionNotFound as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400