from flask import Blueprint

bp = Blueprint("transference", __name__)

@bp.route("/health", methods=["GET"])
def health_check():
    return {"status":"ok", "message":"Service is healthy"}