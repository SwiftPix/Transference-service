import pytest
from flask import Flask
from pymongo import MongoClient
from main import create_app
from settings import settings

@pytest.fixture
def app():
    """Fixture para criar uma instância do aplicativo Flask para os testes."""
    app = create_app()

    app.config["TESTING"] = True
    app.config["MONGO_DATABASE_URI"] = settings.MONGO_DATABASE_URI
    app.config["MONGO_DATABASE_NAME"] = settings.MONGO_DATABASE_NAME

    with app.app_context():
        client = MongoClient(app.config["MONGO_DATABASE_URI"])
        db = client[app.config["MONGO_DATABASE_NAME"]]
        db.keys.delete_many({})
        db.transactions.delete_many({})

        yield app

        db.keys.delete_many({})
        db.transactions.delete_many({})
        client.close()


@pytest.fixture
def client(app):
    """Fixture para criar um cliente de teste para o aplicativo Flask."""
    return app.test_client()


@pytest.fixture
def mock_get_key_by_user(mocker):
    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_by_key", return_value="valor_desejado"
    )


@pytest.fixture
def mock_get_user_balance(mocker):
    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_balance", 
        return_value={
            "balance": 25.0,
            "currency": "real"
        }
    )


@pytest.fixture
def mock_updated_balance(mocker):
    mocker.patch(
        "controllers.transference_controller.TransferenceController.updated_balance", return_value="OK"
    )


@pytest.fixture
def mock_get_receiver_user_by_id(mocker):
    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_by_id", 
        return_value={
            "_id": "665e0069183ce834954a2f44",
            "name": "Teste2",
            "cpf": "284.438.920-13",
            "institution": "001",
            "agency": "0001",
            "account": "000"
        }
    )


@pytest.fixture
def mock_get_sender_user_by_id(mocker):
    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_by_id", 
        return_value={
            "_id": "665dff9c183ce834954a2f42",
            "name": "Teste1",
            "cpf": "284.438.920-13",
            "institution": "001",
            "agency": "0001",
            "account": "000"
        }
    )
