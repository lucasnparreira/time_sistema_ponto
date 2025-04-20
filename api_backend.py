from datetime import datetime 
from flask import Flask, json, redirect, request, jsonify, render_template, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*")

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    return dict(user=session.get('user'))

@app.route('/funcionario', methods=['POST', 'GET'])
def add_funcionario():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar funcionário por matrícula ou nome (GET)
    if request.method == 'GET':
        search = request.args.get('search')  # Alterado para pegar da query string
        if search:
            cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ? OR nome = ?', (search, search))
            funcionario = cursor.fetchone()

            if funcionario:
                return jsonify({'funcionario': funcionario}), 200
            else:
                conn.close()
                return jsonify({'error': 'Funcionário não encontrado.'}), 404

    # Adicionar funcionário (POST)
    if request.method == 'POST':
        data = request.json
        
        print("Dados recebidos:", data)
        
        # Verificar se matrícula e nome são obrigatórios
        if not data.get('matricula') or not data.get('nome'):
            return jsonify({"error": "Matrícula e nome são obrigatórios."}), 400  # Status 400 Bad Request
        
        query = '''
            INSERT INTO FUNCIONARIO (matricula, nome, funcao, data_inicio, data_termino, 
                                    departamento, escala_id, gerente, endereco, telefone, cpf, rg, banco, agencia, conta_corrente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        values = (
            data.get('matricula'), data.get('nome'), data.get('funcao'), data.get('data_inicio'), data.get('data_termino'),
            data.get('departamento'), data.get('escala_id'), data.get('gerente'), data.get('endereco'), data.get('telefone'), data.get('cpf'), 
            data.get('rg'), data.get('banco'), data.get('agencia'), data.get('conta_corrente')
        )

        try:
            cursor.execute(query, values)
            conn.commit()
            return jsonify({'message': 'Funcionário cadastrado com sucesso!'}), 201  # Status 201 Created
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # Status 500 Internal Server Error
        finally:
            cursor.close()
            conn.close()


@app.route('/funcionario/<int:matricula>', methods=['DELETE'])
# @login_required
def delete_funcionario(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('select * from funcionario where matricula = ?', (matricula,) )
    funcionario = cursor.fetchone()

    if not funcionario:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    cursor.execute('DELETE FROM FUNCIONARIO WHERE matricula = ?', (matricula,))
    conn.commit()

    cursor.close()
    conn.close()
  
    return jsonify({'message': 'Funcionário deletado com sucesso'}), 200


@app.route('/funcionario/<int:matricula>', methods=['PUT'])
# @login_required
def update_funcionario(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ?', (matricula,))
    funcionario = cursor.fetchone()

    if funcionario is None:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    data = request.get_json()

    query = '''
        UPDATE FUNCIONARIO
        SET nome = ?, funcao = ?, data_inicio = ?, data_termino = ?, 
            departamento = ?, escala_id = ?, gerente = ?, endereco = ?, telefone = ?, 
            cpf = ?, rg = ?, banco = ?, agencia = ?, conta_corrente = ?
        WHERE matricula = ?
    '''
    values = (
        data['nome'], data['funcao'], data['data_inicio'], data.get('data_termino'),
        data['departamento'], data['escala_id'], data.get('gerente'), data.get('endereco'), data['telefone'],
        data['cpf'], data['rg'], data['banco'], data['agencia'], data['conta_corrente'], matricula
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Funcionário atualizado com sucesso'}), 200


@app.route('/funcionario/<int:matricula>', methods=['GET'])
# @login_required
def get_funcionario(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ?', (matricula,))
    funcionario = cursor.fetchone()

    if not funcionario:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    funcionario_data = {
        'matricula': funcionario['matricula'],
        'nome': funcionario['nome'],
        'funcao': funcionario['funcao'],
        'data_inicio': funcionario['data_inicio'],
        'data_termino': funcionario['data_termino'],
        'departamento': funcionario['departamento'],
        'escala_id': funcionario['escala_id'],
        'gerente': funcionario['gerente'],
        'endereco': funcionario['endereco'],
        'telefone': funcionario['telefone'],
        'cpf': funcionario['cpf'],
        'rg': funcionario['rg'],
        'banco': funcionario['banco'],
        'agencia': funcionario['agencia'],
        'conta_corrente': funcionario['conta_corrente']
    }

    cursor.close()
    conn.close()
    return jsonify(funcionario_data), 200


@app.route('/funcionarios', methods=['GET'])
# @login_required
def list_funcionarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FUNCIONARIO')
    funcionarios = cursor.fetchall()

    # Verificar se a tabela está vazia
    if not funcionarios:
        return jsonify({'message': 'Tabela de funcionários vazia'}), 200
    
    funcionarios_json = [
        {
            "matricula": funcionario[0],
            "nome": funcionario[1],
            "funcao": funcionario[2],
            "data_inicio": funcionario[3],
            "data_termino": funcionario[4],
            "departamento": funcionario[5],
            "escala_id": funcionario[6],
            "gerente": funcionario[7],
            "endereco": funcionario[8],
            "telefone": funcionario[9],
            "cpf": funcionario[10],
            "rg": funcionario[11],
            "banco": funcionario[12],
            "agencia": funcionario[13],
            "conta_corrente": funcionario[14]
        }
        for funcionario in funcionarios
    ]

    conn.close()
    
    return jsonify({'funcionarios': funcionarios_json}), 200

@app.route('/endereco', methods=['GET','POST'])
# @login_required
def add_endereco():
    data = request.json
    rua = data.get('rua')
    bairro = data.get('bairro')
    cidade = data.get('cidade')
    pais = data.get('pais')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    if not all([rua, bairro, cidade, pais]):
        return jsonify({'error':'Dados incompletos'}), 404
    
    cursor.execute('INSERT INTO ENDERECO (rua, bairro, cidade, pais) VALUES (?, ?, ?, ?)', (rua, bairro, cidade, pais))
    conn.commit()
    conn.close()

    return jsonify({'message':'Endereco adicionado com sucesso!'}), 201


@app.route('/endereco/<int:id>', methods=['PUT'])
# @login_required
def edit_endereco(id):
    data = request.json
    rua = data.get('rua')
    bairro = data.get('bairro')
    cidade = data.get('cidade')
    pais = data.get('pais')

    conn = get_db_connection()
    cursor = conn.cursor()
    

    cursor.execute('SELECT * FROM ENDERECO WHERE id = ?', (id,))
    endereco = cursor.fetchone()

    if not endereco:
        return jsonify({'error': 'Endereço não encontrado'}), 404

    cursor.execute('UPDATE ENDERECO SET rua = ?, bairro = ?, cidade = ?, pais = ? WHERE id = ?', (rua, bairro, cidade, pais, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Endereco atualizado com sucesso!'}), 201


@app.route('/endereco/<int:id>', methods=['POST'])
# @login_required
def delete_endereco(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ENDERECO WHERE id = ?', (id,))
    endereco = cursor.fetchone()

    if not endereco:
        return jsonify({'error': 'Endereço não encontrado'}), 404
    
    cursor.execute('DELETE FROM ENDERECO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Endereco deletado com sucesso!'}), 201


@app.route('/endereco/<int:id>', methods=['GET'])
# @login_required
def view_endereco(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ENDERECO WHERE id = ?', (id,))
    endereco = cursor.fetchone()

    if not endereco:
        conn.close()
        return jsonify({'error': 'Endereco não encontrado'}), 404
    
    conn.close()
    
    return jsonify({'endereco': endereco})


@app.route('/enderecos', methods=['GET'])
# @login_required
def list_enderecos():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ENDERECO')
    enderecos = cursor.fetchall()

    # Verifique a estrutura das tuplas retornadas
    print("Endereços retornados:", enderecos)  # Adicionei este print para depurar

    # Verificar se a tabela está vazia
    if not enderecos:
        conn.close()
        return jsonify({'message': 'Tabela de endereços vazia'}), 200

    # Estruturar o retorno para JSON de maneira mais amigável
    enderecos_json = [
        {
            "id": endereco[0],            # Verifique se a tupla tem pelo menos 7 elementos
            "logradouro": endereco[1],    # Caso contrário, isso gerará o erro
            "numero": endereco[2],
            "bairro": endereco[3],
            "cidade": endereco[4],
            "cep": endereco[5]
        }
        for endereco in enderecos
    ]

    conn.close()
    
    return jsonify({'enderecos': enderecos_json}), 200

@app.route('/departamento', methods=['POST'])
# @login_required
def add_departamento():
    data = request.json 
    descricao = data.get('descricao')

    if not descricao:
        return jsonify({'error': 'Dados incompletos'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO DEPARTAMENTO (descricao) VALUES (?)', (descricao,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Departamento criado com sucesso!'}), 201
    
@app.route('/departamento/<int:id>', methods=['GET', 'PUT'])
def edit_departamento(id):
    if request.method == 'GET':
        # Busca o departamento com o ID fornecido
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
        departamento = cursor.fetchone()
        conn.close()

        if not departamento:
            return jsonify({'error': 'Departamento não encontrado'}), 404

        # Retorna os dados do departamento em formato JSON
        return jsonify({'id': departamento[0], 'descricao': departamento[1]}), 200

    elif request.method == 'PUT':
        # Atualiza o departamento com os dados fornecidos no corpo da requisição
        data = request.json
        descricao = data.get('descricao')

        if not descricao:
            return jsonify({'error': 'Descrição é obrigatória'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
        departamento = cursor.fetchone()

        if not departamento:
            conn.close()
            return jsonify({'error': 'Departamento não encontrado'}), 404

        cursor.execute('UPDATE DEPARTAMENTO SET descricao = ? WHERE id = ?', (descricao, id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Departamento atualizado com sucesso!'}), 200


@app.route('/departamento/<int:id>/delete', methods=['POST'])
# @login_required
def delete_departamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o departamento existe
    cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
    departamento = cursor.fetchone()

    if not departamento:
        conn.close()
        return jsonify({'error': 'Departamento não encontrado'}), 404
    
    cursor.execute('DELETE FROM DEPARTAMENTO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Departamento deletado com sucesso!'}), 200



# @app.route('/departamento/<int:id>', methods=['GET'])
# # @login_required
# def view_departamento(id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
#     departamento = cursor.fetchone()

#     if not departamento:
#         return jsonify({'error': 'Departamento nao encontrado.'}), 404

#     conn.close()
    
#     return jsonify({'departamento': departamento}), 201


@app.route('/departamentos')
# @login_required
def list_departamentos():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM DEPARTAMENTO')
    departamentos = cursor.fetchall()

    # Verifica se a tabela está vazia
    if not departamentos:
        conn.close()
        return jsonify({'message': 'Tabela de departamentos vazia.'}), 200

    departamentos_json = [
        {
            "id": departamento[0],           # Acesse os valores por índice, assumindo que a consulta retorna as colunas esperadas
            "descricao": departamento[1]
        }
        for departamento in departamentos
    ]

    conn.close()

    # Retorna a lista de departamentos
    return jsonify({'departamentos': departamentos_json}), 200



@app.route('/funcao', methods=['POST'])
# @login_required
def add_funcao():
    data = request.json
    descricao = data.get('descricao')

    if not descricao:
        return jsonify({'error':'Dados incompletos'}), 404
    
    conn = get_db_connection()
    cursor = conn.cursor()
        
    cursor.execute('INSERT INTO FUNCAO (descricao) VALUES (?)', (descricao,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Funcao criada com sucesso!'}), 201

@app.route('/funcao/<int:id>', methods=['GET', 'PUT'])
# @login_required
def edit_funcao(id):
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
        funcao = cursor.fetchone()

        if not funcao:
            conn.close()
            return jsonify({'error': 'Função não encontrada'}), 404

        conn.close()
        return jsonify({'funcao': {'id': funcao[0], 'descricao': funcao[1]}}), 200

    elif request.method == 'PUT':
        data = request.json
        descricao = data.get('descricao')

        if not descricao:
            return jsonify({'error': 'Descrição é obrigatória'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
        funcao = cursor.fetchone()

        if not funcao:
            conn.close()
            return jsonify({'error': 'Função não encontrada'}), 404

        cursor.execute('UPDATE FUNCAO SET descricao = ? WHERE id = ?', (descricao, id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Função atualizada com sucesso!'}), 200


@app.route('/funcao/<int:id>/delete', methods=['DELETE'])
# @login_required
def delete_funcao(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
    funcao = cursor.fetchone()

    if not funcao:
        conn.close()
        return jsonify({'error': 'função não encontrada'}), 404
    
    cursor.execute('DELETE FROM FUNCAO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Funcao deletada com sucesso!'}), 204



# @app.route('/funcao/<int:id>', methods=['GET'])
# # @login_required
# def view_funcao(id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
#     funcao = cursor.fetchone()
    
#     if not funcao:
#         conn.close()
#         return jsonify({'error': 'função não encontrada'}), 404

#     conn.close()
#     return jsonify({'funcao': funcao}), 201

@app.route('/funcoes')
# @login_required
def list_funcoes():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FUNCAO')
    funcoes = cursor.fetchall()
    conn.close()

    # if not funcoes:
    #     conn.close()
    #     return jsonify({'message': 'Tabela de funções vazia'}), 200  # Retorna 200 OK se não houver funções
    
    funcoes_json = [
        {
            "id": funcao[0],           # Acesse os valores por índice
            "descricao": funcao[1]
        }
        for funcao in funcoes
    ]

    

    return jsonify({'funcoes': funcoes_json}), 200

@app.route('/evento/novo', methods=['GET','POST'])
# @login_required
def add_evento():
    data = request.json
    codigo = data.get('codigo')
    descricao = data.get('descricao')

    if not descricao:
        return jsonify({'error': 'Dados incompletos'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO EVENTO (codigo, descricao) VALUES (?, ?)', (codigo, descricao,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Evento criado com sucesso!'}), 201


@app.route('/evento/<int:id>', methods=['GET', 'PUT'])
def edit_evento(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
        evento = cursor.fetchone()

        if not evento:
            conn.close()
            return jsonify({'error': 'Evento não encontrado'}), 404

        evento_json = {
            "id": evento[0],
            "codigo": evento[1],
            "descricao": evento[2]
        }

        conn.close()
        return jsonify({'evento': evento_json}), 200

    elif request.method == 'PUT':
        data = request.json
        codigo = data.get('codigo')
        descricao = data.get('descricao')

        cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
        evento = cursor.fetchone()

        if not evento:
            conn.close()
            return jsonify({'error': 'Evento não encontrado'}), 404

        cursor.execute('UPDATE EVENTO SET codigo = ?, descricao = ? WHERE id = ?', (codigo, descricao, id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Evento atualizado com sucesso!'}), 200


@app.route('/evento/<int:id>/delete', methods=['POST','DELETE'])
# @login_required
def delete_evento(id):
    if request.method == 'POST':
        if request.form.get('_method') == 'DELETE':
            request.method = 'DELETE'
            
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return jsonify({'error': 'Evento não encontrado'}), 404

    cursor.execute('DELETE FROM EVENTO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Evento deletado com sucesso!'}), 204

@app.route('/evento/<int:id>', methods=['GET'])
# @login_required
def view_evento(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return jsonify({'error': 'Evento não encontrado'}), 404
    
    conn.close()
    
    return jsonify({'evento': evento}), 201

@app.route('/eventos', methods=['GET'])
# @login_required
def list_eventos():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM EVENTO')
    eventos = cursor.fetchall()

    if not eventos:
        conn.close()
        return jsonify({'message': 'Tabela de eventos vazia'}), 200  

    eventos_json = [
        {
            "id": evento[0],           
            "codigo": evento[1],
            "descricao": evento[2]
        }
        for evento in eventos
    ]

    conn.close()

    return jsonify({'eventos': eventos_json}), 200  

@app.route('/ponto', methods=['GET', 'POST'])
# @login_required
def add_ponto():
    conn = None
    try:
        data = request.json

        hora_entrada = data.get('hora_entrada')
        hora_saida = data.get('hora_saida')
        data_ponto = data.get('data')
        nome_funcionario = data.get('funcionario')
        evento = data.get('evento')

        if not all([hora_entrada, hora_saida, data_ponto, nome_funcionario, evento]):
            return jsonify({'error': 'Dados incompletos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Busca matrícula do funcionário
        cursor.execute('SELECT matricula FROM FUNCIONARIO WHERE nome = ?', (nome_funcionario,))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({'error': 'Funcionário não encontrado'}), 404

        matricula_funcionario = resultado['matricula']
        
        dias_semana = {
            'Monday': 'Segunda',
            'Tuesday': 'Terca',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sabado',
            'Sunday': 'Domingo'
        }

        dia_semana_en = datetime.datetime.strptime(data_ponto, '%Y-%m-%d').strftime('%A')
        dia_semana = dias_semana.get(dia_semana_en, dia_semana_en)

        # Busca escala do funcionário para o dia
        cursor.execute('''
            SELECT e.hora_entrada, e.hora_saida
            FROM ESCALA e
            JOIN ESCALA_FUNCIONARIO ef ON e.id = ef.escala_id
            WHERE ef.funcionario = ? AND e.dia_semana = ?
        ''', (matricula_funcionario, dia_semana))

        escala = cursor.fetchone()

        if escala:
            entrada_escala = datetime.datetime.strptime(escala['hora_entrada'], '%H:%M')
            saida_escala = datetime.datetime.strptime(escala['hora_saida'], '%H:%M')
            entrada_real = datetime.datetime.strptime(hora_entrada, '%H:%M')
            saida_real = datetime.datetime.strptime(hora_saida, '%H:%M')

            horas_normais = max(0, (min(saida_real, saida_escala) - max(entrada_real, entrada_escala)).total_seconds() / 3600)
            horas_extras = max(0, (saida_real - saida_escala).total_seconds() / 3600)
        else:
            horas_normais = 0
            horas_extras = 0

        # Busca código do evento
        cursor.execute('SELECT codigo FROM EVENTO WHERE descricao = ?', (evento,))
        evento_resultado = cursor.fetchone()

        if evento_resultado:
            evento = evento_resultado['codigo']
        else:
            evento = None  # ou algum valor default

        # Insere o ponto no banco
        cursor.execute(
            'INSERT INTO PONTO (funcionario, data, hora_entrada, hora_saida, evento, horas_normais, horas_extras) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (matricula_funcionario, data_ponto, hora_entrada, hora_saida, evento, horas_normais, horas_extras)
        )
        conn.commit()

        return jsonify({'message': 'Ponto registrado com sucesso!'}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Erro ao registrar ponto: {str(e)}'}), 500

    finally:
        if conn:
            conn.close()


@app.route('/ponto/<int:id>', methods=['PUT'])
# @login_required
def edit_ponto(id):
    try:
        data = request.json

        hora_entrada = data.get('hora_entrada')
        hora_saida = data.get('hora_saida')
        data_ponto = data.get('data')
        nome_funcionario = data.get('funcionario')
        evento = data.get('evento')

        if not all([hora_entrada, hora_saida, data_ponto, nome_funcionario, evento]):
            return jsonify({'error': 'Dados incompletos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se ponto existe
        cursor.execute('SELECT * FROM PONTO WHERE id = ?', (id,))
        ponto_existente = cursor.fetchone()

        if not ponto_existente:
            conn.close()
            return jsonify({'error': 'Ponto não encontrado'}), 404

        # Busca matrícula do funcionário
        cursor.execute('SELECT matricula FROM FUNCIONARIO WHERE nome = ?', (nome_funcionario,))
        resultado = cursor.fetchone()

        if not resultado:
            conn.close()
            return jsonify({'error': 'Funcionário não encontrado'}), 404

        matricula_funcionario = resultado['matricula']

        # Mapeamento dos dias para português
        dias_semana = {
            'Monday': 'Segunda',
            'Tuesday': 'Terca',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sabado',
            'Sunday': 'Domingo'
        }
        dia_semana_en = datetime.datetime.strptime(data_ponto, '%Y-%m-%d').strftime('%A')
        dia_semana = dias_semana.get(dia_semana_en, dia_semana_en)

        # Busca escala do funcionário para o dia
        cursor.execute('''
            SELECT e.hora_entrada, e.hora_saida
            FROM ESCALA e
            JOIN ESCALA_FUNCIONARIO ef ON e.id = ef.escala_id
            WHERE ef.funcionario = ? AND e.dia_semana = ?
        ''', (matricula_funcionario, dia_semana))

        escala = cursor.fetchone()

        if escala:
            entrada_escala = datetime.datetime.strptime(escala['hora_entrada'], '%H:%M')
            saida_escala = datetime.datetime.strptime(escala['hora_saida'], '%H:%M')
            entrada_real = datetime.datetime.strptime(hora_entrada, '%H:%M')
            saida_real = datetime.datetime.strptime(hora_saida, '%H:%M')

            horas_normais = max(0, (min(saida_real, saida_escala) - max(entrada_real, entrada_escala)).total_seconds() / 3600)
            horas_extras = max(0, (saida_real - saida_escala).total_seconds() / 3600)
        else:
            horas_normais = 0
            horas_extras = 0

        # Busca código do evento
        cursor.execute('SELECT codigo FROM EVENTO WHERE descricao = ?', (evento,))
        evento_resultado = cursor.fetchone()

        if evento_resultado:
            evento_codigo = evento_resultado['codigo']
        else:
            evento_codigo = None  # ou algum valor padrão

        # Atualiza o ponto
        cursor.execute('''
            UPDATE PONTO
            SET funcionario = ?, data = ?, hora_entrada = ?, hora_saida = ?, evento = ?, horas_normais = ?, horas_extras = ?
            WHERE id = ?
        ''', (matricula_funcionario, data_ponto, hora_entrada, hora_saida, evento_codigo, horas_normais, horas_extras, id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Ponto atualizado com sucesso!'}), 200

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({'error': f'Erro ao atualizar ponto: {str(e)}'}), 500


@app.route('/ponto/<int:id>/delete', methods=['DELETE'])
# @login_required
def delete_ponto(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM PONTO WHERE id = ?', (id,))
    ponto = cursor.fetchone()

    if not ponto:
        conn.close()
        return jsonify({'error': 'Ponto não encontrado'}), 404
    
    cursor.execute('DELETE FROM PONTO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Ponto deletado com sucesso!'})

@app.route('/ponto/<int:id>', methods=['GET'])
# @login_required
def view_ponto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.id, f.nome, p.data, p.hora_entrada, p.hora_saida, e.descricao
        FROM PONTO p
        JOIN EVENTO e ON p.evento = e.codigo
        JOIN FUNCIONARIO f ON p.funcionario = f.matricula
        and p.id = ?
    ''', (id,))

    ponto = cursor.fetchone()
    
    if not ponto:  # Caso não haja o ponto no banco de dados
        conn.close()
        return jsonify({'error': 'Ponto não encontrado'}), 404
    
    ponto_json = [
        {
            "id": ponto[0],
            "nome": ponto[1],
            "data": ponto[2],
            "hora_entrada": ponto[3],
            "hora_saida": ponto[4],
            "evento": ponto[5]
        }
    ]

    return jsonify({"pontos": ponto_json}), 200


@app.route('/ponto/buscar', methods=['GET'])
# @login_required
def buscar_funcionario():
    query = request.args.get('query')
    
    if not query:
        return jsonify({"error": "A matrícula ou nome deve ser informado para busca"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT matricula, nome
        FROM FUNCIONARIO
        WHERE nome LIKE ? OR matricula LIKE ?
    ''', ('%' + query + '%', '%' + query + '%'))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        funcionario_data = {
            "matricula": resultado['matricula'],
            "nome": resultado['nome']
        }
        return jsonify(funcionario_data)
    else:
        return jsonify({"error": "Funcionário não encontrado"}), 404

@app.route('/pontos', methods=['GET', 'POST'])
# @login_required
def list_pontos():
    conn = get_db_connection()
    cursor = conn.cursor()

    pontos = []
    
    try:
        if request.method == 'POST':
            data = request.json  
            filtro = data.get('filtro')
            filtro_evento = data.get('filtro_evento')

            query = '''
                SELECT p.id, f.nome, p.data, p.hora_entrada, p.hora_saida, e.descricao
                FROM PONTO p
                JOIN EVENTO e ON p.evento = e.codigo
                JOIN FUNCIONARIO f ON p.funcionario = f.matricula
                WHERE 1 = 1
            '''
            params = []

            if filtro:
                query += ' AND (f.matricula = ? OR f.nome LIKE ?)'
                params.extend([filtro, f"%{filtro}%"])

            if filtro_evento:
                query += ' AND (e.codigo = ? OR e.descricao LIKE ?)'
                params.extend([filtro_evento, f"%{filtro_evento}%"])


            cursor.execute(query, params)
        else:
            cursor.execute('''
                SELECT p.id, f.nome, p.data, p.hora_entrada, p.hora_saida, e.descricao
                FROM PONTO p
                JOIN EVENTO e ON p.evento = e.codigo
                JOIN FUNCIONARIO f ON p.funcionario = f.matricula
            ''')
            

        pontos = cursor.fetchall()
        
        if pontos:  # Verifica se há pontos
            pontos_json = [
                {
                    "id": row[0],
                    "nome": row[1],
                    "data": row[2],
                    "hora_entrada": row[3],
                    "hora_saida": row[4],
                    "evento": row[5]
                }
                for row in pontos
            ]
            return jsonify({"pontos": pontos_json}), 200
        else:
            return jsonify({"message": "Nenhum ponto encontrado."}), 404

    except Exception as e:
        return jsonify({"error": f"Erro ao listar pontos: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/usuario', methods=['POST'])
# @login_required
def add_usuario():
    data = request.json
    nome = data.get('nome')
    senha = data.get('senha')

    if not nome or not senha:
        return jsonify({"error":"Nome e senha sao obrigatorios"}), 400
    
    if senha.strip() == '':
        return jsonify({"error":"Senha nao pode ser vazia"}), 400
    
    conn = None 
    try:
        hashed_password = generate_password_hash(senha)

        conn = get_db_connection()
        cursor = conn.cursor()
    
        cursor.execute('INSERT INTO usuario (nome, senha) VALUES (?, ?)', (nome, hashed_password))
        conn.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso!"}), 201
    
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Erro ao cadastrar o usuario: {e}"}), 500
    
    finally:
        if conn:
            conn.close()


@app.route('/usuario/<int:id>', methods=['GET','PUT'])
# @login_required
def edit_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM usuario WHERE id = ?', (id,))
        usuario = cursor.fetchone()
        conn.close()

        if not usuario:
            return jsonify({"error": "Usuario nao encontrado"}), 404

        usuario_dict = {"id": usuario[0], "nome": usuario[1]}
        return jsonify({"usuario": usuario_dict}), 200
    
    elif request.method == 'PUT':
        data = request.json 
        nome = data.get('nome')
        senha = data.get('senha')

        if not nome or not senha:
            return jsonify({"error": "Nome e senha sao obrigatorios"}), 400

        hashed_password = generate_password_hash(senha)

        cursor.execute('''
                        update usuario
                       set nome = ?, senha = ?
                       where id = ?
                       ''', (nome, hashed_password, id))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Usuario atualizado com sucesso!"})

@app.route('/usuario/<int:id>', methods=['POST','DELETE'])
# @login_required
def delete_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('delete from usuario where id = ?', (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Usuario deletado com sucesso!"}), 200

@app.route('/usuarios', methods=['GET'])
# @login_required
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuario')
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    usuarios_json = [{"id": u['id'], "nome": u['nome'], "matricula": u['user_matricula']} for u in usuarios]

    return jsonify({"usuarios": usuarios_json})

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.json 
        nome = data.get('nome')
        senha = data.get('senha')

        if not nome or not senha:
            return jsonify({"error":"Nome e senha sao obrigatorios"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('select * from usuario where nome = ?', (nome,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario and check_password_hash(usuario['senha'], senha):
            user_data = {"id": usuario['id'], "nome": usuario['nome']}
            session['user'] = user_data
            return jsonify({"message": "Login bem-sucedido", **user_data})
        else:
            return jsonify({"error":"Usuario ou senha incorretos"}), 401

    return jsonify({"error":"Metodo nao permitido"}), 405

def get_matricula_by_nome(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT matricula FROM FUNCIONARIO WHERE nome = ?', (nome,))
    resultado = cursor.fetchone()
    
    conn.close()
    
    if resultado:
        return resultado['matricula']
    else:
        return None
    
@app.route('/importar_ponto', methods=['POST'])
def importar_ponto():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['file']

        if arquivo.filename == '':
            return jsonify({'error': 'Nome de arquivo inválido'}), 400

        # Garante que a pasta temp existe
        os.makedirs('temp', exist_ok=True)

        caminho_temp = os.path.join('temp', arquivo.filename)
        arquivo.save(caminho_temp)

        with open(caminho_temp, 'r') as f:
            for linha in f:
                dados = linha.strip().split('|')
                if len(dados) < 3:
                    print(f'Linha com formato inválido: {linha.strip()}')
                    continue

                matricula_funcionario, data_ponto, hora = dados

                cursor.execute('SELECT matricula FROM FUNCIONARIO WHERE matricula = ?', (matricula_funcionario,))
                if not cursor.fetchone():
                    print(f'Funcionario {matricula_funcionario} não encontrado, linha ignorada')
                    continue

                try:
                    data_obj = datetime.strptime(data_ponto, '%Y-%m-%d')
                except ValueError:
                    print(f'Data inválida: {data_ponto}')
                    continue

                dia_semana = data_obj.weekday()

                def classificar_evento(hora):
                    if dia_semana >= 5:
                        return 4
                    if '08:00' <= hora <= '17:00':
                        return 1
                    return 4

                evento_entrada = classificar_evento(hora)
                evento_saida = classificar_evento(hora)

                evento = evento_entrada if evento_entrada == evento_saida else None

                cursor.execute(''' 
                    SELECT id, hora_entrada, hora_saida
                    FROM PONTO 
                    WHERE funcionario = ? AND data = ?
                ''', (matricula_funcionario, data_ponto))

                registro_existente = cursor.fetchone()

                if registro_existente:
                    id_registro, hora_entrada_existente, hora_saida_existente = registro_existente
                
                    if not hora_entrada_existente:
                        cursor.execute(''' 
                            UPDATE PONTO 
                            SET hora_entrada = ?, evento = ?
                            WHERE id = ?
                        ''', (hora, evento_entrada, id_registro))
                elif not hora_saida_existente:
                     cursor.execute(''' 
                            UPDATE PONTO 
                            SET hora_saida = ?, evento = ?
                            WHERE id = ?
                        ''', (hora, evento_saida, id_registro))
                else:
                    cursor.execute('''
                    INSERT INTO PONTO (funcionario, data, hora_entrada, hora_saida, evento)
                    VALUES (?, ?, ?, ?, ?)
                ''', (matricula_funcionario, data_ponto, hora, None, evento))

            conn.commit()

        return jsonify({'message': 'Arquivo processado com sucesso!'}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro na importação: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/escala', methods=['POST'])
# @login_required
def add_escala():
    data = request.json
    descricao = data.get('descricao')
    horarios = data.get('horarios', [])

    if not descricao:
        return jsonify({'error': 'Dados incompletos'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO escala (descricao) VALUES (?)', (descricao,))
    escala_id = cursor.lastrowid

    for h in horarios:
        cursor.execute('''
            INSERT INTO ESCALA_HORARIOS (escala_id, dia_semana, hora_entrada, hora_saida)
            VALUES (?, ?, ?, ?) 
        ''', (escala_id, h['dia_semana'], h['hora_entrada'], h['hora_saida']))

    conn.commit()
    conn.close()

    return jsonify({'message': 'escala criada com sucesso!'}), 201

@app.route('/escala/<int:id>', methods=['GET', 'PUT'])
def edit_escala(id):
    if request.method == 'GET':
        # Busca a escala com o ID fornecido
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM escala WHERE id = ?', (id,))
        escala = cursor.fetchone()

        if not escala:
            conn.close()
            return jsonify({'error': 'escala não encontrada'}), 404

        cursor.execute('SELECT dia_semana, hora_entrada, hora_saida FROM ESCALA_HORARIOS WHERE escala_id = ?', (id,))
        horarios = cursor.fetchall()
        conn.close()

        horarios_list = []
        for h in horarios:
            horarios_list.append({
                'dia_semana': h[0],
                'hora_entrada': h[1],
                'hora_saida': h[2]
            })
        
        # Retorna os dados da escala em formato JSON
        return jsonify({
            'id': escala[0], 
            'descricao': escala[1],
            'horarios': horarios_list
            }), 200

    elif request.method == 'PUT':
        # Atualiza a escala com os dados fornecidos no corpo da requisição
        data = request.json
        descricao = data.get('descricao')
        horarios = data.get('horarios', [])

        if not descricao:
            return jsonify({'error': 'Descrição é obrigatória'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM escala WHERE id = ?', (id,))
        escala = cursor.fetchone()

        if not escala:
            conn.close()
            return jsonify({'error': 'escala não encontrada'}), 404

        cursor.execute('UPDATE escala SET descricao = ? WHERE id = ?', (descricao, id))

        cursor.execute('DELETE FROM ESCALA_HORARIOS WHERE escala_id = ?', (id,))

        for h in horarios:
            cursor.execute('''
                INSERT INTO ESCALA_HORARIOS (escala_id, dia_semana, hora_entrada, hora_saida)
                VALUES (?, ?, ?, ?)
            ''', (id, h['dia_semana'], h['hora_entrada'], h['hora_saida']))

        conn.commit()
        conn.close()

        return jsonify({'message': 'escala atualizada com sucesso!'}), 200


@app.route('/escala/<int:id>/delete', methods=['POST'])
# @login_required
def delete_escala(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se a escala existe
    cursor.execute('SELECT * FROM escala WHERE id = ?', (id,))
    escala = cursor.fetchone()

    if not escala:
        conn.close()
        return jsonify({'error': 'escala não encontrado'}), 404

    cursor.execute("DELETE FROM ESCALA_HORARIOS WHERE escala_id = ?", (id,))
    cursor.execute('DELETE FROM escala WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'escala deletado com sucesso!'}), 200


@app.route('/escalas', methods=['GET'])
# @login_required
def list_escalas():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM escala')
    escalas = cursor.fetchall()

    # Verifica se a tabela está vazia
    if not escalas:
        conn.close()
        return jsonify({'message': 'Tabela de escalas vazia.'}), 200
    
    result = []
    for e in escalas:
        cursor.execute("SELECT * FROM ESCALA_HORARIOS WHERE escala_id = ?", (e['id'],))
        horarios = cursor.fetchall()
        result.append({
            'id': e['id'],
            'descricao': e['descricao'],
            'horarios': [dict(h) for h in horarios]
        })

    conn.close()

    # Retorna a lista de escalas
    return jsonify(result), 200

@app.route('/escala_funcionario', methods=['POST'])
def assign_escala_to_funcionario():
    try:
        data = request.json

        funcionario = data.get('funcionario')  # ID do funcionário
        escala_id = data.get('escala_id')     # ID da escala

        if not all([funcionario, escala_id]):
            return jsonify({'error': 'Dados incompletos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se a escala existe
        cursor.execute('SELECT * FROM ESCALA WHERE id = ?', (escala_id,))
        escala = cursor.fetchone()

        if not escala:
            return jsonify({'error': 'Escala não encontrada'}), 404

        # Verifica se o funcionário existe
        cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ?', (funcionario,))
        funcionario_db = cursor.fetchone()

        if not funcionario_db:
            return jsonify({'error': 'Funcionário não encontrado'}), 404

        # Associa o funcionário à escala
        cursor.execute('''
            INSERT INTO ESCALA_FUNCIONARIO (funcionario, escala_id) 
            VALUES (?, ?)
        ''', (funcionario, escala_id))
        conn.commit()

        return jsonify({'message': 'Funcionário associado à escala com sucesso!'}), 201

    except Exception as e:
        return jsonify({'error': f'Erro ao associar funcionário à escala: {str(e)}'}), 500

@app.route('/escala_funcionario', methods=['GET'])
def list_escala_funcionarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT EF.id, EF.funcionario, F.nome, EF.escala_id, E.descricao 
            FROM ESCALA_FUNCIONARIO EF
            JOIN FUNCIONARIO F ON EF.funcionario = F.matricula
            JOIN ESCALA E ON EF.escala_id = E.id
        ''')
        resultados = cursor.fetchall()

        lista = []
        for row in resultados:
            lista.append({
                'id': row['id'],
                'funcionario': row['funcionario'],
                'nome_funcionario': row['nome'],
                'escala_id': row['escala_id'],
                'descricao_escala': row['descricao']
            })

        return jsonify({'associacoes': lista}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/escala_funcionario/<int:id>', methods=['PUT'])
def edit_escala_funcionario(id):
    try:
        data = request.json

        funcionario = data.get('funcionario')
        escala_id = data.get('escala_id')

        if not all([funcionario, escala_id]):
            return jsonify({'error': 'Dados incompletos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se associação existe
        cursor.execute('SELECT * FROM ESCALA_FUNCIONARIO WHERE id = ?', (id,))
        associacao = cursor.fetchone()
        if not associacao:
            return jsonify({'error': 'Associação não encontrada'}), 404

        # Verifica se escala existe
        cursor.execute('SELECT * FROM ESCALA WHERE id = ?', (escala_id,))
        escala = cursor.fetchone()
        if not escala:
            return jsonify({'error': 'Escala não encontrada'}), 404

        # Verifica se funcionário existe
        cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ?', (funcionario,))
        funcionario_db = cursor.fetchone()
        if not funcionario_db:
            return jsonify({'error': 'Funcionário não encontrado'}), 404

        # Atualiza a associação
        cursor.execute('''
            UPDATE ESCALA_FUNCIONARIO 
            SET funcionario = ?, escala_id = ? 
            WHERE id = ?
        ''', (funcionario, escala_id, id))

        conn.commit()
        return jsonify({'message': 'Associação atualizada com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/escala_funcionario/<int:id>', methods=['DELETE'])
def delete_escala_funcionario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se associação existe
        cursor.execute('SELECT * FROM ESCALA_FUNCIONARIO WHERE id = ?', (id,))
        associacao = cursor.fetchone()
        if not associacao:
            return jsonify({'error': 'Associação não encontrada'}), 404

        # Exclui a associação
        cursor.execute('DELETE FROM ESCALA_FUNCIONARIO WHERE id = ?', (id,))
        conn.commit()

        return jsonify({'message': 'Associação removida com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# estrutura para mensageria 
@app.route('/chat')
def index():
    return render_template('chat.html', user=session.get('user'))

@app.route('/conversas', methods=['POST'])
def criar_conversa():
    data = request.get_json()
    titulo = data.get('titulo')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO CONVERSA (titulo) VALUES (?)', (titulo,))
    conversa_id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'id': conversa_id, 'titulo': titulo}), 201

@app.route('/conversas', methods=['GET'])
def listar_conversas():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, titulo FROM CONVERSA')
    conversas = cursor.fetchall()

    resultado = [{'id': c['id'], 'titulo': c['titulo']} for c in conversas]

    cursor.close()
    conn.close()

    return jsonify(resultado)

@app.route('/conversas/<int:conversa_id>/mensagens', methods=['GET'])
def listar_mensagens(conversa_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(''' 
        SELECT M.id, U.matricula as login_usuario, M.conteudo, M.data_hora
        FROM MENSAGEM M
        JOIN USUARIO U ON M.usuario_id = U.id
        WHERE M.conversa_id = ?
        ORDER BY M.data_hora ASC
    ''', (conversa_id,))

    mensagens = cursor.fetchall()

    resultado = [{
        'id': m['id'],
        'login_usuario': m['login_usuario'],
        'conteudo': m['conteudo'],
        'data_hora': m['data_hora']
    } for m in mensagens]

    cursor.close()
    conn.close()

    return jsonify(resultado)

@socketio.on('enviar_mensagem')
def handle_enviar_mensagem(data):
    print(f"Mensagem recebida: {data}")  # Verificando os dados recebidos

    conversa_id = data.get('conversa_id')
    login_usuario = data.get('login_usuario')
    conteudo = data.get('conteudo')

    print(f"Mensagem recebida: {conteudo}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Busca o id do usuário pela matricula
    cursor.execute("SELECT id FROM USUARIO WHERE matricula = ?", (login_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        emit('nova_mensagem', {'login_usuario': 'Sistema', 'conteudo': 'Usuário não encontrado'})
        return
    
    usuario_id = usuario['id']

    cursor.execute(''' 
        INSERT INTO MENSAGEM (conversa_id, usuario_id, conteudo)
        VALUES (?, ?, ?)
    ''', (conversa_id, usuario_id, conteudo))
    conn.commit()

    # Envia a mensagem para todos os participantes da conversa
    emit('nova_mensagem', {
        'conversa_id': conversa_id,
        'login_usuario': login_usuario,
        'conteudo': conteudo
    }, broadcast=True)
    
    cursor.close()
    conn.close()


@socketio.on('entrar_conversa')
def handle_entrar_conversa(data):
    conversa_id = data.get('conversa_id')
    join_room(f'conversa_{conversa_id}')
    print(f"Usuario entrou na conversa {conversa_id}")

@socketio.on('connect')
def handle_connect():
    print("Cliente conectado com sucesso!")
    emit('message', {'data': 'Olá, cliente! Conexão bem-sucedida!'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Cliente desconectado.")

if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
