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
    mock_get_key_by_user = mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_by_key",
        return_value={
            "created_at": "Mon, 01 Jan 2024 03:00:00 GMT",
            "key": "11999888156",
            "type": "telefone",
            "updated_at": "Mon, 01 Jan 2024 03:00:00 GMT",
            "user_id": "665e0069183ce834954a2f44"
        }
    )

    return mock_get_key_by_user


@pytest.fixture
def mock_get_user_balance(mocker):
    mock_get_user_balance = mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_balance", 
        return_value={
            "balance": 100.0,
            "currency": "BRL"
        }
    )

    return mock_get_user_balance


@pytest.fixture
def mock_get_user_insuficient_balance(mocker):
    mock_get_user_insuficient_balance = mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_balance", 
        return_value={
            "balance": 5.0,
            "currency": "BRL"
        }
    )

    return mock_get_user_insuficient_balance


@pytest.fixture
def mock_updated_balance(mocker):
    mock_updated_balance = mocker.patch(
        "controllers.transference_controller.TransferenceController.updated_balance", return_value="OK"
    )

    return mock_updated_balance


@pytest.fixture
def mock_get_user_by_id(mocker):
    mock_get_user_by_id = mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_by_id",
        side_effect=[
            {
                "_id": "665e0069183ce834954a2f44",
                "name": "Teste2",
                "cpf": "785.188.920-07",
                "institution": "001",
                "agency": "0001",
                "account": "000",
                "currency": "BRL",
                "balance": 100.0,
                "cellphone": "11999888156"
            },
            {
                "_id": "665dff9c183ce834954a2f42",
                "name": "Teste1",
                "cpf": "284.438.920-13",
                "institution": "001",
                "agency": "0001",
                "account": "000",
                "currency": "BRL",
                "balance": 100.0,
                "cellphone": "11999888155"
            }
        ]
    )

    return mock_get_user_by_id


@pytest.fixture
def mock_get_user_by_id_different_currencies(mocker):
    mock_get_user_by_id_different_currencies = mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_by_id",
        side_effect=[
            {
                "_id": "665e0069183ce834954a2f44",
                "name": "Teste2",
                "cpf": "785.188.920-07",
                "institution": "001",
                "agency": "0001",
                "account": "000",
                "currency": "USD",
                "balance": 100.0,
                "cellphone": "11999888156"
            },
            {
                "_id": "665dff9c183ce834954a2f42",
                "name": "Teste1",
                "cpf": "284.438.920-13",
                "institution": "001",
                "agency": "0001",
                "account": "000",
                "currency": "BRL",
                "balance": 100.0,
                "cellphone": "11999888155"
            }
        ]
    )

    return mock_get_user_by_id_different_currencies


@pytest.fixture
def mock_get_conversion(mocker):
    mock_get_conversion = mocker.patch(
        "controllers.transference_controller.TransferenceController.get_conversion", 
        return_value={
            "result": 30.0
        }
    )
    return mock_get_conversion


@pytest.fixture
def mock_send_sms(mocker):
    mock_send_sms = mocker.patch(
        "controllers.push_controller.PushController.send_sms", 
        return_value={}
    )
    return mock_send_sms