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
