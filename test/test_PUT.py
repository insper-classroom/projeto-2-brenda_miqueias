from unittest.mock import call, patch
from servidor import app


def test_update_imovel_sucesso():
	'''Testa a rota PUT /imoveis/<id> em caso de sucesso.'''
	payload = {
		'logradouro': 'Rua Nova',
		'tipo_logradouro': 'Rua',
		'bairro': 'Centro',
		'cidade': 'Sao Paulo',
		'cep': '01000-000',
		'tipo': 'apartamento',
		'valor': 500000.0,
		'data_aquisicao': '2024-01-01',
	}

	expected_update_command = '''
		UPDATE imoveis
		SET
			logradouro=%s,
			tipo_logradouro=%s,
			bairro=%s,
			cidade=%s,
			cep=%s,
			tipo=%s,
			valor=%s,
			data_aquisicao=%s
		WHERE id=%s
	'''

	expected_update_params = (
		'Rua Nova',
		'Rua',
		'Centro',
		'Sao Paulo',
		'01000-000',
		'apartamento',
		500000.0,
		'2024-01-01',
		1,
	)

	updated_row = [{
		'id': 1,
		'logradouro': 'Rua Nova',
		'tipo_logradouro': 'Rua',
		'bairro': 'Centro',
		'cidade': 'Sao Paulo',
		'cep': '01000-000',
		'tipo': 'apartamento',
		'valor': 500000.0,
		'data_aquisicao': '2024-01-01',
	}]

	with patch('servidor.run_sql', side_effect=[[{'id': 1}], True, updated_row]) as mocked_run_sql:
		client = app.test_client()
		response = client.put('/imoveis/1', json=payload)

	assert response.status_code == 200
	assert response.get_json() == {
		'mensagem': 'Imovel atualizado com sucesso.',
		'imovel': updated_row[0],
	}
	mocked_run_sql.assert_has_calls([
		call('SELECT id FROM imoveis WHERE id=%s', params=(1,), fetch=True),
		call('SELECT * FROM imoveis WHERE id=%s', params=(1,), fetch=True),
	], any_order=True)

	update_call = mocked_run_sql.call_args_list[1]
	assert 'UPDATE imoveis' in update_call.args[0]
	assert update_call.kwargs['params'] == expected_update_params


def test_update_imovel_id_inexistente():
	'''Testa 404 quando o id nao existe.'''
	with patch('servidor.run_sql', return_value=[]) as mocked_run_sql:
		client = app.test_client()
		response = client.put('/imoveis/999', json={'logradouro': 'Rua A', 'cidade': 'Sao Paulo'})

	assert response.status_code == 404
	assert response.get_json() == {'erro': 'Imovel nao encontrado.'}
	mocked_run_sql.assert_called_once_with('SELECT id FROM imoveis WHERE id=%s', params=(999,), fetch=True)


def test_update_imovel_sem_json():
	'''Testa 400 quando o corpo nao possui JSON valido.'''
	with patch('servidor.run_sql') as mocked_run_sql:
		client = app.test_client()
		response = client.put('/imoveis/1', data='texto')

	assert response.status_code == 400
	assert response.get_json() == {'erro': 'Envie um JSON valido no corpo da requisicao.'}
	mocked_run_sql.assert_not_called()