from flask import Flask
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

if __name__== '__main__':
    app.run(debug=True)