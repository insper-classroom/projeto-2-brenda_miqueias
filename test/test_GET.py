from unittest.mock import patch
from servidor import app

def test_get_all_imoveis():
	'''Testa a rota GET /imoveis garantindo que:

        1. run_sql é chamado uma única vez com a query esperada e fetch=True.
        2. A resposta HTTP retorna status 200.
        3. O corpo da resposta em JSON corresponde aos dados simulados.
        4. O acesso ao banco é isolado com mock para manter o teste determinístico.
    '''
	expected_data = [{"id": 1, "bairro": "Centro"}]

	with patch('servidor.run_sql', return_value=expected_data) as mocked_run_sql:
		client = app.test_client()
		response = client.get('/imoveis')

	mocked_run_sql.assert_called_once_with('SELECT * FROM imoveis', fetch=True)
	assert response.status_code == 200
	assert response.get_json() == expected_data


def test_get_imovel_id():
	'''Testa a rota GET /imoveis/<id>.

        Valida que:

        A consulta SQL usa filtro por id com placeholder correto.
        O parâmetro id é enviado em params como tupla.
        A resposta retorna status 200.
        O JSON retornado corresponde aos dados mockados.
    '''
	expected_data = [{"id": 1, "bairro": "Centro"}]

	with patch('servidor.run_sql', return_value=expected_data) as mocked_run_sql:
		client = app.test_client()
		response = client.get('/imoveis/1')

	mocked_run_sql.assert_called_once_with('SELECT * FROM imoveis WHERE id=%s', params=(1,), fetch=True)
	assert response.status_code == 200
	assert response.get_json() == expected_data

def test_get_all_type_imovel_sucesso():
	'''Testa a rota GET /imoveis/tipo/<imovel_type> em caso de sucesso.'''
	expected_data = [{"id": 1, "tipo": "apartamento"}]

	with patch('servidor.run_sql', return_value=expected_data) as mocked_run_sql:
		client = app.test_client()
		response = client.get('/imoveis/tipo/apartamento')

	mocked_run_sql.assert_called_once_with(
		command='SELECT * FROM imoveis WHERE LOWER(tipo)=LOWER(%s)',
		params=('apartamento',),
		fetch=True,
	)
	assert response.status_code == 200
	assert response.get_json() == expected_data

def test_get_all_type_imovel_nao_encontrado():
	'''Testa 404 quando nao ha imoveis para o tipo informado.'''
	with patch('servidor.run_sql', return_value=[]) as mocked_run_sql:
		client = app.test_client()
		response = client.get('/imoveis/tipo/cobertura')

	mocked_run_sql.assert_called_once_with(
		command='SELECT * FROM imoveis WHERE LOWER(tipo)=LOWER(%s)',
		params=('cobertura',),
		fetch=True,
	)
	assert response.status_code == 404
	assert response.get_json() == {'erro': 'Nenhum imovel encontrado para o tipo: cobertura'}

def test_get_all_city_imovel_sucesso():
	'''Testa a rota GET /imoveis/cidade?cidade=<cidade> em caso de sucesso.'''
	expected_data = [{"id": 1, "cidade": "Recife"}]

	with patch('servidor.run_sql', return_value=expected_data) as mocked_run_sql:
		client = app.test_client()
		response = client.get('/imoveis/cidade?cidade=Recife')

	mocked_run_sql.assert_called_once_with(
		command='SELECT * FROM imoveis WHERE LOWER(cidade)=LOWER(%s)',
		params=('Recife',),
		fetch=True,
	)
	assert response.status_code == 200
	assert response.get_json() == expected_data

def test_get_all_city_imovel_sem_query_param():
	'''Testa 400 quando a cidade nao e informada na query string.'''
	with patch('servidor.run_sql') as mocked_run_sql:
		client = app.test_client()
		response = client.get('/imoveis/cidade')

	mocked_run_sql.assert_not_called()
	assert response.status_code == 400
	assert response.get_json() == {
		'erro': 'Informe a cidade na query string, ex: /imoveis/cidade?cidade=Recife'
	}

def test_get_all_city_imovel_nao_encontrado():
	'''Testa 404 quando nao ha imoveis para a cidade informada.'''
	with patch('servidor.run_sql', return_value=[]) as mocked_run_sql:
		client = app.test_client()
		response = client.get('/imoveis/cidade?cidade=Manaus')

	mocked_run_sql.assert_called_once_with(
		command='SELECT * FROM imoveis WHERE LOWER(cidade)=LOWER(%s)',
		params=('Manaus',),
		fetch=True,
	)
	assert response.status_code == 404
	assert response.get_json() == {'erro': 'Nenhum imovel encontrado para a cidade: Manaus'}