from copy import deepcopy
from freezegun import freeze_time
import json
import re
from tests.payloads import payload_create_key, payload_convert, payload_transaction, response_transaction, response_get_key


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


def test_convert_success(client):
    """Testa o endpoint de conversão com sucesso."""

    response = client.post("/convert", json=payload_convert)

    assert response.status_code == 200
    assert response.json["result"] == 2.862


def test_convert_error_invalid_payload(client):
    """Testa o endpoint de conversão com payload inválido."""
    invalid_payload_convert = deepcopy(payload_convert)
    invalid_payload_convert.pop("currency")

    response = client.post("/convert", json=invalid_payload_convert)

    data = json.loads(response.data)
    assert response.status_code == 422
    assert data["message"] == "{'currency': ['A moeda é obrigatória']}"


def test_convert_error_other_exeception(client, mocker):
    """Testa o endpoint de conversão com payload exceção generica."""

    mocker.patch(
        "controllers.transference_controller.TransferenceController.get_tax_balance", side_effect=Exception("Erro ao converter valor")
    )

    response = client.post("/convert", json=payload_convert)
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data["status"] == 400
    assert data["message"] == "Erro ao converter valor"


def test_get_user_keys_success(client):
    """Testa o endpoint de buscar chaves do usuário pelo id de usuário."""
    with freeze_time("2024-01-01"):
        response = client.post("/create_key", json=payload_create_key)

        data = json.loads(response.data)
        assert response.status_code == 200
        match = re.search(r"ID: ([a-f0-9]{24})", data["message"])
        assert match is not None
        key_id = match.group(1)

        expected_reponse = deepcopy(response_get_key)
        expected_reponse["result"][0]["_id"] = key_id

        user_id = payload_create_key["user_id"]

        response = client.get(f"/my_keys/{user_id}")
        assert response.status_code == 200
        assert response.json == expected_reponse


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

        expected_reponse = deepcopy(response_get_key)
        expected_reponse["result"][0]["_id"] = key_id

        response = client.get(f"/key/{key_id}")

        assert response.status_code == 200
        assert response.json == expected_reponse


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

    response = client.post("/create_key", json=payload_create_key)

    assert response.status_code == 200

    key = payload_create_key["key"]

    response = client.get(f"/user_keys/{key}")

    assert response.status_code == 200
    assert response.json == response_get_key


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


def test_create_transference_success(
        client, 
        mock_get_key_by_user, 
        mock_get_user_balance, 
        mock_updated_balance,
        mock_get_receiver_user_by_id,
        mock_get_sender_user_by_id
    ):
    """Testa o endpoint de transferencia com sucesso."""
    with freeze_time("2024-01-01"):
        expected_reponse = deepcopy(response_transaction)

        response = client.post("/transference", json=payload_transaction)

        expected_reponse["_id"] = response["_id"]

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data == expected_reponse
        mock_get_key_by_user.assert_called_once()
        mock_get_user_balance.assert_called()
        mock_updated_balance.assert_called()
        mock_get_receiver_user_by_id.assert_called()
        mock_get_sender_user_by_id.assert_called()


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