import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'port': int(os.getenv('DB_PORT', '3306')),
    }

def run_sql(command, params=None, fetch=False, return_rowcount=False):
    '''Executa comandos SQL em um banco de dados MySQL.

    Args:
        command (str): Comando SQL a ser executado.
        params (tuple | list | None, optional): Parametros do comando SQL.
            Defaults to None.
        fetch (bool, optional): Indica se o comando deve retornar resultados.
            Defaults to False.
        return_rowcount (bool, optional): Quando ``True`` e ``fetch`` for
            ``False``, retorna a quantidade de linhas afetadas.
            Defaults to False.

    Returns:
        list[dict] | bool | int | None: Retorna uma lista de dicionarios
        quando ``fetch`` for ``True``, ``True`` em caso de sucesso para
        comandos sem retorno, a quantidade de linhas afetadas quando
        ``return_rowcount`` for ``True``, ou ``None`` em caso de erro.
    '''
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        
        cursor = connection.cursor(dictionary=True)

        cursor.execute(command, params or ())

        if fetch:
            result = cursor.fetchall()
            return result

        connection.commit()
        if return_rowcount:
            return cursor.rowcount
        return True

    except mysql.connector.Error as e:
        print(f"Erro ao conectar/executar no MySQL: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()