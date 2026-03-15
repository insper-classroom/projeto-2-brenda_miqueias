from flask import Flask, jsonify, request
from utils import run_sql

app = Flask(__name__)

@app.route('/imoveis', methods=['GET'])
def get_all_imoveis():
    command = 'SELECT * FROM imoveis'
    return run_sql(command, fetch=True)

@app.route('/imoveis/<int:id>', methods=['GET'])
def get_imovel_id(id):
    command = 'SELECT * FROM imoveis WHERE id=%s'
    return run_sql(command, params=(id,), fetch=True)

@app.route('/imoveis/submit', methods=['POST'])
def submit_imovel():
    data = request.get_json(silent=True) #captura do corpo da requisicao

    # retorna 400 se o usuario nao inserir nada no corpo da requisicao
    if not data:
        return jsonify({'erro': 'Envie um JSON valido no corpo da requisicao.'}), 400

    campos_obrigatorios = ['logradouro', 'cidade'] # NOT NULL em imoveis.sql (o banco rejeita registros sem esses valores)
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)] #lista campos obrigatrios faltantes

    # se a lista campos_faltantes não estiver vazia, ele retorna 400.
    if campos_faltantes:
        return jsonify({'erro': f"Campos obrigatorios ausentes: {', '.join(campos_faltantes)}"}), 400

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
        return jsonify({'erro': 'Nao foi possivel cadastrar o imovel.'}), 500

    # se tudo der certo, retornmaos 201 ( Created ) e a mensagem de cadastro
    return jsonify({'mensagem': 'Imovel cadastrado com sucesso.'}), 201

@app.route('/imoveis/update/<int:id>', methods=['PUT'])
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

if __name__== '__main__':
    app.run(debug=True)