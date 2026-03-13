from flask import Flask
from utils import run_sql

app = Flask(__name__)

@app.route('/imoveis', methods=['GET'])
def get_all_imoveis():
    command = 'SELECT * FROM imoveis'
    return run_sql(command, fetch=True)

if __name__== '__main__':
    app.run(debug=True)