from unittest.mock import patch
from servidor import app


def test_delete_imovel_sucesso():
    with patch('servidor.run_sql', return_value=1) as mocked_run_sql:
        client = app.test_client()
        response = client.delete('/imoveis/1')

    assert response.status_code == 200
    body = response.get_json()
    assert body['data'] == {'mensagem': 'Imovel excluido com sucesso.'}
    assert isinstance(body['links'], list)
    assert len(body['links']) > 0
    mocked_run_sql.assert_called_once_with(
        'DELETE FROM imoveis WHERE id = %s',
        params=(1,),
        return_rowcount=True
    )

def test_delete_imovel_nao_encontrado():
    with patch('servidor.run_sql', return_value=0) as mocked_run_sql:
        client = app.test_client()
        response = client.delete('/imoveis/999')

    assert response.status_code == 404
    body = response.get_json()
    assert body['erro'] == 'Imovel nao encontrado.'
    assert isinstance(body['links'], list)
    assert len(body['links']) > 0
    mocked_run_sql.assert_called_once_with(
        'DELETE FROM imoveis WHERE id = %s',
        params=(999,),
        return_rowcount=True
    )

def test_delete_imovel_erro_banco():
    with patch('servidor.run_sql', return_value=None) as mocked_run_sql:
        client = app.test_client()
        response = client.delete('/imoveis/1')

    assert response.status_code == 500
    body = response.get_json()
    assert body['erro'] == 'Nao foi possivel excluir o imovel.'
    assert isinstance(body['links'], list)
    assert len(body['links']) > 0
    mocked_run_sql.assert_called_once_with(
        'DELETE FROM imoveis WHERE id = %s',
        params=(1,),
        return_rowcount=True
    )