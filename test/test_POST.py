from unittest.mock import patch
from servidor import app

def test_submit_imovel():
	'''Testa a rota POST /submit.

        Valida que:

        O corpo JSON e convertido em parametros na ordem esperada.
        O INSERT e executado sem fetch.
        A rota retorna status 201 quando o cadastro e bem-sucedido.
    '''

	# dados enviados para o corpo da requisicao
	payload = {
		'logradouro': 'Rua das Flores',
		'tipo_logradouro': 'Rua',
		'bairro': 'Centro',
		'cidade': 'Sao Paulo',
		'cep': '01000-000',
		'tipo': 'apartamento',
		'valor': 450000.0,
		'data_aquisicao': '2026-03-14',
	}

	# comando esperado
	expected_command = '''
        INSERT INTO imoveis (
            logradouro,
            tipo_logradouro,
            bairro,
            cidade,
            cep,
            tipo,
            valor,
            data_aquisicao
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''

	# parametros esperados
	expected_params = (
		'Rua das Flores',
		'Rua',
		'Centro',
		'Sao Paulo',
		'01000-000',
		'apartamento',
		450000.0,
		'2026-03-14',
	)

	with patch('servidor.run_sql', return_value=True) as mocked_run_sql:
		client = app.test_client()
		response = client.post('/submit', json=payload)

	mocked_run_sql.assert_called_once_with(expected_command, params=expected_params)
	assert response.status_code == 201
	assert response.get_json() == {'mensagem': 'Imovel cadastrado com sucesso.'}

def test_submit_imovel_sem_campos_obrigatorios():
	'''Testa a validacao minima da rota POST /submit.'''

	with patch('servidor.run_sql') as mocked_run_sql:
		client = app.test_client()
		response = client.post('/submit', json={'bairro': 'Centro'})

	mocked_run_sql.assert_not_called()
	assert response.status_code == 400
	assert response.get_json() == {'erro': 'Campos obrigatorios ausentes: logradouro, cidade'}