from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from schemas import PixKeySchema
from controllers.transference_controller import TransferenceController
from utils.exceptions import KeyAlreadyExistsException, KeyNotFound

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
        return keys
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/key/<key_id>", methods=["GET"])
def get_user_keys(key_id):
    try:
        key = TransferenceController.get_key(key_id)
        return key
    except KeyNotFound as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400