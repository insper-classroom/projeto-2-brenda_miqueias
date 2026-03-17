from flask import Flask, jsonify, request, url_for
from utils import run_sql

app = Flask(__name__)

@app.route('/imoveis', methods=['GET'])
def get_all_imoveis():
    command = 'SELECT * FROM imoveis'
    resultado = run_sql(command, fetch=True)
    if resultado is None:
        return jsonify({
            'erro': 'Nao foi possivel consultar os imoveis.',
            'links': [
                {'rel': 'self', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'},
                {'rel': 'create', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'}
            ]
        }), 500
    return jsonify({
        'data': resultado,
        'links': [
            {'rel': 'self', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'},
            {'rel': 'create', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'},
            {'rel': 'by_type', 'href': url_for('get_all_type_imovel', imovel_type='{tipo}', _external=True), 'method': 'GET'},
            {'rel': 'by_city', 'href': f"{url_for('get_all_city_imovel', _external=True)}?cidade={{cidade}}", 'method': 'GET'}
        ]
    }), 200

@app.route('/imoveis/<int:id>', methods=['GET'])
def get_imovel_id(id):
    command = 'SELECT * FROM imoveis WHERE id=%s'
    resultado = run_sql(command, params=(id,), fetch=True)
    if resultado is None:
        return jsonify({
            'erro': 'Nao foi possivel consultar o imovel.',
            'links': [
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'},
                {'rel': 'create', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'}
            ]
        }), 500
    if not resultado:
        return jsonify({
            'erro': 'Imovel nao encontrado.',
            'links': [
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'},
                {'rel': 'create', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'}
            ]
        }), 404
    return jsonify({
        'data': resultado[0],
        'links': [
            {'rel': 'self', 'href': url_for('get_imovel_id', id=id, _external=True), 'method': 'GET'},
            {'rel': 'update', 'href': url_for('update_imovel', id=id, _external=True), 'method': 'PUT'},
            {'rel': 'delete', 'href': url_for('imoveis_delete', id=id, _external=True), 'method': 'DELETE'},
            {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
        ]
    }), 200

@app.route('/imoveis', methods=['POST'])
def submit_imovel():
    data = request.get_json(silent=True) #captura do corpo da requisicao

    # retorna 400 se o usuario nao inserir nada no corpo da requisicao
    if not data:
        return jsonify({
            'erro': 'Envie um JSON valido no corpo da requisicao.',
            'links': [
                {'rel': 'self', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'},
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
            ]
        }), 400

    campos_obrigatorios = ['logradouro', 'cidade'] # NOT NULL em imoveis.sql (o banco rejeita registros sem esses valores)
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)] #lista campos obrigatrios faltantes

    # se a lista campos_faltantes não estiver vazia, ele retorna 400.
    if campos_faltantes:
        return jsonify({
            'erro': f"Campos obrigatorios ausentes: {', '.join(campos_faltantes)}",
            'links': [
                {'rel': 'self', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'},
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
            ]
        }), 400

    command = '''
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
    params = (
        data['logradouro'],
        data.get('tipo_logradouro'),
        data.get('bairro'),
        data['cidade'],
        data.get('cep'),
        data.get('tipo'),
        data.get('valor'),
        data.get('data_aquisicao'),
    )

    run = run_sql(command, params=params)

    # se o run nao devolver uma resposta do banaco, retorna 500 ( Internal Server Error )
    if run is None:
        return jsonify({
            'erro': 'Nao foi possivel cadastrar o imovel.',
            'links': [
                {'rel': 'self', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'},
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
            ]
        }), 500

    # se tudo der certo, retornmaos 201 ( Created ) e a mensagem de cadastro
    return jsonify({
        'data': {'mensagem': 'Imovel cadastrado com sucesso.'},
        'links': [
            {'rel': 'self', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'},
            {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
        ]
    }), 201

@app.route('/imoveis/<int:id>', methods=['PUT'])
def update_imovel(id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'erro': 'Envie um JSON valido no corpo da requisicao.'}), 400

    campos_obrigatorios = ['logradouro', 'cidade']
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)]
    if campos_faltantes:
        return jsonify({'erro': f"Campos obrigatorios ausentes: {', '.join(campos_faltantes)}"}), 400

    existe = run_sql('SELECT id FROM imoveis WHERE id=%s', params=(id,), fetch=True)
    if existe is None:
        return jsonify({'erro': 'Nao foi possivel verificar o imovel.'}), 500
    if not existe:
        return jsonify({'erro': 'Imovel nao encontrado.'}), 404

    command = '''
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
    params = (
        data['logradouro'],
        data.get('tipo_logradouro'),
        data.get('bairro'),
        data['cidade'],
        data.get('cep'),
        data.get('tipo'),
        data.get('valor'),
        data.get('data_aquisicao'),
        id,
    )

    atualizado = run_sql(command, params=params)
    if atualizado is None:
        return jsonify({'erro': 'Nao foi possivel atualizar o imovel.'}), 500

    imovel_atualizado = run_sql('SELECT * FROM imoveis WHERE id=%s', params=(id,), fetch=True)
    if imovel_atualizado is None:
        return jsonify({'erro': 'Imovel atualizado, mas nao foi possivel recuperar os dados.'}), 500

    return jsonify({'mensagem': 'Imovel atualizado com sucesso.', 'imovel': imovel_atualizado[0]}), 200

@app.route('/imoveis/<int:id>', methods=['DELETE'])
def imoveis_delete(id):
    command = 'DELETE FROM imoveis WHERE id = %s'
    result = run_sql(command, params=(id,), return_rowcount=True)
    if result is None:
        return jsonify({'erro': 'Nao foi possivel excluir o imovel.'}), 500
    if result == 0:
        return jsonify({'erro': 'Imovel nao encontrado.'}), 404
    if result > 0:
        return jsonify({'mensagem': 'Imovel excluido com sucesso.'}), 200
    return jsonify({'erro': 'Não foi possível excluir o imóvel.'}), 500

@app.route('/imoveis/tipo/<string:imovel_type>', methods=['GET'])
def get_all_type_imovel(imovel_type):
    tipo = imovel_type.strip()

    if not tipo:
        return jsonify({
            'erro': 'Tipo de imovel invalido.',
            'links': [
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
            ]
        }), 400

    command = 'SELECT * FROM imoveis WHERE LOWER(tipo)=LOWER(%s)'
    resultado = run_sql(command=command, params=(tipo,), fetch=True)

    if resultado is None:
        return jsonify({
            'erro': 'Nao foi possivel consultar os imoveis por tipo.',
            'links': [
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'},
                {'rel': 'self', 'href': url_for('get_all_type_imovel', imovel_type=tipo, _external=True), 'method': 'GET'}
            ]
        }), 500

    if not resultado:
        return jsonify({
            'erro': f'Nenhum imovel encontrado para o tipo: {tipo}',
            'links': [
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'},
                {'rel': 'create', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'}
            ]
        }), 404

    return jsonify({
        'data': resultado,
        'links': [
            {'rel': 'self', 'href': url_for('get_all_type_imovel', imovel_type=tipo, _external=True), 'method': 'GET'},
            {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
        ]
    }), 200

@app.route('/imoveis/cidade', methods=['GET'])
def get_all_city_imovel():
    city = request.args.get('cidade', '').strip()

    if not city:
        return jsonify({
            'erro': 'Informe a cidade na query string, ex: /imoveis/cidade?cidade=Recife',
            'links': [
                {'rel': 'self', 'href': f"{url_for('get_all_city_imovel', _external=True)}?cidade={{cidade}}", 'method': 'GET'},
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
            ]
        }), 400

    command = 'SELECT * FROM imoveis WHERE LOWER(cidade)=LOWER(%s)'
    resultado = run_sql(command=command, params=(city,), fetch=True)

    if resultado is None:
        return jsonify({
            'erro': 'Nao foi possivel consultar os imoveis por cidade.',
            'links': [
                {'rel': 'self', 'href': f"{url_for('get_all_city_imovel', _external=True)}?cidade={city}", 'method': 'GET'},
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
            ]
        }), 500

    if not resultado:
        return jsonify({
            'erro': f'Nenhum imovel encontrado para a cidade: {city}',
            'links': [
                {'rel': 'self', 'href': f"{url_for('get_all_city_imovel', _external=True)}?cidade={city}", 'method': 'GET'},
                {'rel': 'create', 'href': url_for('submit_imovel', _external=True), 'method': 'POST'},
                {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
            ]
        }), 404

    return jsonify({
        'data': resultado,
        'links': [
            {'rel': 'self', 'href': f"{url_for('get_all_city_imovel', _external=True)}?cidade={city}", 'method': 'GET'},
            {'rel': 'collection', 'href': url_for('get_all_imoveis', _external=True), 'method': 'GET'}
        ]
    }), 200

if __name__== '__main__':
    app.run(debug=True)