# transference-service

Esse serviço realiza as funcionalidades envolvendo transferência e cadastro de chaves pix. Também lida com um serviço externo para enviar sms aos usuários.

# Execução

Para executar o serviço, pode-se rodar via docker e via venv.

## Via Venv

### Criar virtual env para python 3.11

```
pyhton3 -m venv .venv
```

### Ativar virtual env

```
source {Caminho para venv}/bin/activate
```

### Baixar requirements
```
pip install -r requirements.txt
```

### Executar API
```
python3 src/main.py
```

## Via Docker
```
sudo docker-compose up -d
```

## Para rodar os testes
Necessário ter uma venv com no minimo pytest, pytest-mock e pytest-flask instalados. Recomenda-se seguir os passos para rodar projeto via venv. Em seguida rodar:

```
export PYTHONPATH={Caminho completp até a pasta src}
```

```
pytest
```

## OBS.: Para execução correta dos serviços é necessário que as variáveis de ambiente estejam corretamente definidas no settings.py, por segurança as envs são definidas no cluster ao buildar o serviço, seus reais valores não estão definidos nesse serviço. Solicitar aos membros do grupo as variáveis corretas caso necessário.