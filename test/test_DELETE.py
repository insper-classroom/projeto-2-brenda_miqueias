from unittest.mock import patch
from servidor import app


def test_delete_imovel_sucesso():
    with patch('servidor.run_sql', return_value=1) as mocked_run_sql:
        client = app.test_client()
        response = client.delete('/imoveis/delete/1')

    assert response.status_code == 200
    assert response.get_json() == {'mensagem': 'Imovel excluido com sucesso.'}
    mocked_run_sql.assert_called_once_with(
        'DELETE FROM imoveis WHERE id = %s',
        params=(1,),
        return_rowcount=True
    )