from copy import deepcopy
from freezegun import freeze_time
import json
import re

from database.models import PixKey, Transaction
from tests.payloads import (
    payload_create_key,
    payload_transaction_other_currency,
    payload_transaction,
    response_transaction,
    response_get_key
)
from utils.exceptions import BalanceNotFound, UserServiceError


def test_create_key_success(client):
    """Testa o endpoint de criação de chave com sucesso."""

    response = client.post("/create_key", json=payload_create_key)

    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["status"] == "success"


def test_create_key_error_key_exists(client):
    """Testa o endpoint de criação de chave com chave já existente."""

    response = client.post("/create_key", json=payload_create_key)

    assert response.status_code == 200

    response = client.post("/create_key", json=payload_create_key)

    data = json.loads(response.data)
    assert response.status_code == 409
    assert data["message"] == "Chave já está em uso"


def test_create_key_error_invalid_payload(client):
    """Testa o endpoint de criação de chave com payload inválido."""
    invalid_payload_create_key = deepcopy(payload_create_key)
    invalid_payload_create_key.pop("type")

    response = client.post("/create_key", json=invalid_payload_create_key)

    data = json.loads(response.data)
    assert response.status_code == 422
    assert data["message"] == "{'type': ['Missing data for required field.']}"


def test_create_key_error_other_exeception(client, mocker):
    """Testa o endpoint de criação de chave com payload exceção generica."""

    mocker.patch(
        "controllers.transference_controller.TransferenceController.create_key", side_effect=Exception("Erro ao criar chave")
    )

    response = client.post("/create_key", json=payload_create_key)
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data["status"] == 400
    assert data["message"] == "Erro ao criar chave"


def test_get_user_keys_success(client):
    """Testa o endpoint de buscar chaves do usuário pelo id de usuário."""
    with freeze_time("2024-01-01"):
        response = client.post("/create_key", json=payload_create_key)

        data = json.loads(response.data)
        assert response.status_code == 200
        match = re.search(r"ID: ([a-f0-9]{24})", data["message"])
        assert match is not None
        key_id = match.group(1)

        expected_response = deepcopy(response_get_key)
        expected_response["result"][0]["_id"] = key_id

        user_id = payload_create_key["user_id"]

        response = client.get(f"/my_keys/{user_id}")
        assert response.status_code == 200
        assert response.json == expected_response


def test_get_user_keys_user_not_found(client):
    """Testa o endpoint de buscar chaves do usuário pelo id de usuário com erro de chaves não encontradas."""

    response = client.get("/my_keys/664e9b2da3835b65a119b35f")

    assert response.status_code == 404


def test_get_user_keys_generic_error(client, mocker):
    """Testa o endpoint de atualizar saldo do usuário com erro generico."""

    response = client.post("/create_key", json=payload_create_key)

    assert response.status_code == 200

    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_keys", side_effect=Exception("Erro ao buscar chaves")
    )

    user_id = payload_create_key["user_id"]

    response = client.get(f"/my_keys/{user_id}")

    data = json.loads(response.data)
    assert response.status_code == 400
    assert data["status"] == 400
    assert data["message"] == "Erro ao buscar chaves"


def test_get_key_by_id_success(client):
    """Testa o endpoint de buscar chave do usuário pelo id da chave."""
    with freeze_time("2024-01-01"):
        response = client.post("/create_key", json=payload_create_key)

        data = json.loads(response.data)
        assert response.status_code == 200
        match = re.search(r"ID: ([a-f0-9]{24})", data["message"])
        assert match is not None
        key_id = match.group(1)

        expected_response = deepcopy(response_get_key)
        expected_response["result"][0]["_id"] = key_id

        response = client.get(f"/key/{key_id}")

        assert response.status_code == 200
        assert response.json == expected_response["result"][0]


def test_get_key_by_id_key_not_found(client):
    """Testa o endpoint de buscar chave do usuário pelo id da chave com erro de chave não encontrada."""

    response = client.get("/key/664e9b2da3835b65a119b35d")

    assert response.status_code == 404


def test_get_key_by_id_generic_error(client, mocker):
    """Testa o endpoint de buscar chave do usuário com erro generico."""

    response = client.post("/create_key", json=payload_create_key)

    data = json.loads(response.data)
    assert response.status_code == 200
    match = re.search(r"ID: ([a-f0-9]{24})", data["message"])
    assert match is not None
    key_id = match.group(1)

    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_key_by_id", side_effect=Exception("Erro ao buscar chave")
    )

    response = client.get(f"/key/{key_id}")

    data = json.loads(response.data)
    assert response.status_code == 400
    assert data["status"] == 400
    assert data["message"] == "Erro ao buscar chave"


def test_get_key_by_value_success(client):
    """Testa o endpoint de buscar chave do usuário pelo valor da chave."""

    with freeze_time("2024-01-01"):
        response = client.post("/create_key", json=payload_create_key)

        data = json.loads(response.data)
        assert response.status_code == 200
        match = re.search(r"ID: ([a-f0-9]{24})", data["message"])
        assert match is not None
        key_id = match.group(1)

        key = payload_create_key["key"]

        response = client.get(f"/user_keys/{key}")

        expected_response = deepcopy(response_get_key)
        expected_response["result"][0]["_id"] = key_id

        assert response.status_code == 200
        assert response.json == expected_response["result"][0]


def test_get_key_by_value_key_not_found(client):
    """Testa o endpoint de buscar chave do usuário pelo valor da chave com erro de chave não encontrada."""

    response = client.get("/key/664e9b2da3835b65a119b35d")

    assert response.status_code == 404


def test_get_key_by_value_generic_error(client, mocker):
    """Testa o endpoint de buscar chave do usuário pelo valor da chave com erro generico."""

    response = client.post("/create_key", json=payload_create_key)

    assert response.status_code == 200

    key = payload_create_key["key"]

    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_by_key", side_effect=Exception("Erro ao buscar chave")
    )

    response = client.get(f"/user_keys/{key}")

    data = json.loads(response.data)
    assert response.status_code == 400
    assert data["status"] == 400
    assert data["message"] == "Erro ao buscar chave"


def test_create_transference_success_same_currency(
        client, 
        mock_get_key_by_user, 
        mock_get_user_balance, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms
    ):
    """Testa o endpoint de transferencia com sucesso para a mesma moeda."""
    with freeze_time("2024-01-01"):
        expected_response = deepcopy(response_transaction)

        response = client.post("/transference", json=payload_transaction)

        data = json.loads(response.data)

        transference_id = data["_id"]
        expected_response["_id"] = transference_id

        transaction = Transaction.find_by_id(transference_id)

        assert response.status_code == 200
        assert response.json == expected_response
        assert payload_transaction["value"] == transaction["value"]
        mock_get_conversion.assert_not_called()
        mock_get_key_by_user.assert_called_once()
        mock_get_user_balance.assert_called()
        mock_updated_balance.assert_called()
        mock_get_user_by_id.call_count == 2
        mock_send_sms.call_count == 2


def test_create_transference_success_sender_n_desired_same_currency(
        client, 
        mock_get_key_by_user, 
        mock_get_user_balance, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms
    ):
    """Testa o endpoint de transferencia com sucesso para usuários com mesma moeda, mas moeda da transação diferente."""
    with freeze_time("2024-01-01"):
        expected_response = deepcopy(response_transaction)

        response = client.post("/transference", json=payload_transaction_other_currency)

        data = json.loads(response.data)

        transference_id = data["_id"]
        expected_response["_id"] = transference_id
        expected_response["currency"] = "USD"

        transaction = Transaction.find_by_id(transference_id)

        assert response.status_code == 200
        assert response.json == expected_response
        assert expected_response["value"] == transaction["value"]
        mock_get_conversion.assert_called_once()
        mock_get_key_by_user.assert_called_once()
        mock_get_user_balance.assert_called()
        mock_updated_balance.assert_called()
        mock_get_user_by_id.call_count == 2
        mock_send_sms.call_count == 2


def test_create_transference_success_different_currency(
        client, 
        mock_get_key_by_user, 
        mock_get_user_balance, 
        mock_updated_balance,
        mock_get_user_by_id_different_currencies,
        mock_get_conversion,
        mock_send_sms
    ):
    """Testa o endpoint de transferencia com sucesso para moedas diferentes."""
    with freeze_time("2024-01-01"):
        expected_response = deepcopy(response_transaction)

        response = client.post("/transference", json=payload_transaction_other_currency)

        data = json.loads(response.data)

        transference_id = data["_id"]
        expected_response["_id"] = transference_id
        expected_response["currency"] = "USD"

        transaction = Transaction.find_by_id(transference_id)

        assert response.status_code == 200
        assert response.json == expected_response
        assert expected_response["value"] == transaction["value"]
        mock_get_conversion.assert_called_once()
        mock_get_key_by_user.assert_called_once()
        mock_get_user_balance.assert_called()
        mock_updated_balance.assert_called()
        mock_get_user_by_id_different_currencies.call_count == 2
        mock_send_sms.call_count == 2


def test_create_transference_error_invalid_payload(client):
    """Testa o endpoint de transferencia com payload inválido."""
    invalid_payload_create_transaction = deepcopy(payload_transaction)
    invalid_payload_create_transaction.pop("value")

    response = client.post("/transference", json=invalid_payload_create_transaction)

    data = json.loads(response.data)
    assert response.status_code == 422
    assert data["message"] == "{'value': ['O valor a ser transferido é obrigatório']}"


def test_create_transference_error_other_exeception(client, mocker):
    """Testa o endpoint de transferencia com payload exceção generica."""

    mocker.patch(
        "controllers.transference_controller.TransferenceController.transaction", side_effect=Exception("Erro ao realizar transferencia")
    )

    response = client.post("/transference", json=payload_transaction)
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data["status"] == 400
    assert data["message"] == "Erro ao realizar transferencia"


def test_create_transference_user_not_found_error(
        client,
        mock_get_user_balance, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms,
        mocker
    ):
    """Testa o endpoint de transferencia com sucesso."""
    with freeze_time("2024-01-01"):
        invalid_key_payload = deepcopy(payload_transaction)
        invalid_key_payload["receiver_key"] = "99999999"

        response = client.post("/transference", json=invalid_key_payload)

        pix_key = invalid_key_payload["receiver_key"]

        assert response.status_code == 404
        assert response.json == {"status": 404, "message": f"Usuário não encontrado para chave {pix_key}"}
        mock_get_conversion.assert_not_called()
        mock_get_user_balance.assert_not_called()
        mock_updated_balance.assert_not_called()
        mock_get_user_by_id.assert_not_called()
        mock_send_sms.assert_not_called()


def test_create_transference_balance_not_found_error(
        client,
        mock_get_key_by_user, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms,
        mocker
    ):
    """Testa o endpoint de transferencia com saldo não encontrado."""
    with freeze_time("2024-01-01"):

        mocker.patch(
            "controllers.transference_controller.TransferenceController.get_user_balance", side_effect=BalanceNotFound("Saldo indisponível")
        )

        response = client.post("/transference", json=payload_transaction)

        assert response.status_code == 404
        assert response.json == {"status": 404, "message": "Saldo indisponível"}
        mock_get_conversion.assert_not_called()
        mock_get_key_by_user.assert_called()
        mock_updated_balance.assert_not_called()
        mock_get_user_by_id.assert_not_called()
        mock_send_sms.assert_not_called()


def test_create_transference_user_serivce_unavailable_error(
        client,
        mock_get_key_by_user, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms,
        mocker
    ):
    """Testa o endpoint de transferencia com serviço de usuário indisponível."""
    with freeze_time("2024-01-01"):

        mocker.patch(
            "controllers.transference_controller.TransferenceController.get_user_balance", side_effect=UserServiceError("Serviço de usuário indisponível")
        )

        response = client.post("/transference", json=payload_transaction)

        assert response.status_code == 400
        assert response.json == {"status": 400, "message": "Serviço de usuário indisponível"}
        mock_get_conversion.assert_not_called()
        mock_get_key_by_user.assert_called()
        mock_updated_balance.assert_not_called()
        mock_get_user_by_id.assert_not_called()
        mock_send_sms.assert_not_called()


def test_create_transference_insuficient_balance(
        client, 
        mock_get_key_by_user, 
        mock_get_user_insuficient_balance, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms
    ):
    """Testa o endpoint de transferencia sem saldo suficiente."""
    with freeze_time("2024-01-01"):
        response = client.post("/transference", json=payload_transaction)

        assert response.status_code == 400
        assert response.json == {"status": 400, "message": "Usuário não possui saldo suficiente"}
        mock_get_conversion.assert_not_called()
        mock_get_key_by_user.assert_called_once()
        mock_get_user_insuficient_balance.assert_called()
        mock_updated_balance.assert_not_called()
        mock_get_user_by_id.call_count == 2
        mock_send_sms.assert_not_called()


def test_get_transaction_by_user_id_success(
        client, 
        mock_get_key_by_user, 
        mock_get_user_balance, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms
    ):
    """Testa o endpoint de buscar transferencia pelo id do usuário com sucesso."""
    with freeze_time("2024-01-01"):

        response = client.post("/create_key", json=payload_create_key)

        assert response.status_code == 200

        response = client.post("/transference", json=payload_transaction)

        data = json.loads(response.data)

        transference_id = data["_id"]

        assert response.status_code == 200
        mock_get_conversion.assert_not_called()
        mock_get_key_by_user.assert_called_once()
        mock_get_user_balance.assert_called()
        mock_updated_balance.assert_called()
        mock_get_user_by_id.call_count == 2
        mock_send_sms.call_count == 2

        sender_id = payload_transaction["sender_id"]
        receiver_key = PixKey.find_by_key(payload_transaction["receiver_key"])
        receiver_id = receiver_key["user_id"]

        response = client.get(f"/my_transferences/{sender_id}")

        assert response.status_code == 200
        assert response.json["result"][0]["_id"] == transference_id

        response = client.get(f"/my_transferences/{receiver_id}")

        assert response.status_code == 200


def test_get_transaction_not_found(
        client, 
    ):
    """Testa o endpoint de buscar transferência com transferência não encontrada."""
    with freeze_time("2024-01-01"):
        sender_id = payload_transaction["sender_id"]

        response = client.get(f"/my_transferences/{sender_id}")

        assert response.status_code == 404
        assert response.json == {"status": 404, "message": "Sem nenhuma transação realizada"}


def test_get_transaction_generic_error(client, mocker):
    """Testa o endpoint de buscar transferencia com exceção generica."""

    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_user_transactions", side_effect=Exception("Erro ao buscar transferencia")
    )

    sender_id = payload_transaction["sender_id"]

    response = client.get(f"/my_transferences/{sender_id}")
    assert response.status_code == 400
    assert response.json == {"status": 400, "message": "Erro ao buscar transferencia"}


def test_get_transaction_by_id_success(
        client, 
        mock_get_key_by_user, 
        mock_get_user_balance, 
        mock_updated_balance,
        mock_get_user_by_id,
        mock_get_conversion,
        mock_send_sms
    ):
    """Testa o endpoint de buscar transferencia pelo id com sucesso."""
    with freeze_time("2024-01-01"):

        response = client.post("/create_key", json=payload_create_key)

        assert response.status_code == 200

        response = client.post("/transference", json=payload_transaction)

        data = json.loads(response.data)

        transference_id = data["_id"]

        assert response.status_code == 200
        mock_get_conversion.assert_not_called()
        mock_get_key_by_user.assert_called_once()
        mock_get_user_balance.assert_called()
        mock_updated_balance.assert_called()
        mock_get_user_by_id.call_count == 2
        mock_send_sms.call_count == 2

        response = client.get(f"/transferences/{transference_id}")

        assert response.status_code == 200


def test_get_transaction_by_id_not_found(
        client, 
    ):
    """Testa o endpoint de buscar transferência por id com transferência não encontrada."""
    with freeze_time("2024-01-01"):
        response = client.get("/transferences/664e9b2da3835b65a119b35d")

        assert response.status_code == 404
        assert response.json == {"status": 404, "message": "Sem nenhuma transação realizada"}


def test_get_transaction_by_id_generic_error(client, mocker):
    """Testa o endpoint de buscar transferencia com exceção generica."""

    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_transaction_by_id", side_effect=Exception("Erro ao buscar transferencia")
    )

    response = client.get("/transferences/664e9b2da3835b65a119b35d")
    assert response.status_code == 400
    assert response.json == {"status": 400, "message": "Erro ao buscar transferencia"}