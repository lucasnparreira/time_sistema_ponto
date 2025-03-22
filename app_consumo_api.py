from flask import Flask, redirect, request, jsonify, render_template, url_for, session, flash
from flask_cors import CORS
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

api_url = "http://localhost:5000"

# def get_db_connection():
#     conn = sqlite3.connect('app.db')
#     conn.row_factory = sqlite3.Row
#     return conn 

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user' not in session:
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

#@app.route('/matricula/<string:nome>', methods=['GET'])
def get_matricula_by_nome(nome):
    response = requests.get(f"{api_url}/matricula/{nome}")
    if response.status_code == 200:
        return response.json().get('matricula')
    return None

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        response = requests.post(f"{api_url}/login", json={"nome": nome, "senha": senha})
        
        if response.status_code == 200:
            user_data = response.json()
            session['user'] = user_data
            session['user_nome'] = user_data.get('user_name')
            print(session['user'])
            print("Usuario conectado")
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Credenciais inválidas")
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session.get('user'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
  
@app.route('/funcionario', methods=['POST', 'GET'])
def add_funcionario():
    if request.method == 'GET':
        search = request.args.get('search')
        if search:
            response = requests.get(f"{api_url}/funcionario", params={'search': search})
            return response.json(), response.status_code
    
    if request.method == 'POST':
        data = request.json
        response = requests.post(f"{api_url}/funcionario", json=data)
        return response.json(), response.status_code

@app.route('/funcionario/<int:matricula>', methods=['DELETE'])
def delete_funcionario(matricula):
    response = requests.delete(f"{api_url}/funcionario/{matricula}")
    return response.json(), response.status_code

@app.route('/funcionario/<int:matricula>', methods=['PUT'])
def update_funcionario(matricula):
    data = request.get_json()
    response = requests.put(f"{api_url}/funcionario/{matricula}", json=data)
    return response.json(), response.status_code

@app.route('/funcionario/<int:matricula>', methods=['GET'])
def get_funcionario(matricula):
    response = requests.get(f"{api_url}/funcionario/{matricula}")
    return response.json(), response.status_code

@app.route('/funcionarios')
def list_funcionarios():
    response = requests.get(f"{api_url}/funcionarios")
    return response.json(), response.status_code

@app.route('/endereco', methods=['GET', 'POST'])
def add_endereco():
    if request.method == 'POST':
        data = request.json
        rua = data.get('rua')
        bairro = data.get('bairro')
        cidade = data.get('cidade')
        pais = data.get('pais')

        if not all([rua, bairro, cidade, pais]):
            return render_template('endereco.html', mensagem="Dados incompletos")

        response = requests.post(f"{api_url}/endereco", json=data)

        if response.status_code == 201:
            return render_template('lista_enderecos.html', mensagem="Endereço adicionado com sucesso!")
        else:
            return render_template('endereco.html', mensagem="Erro ao adicionar o endereço")
    
    return render_template('endereco.html')

@app.route('/endereco/<int:id>', methods=['GET', 'PUT'])
def edit_endereco(id):
    if request.method == 'PUT':
        data = request.json
        rua = data.get('rua')
        bairro = data.get('bairro')
        cidade = data.get('cidade')
        pais = data.get('pais')

        response = requests.get(f"{api_url}/endereco/{id}")

        if response.status_code != 200:
            return render_template('erro.html', mensagem="Endereço não encontrado")

        response = requests.put(f"{api_url}/endereco/{id}", json=data)

        if response.status_code == 201:
            return render_template('sucesso.html', mensagem="Endereço atualizado com sucesso!")
        else:
            return render_template('erro.html', mensagem="Erro ao atualizar o endereço")
    
    response = requests.get(f"{api_url}/endereco/{id}")
    if response.status_code != 200:
        return render_template('erro.html', mensagem="Endereço não encontrado")
    
    endereco = response.json()
    return render_template('edit_endereco.html', endereco=endereco)

@app.route('/endereco/<int:id>', methods=['POST'])
def delete_endereco(id):
    response = requests.get(f"{api_url}/endereco/{id}")

    if response.status_code != 200:
        return render_template('erro.html', mensagem="Endereço não encontrado")

    response = requests.delete(f"{api_url}/endereco/{id}")

    if response.status_code == 200:
        return render_template('sucesso.html', mensagem="Endereço deletado com sucesso!")
    else:
        return render_template('erro.html', mensagem="Erro ao deletar o endereço")

@app.route('/endereco/<int:id>', methods=['GET'])
def view_endereco(id):
    response = requests.get(f"{api_url}/endereco/{id}")

    if response.status_code != 200:
        return render_template('erro.html', mensagem="Endereço não encontrado")
    
    endereco = response.json()
    return render_template('view_endereco.html', endereco=endereco)


@app.route('/enderecos', methods=['GET'])
def list_enderecos():
    response = requests.get(f"{api_url}/enderecos")

    if response.status_code != 200:
        return render_template('erro.html', mensagem="Tabela de endereços vazia")

    enderecos = response.json()
    return render_template('list_enderecos.html', enderecos=enderecos)

@app.route('/departamento', methods=['POST'])
def add_departamento():
    if request.method == 'POST':
        data = request.json
        descricao = data.get('descricao')

        response = requests.post(f"{api_url}/descricao", json=data)

        if response.status_code == 201:
            return render_template('lista_departamentos.html', mensagem="Endereço adicionado com sucesso!")
        else:
            return render_template('departamento.html', mensagem="Erro ao adicionar o departamento")
    
    return render_template('lista_departamentos.html', message='Departamento criado com sucesso!'), 201
    
@app.route('/departamento/<int:id>', methods=['PUT'])
def edit_departamento(id):
    data = request.json
    descricao = data.get('descricao')

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

    return jsonify({'message': 'Departamento atualizado com sucesso!'}), 201


@app.route('/departamento/<int:id>/delete', methods=['POST'])
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

    return jsonify({'message': 'Departamento deletado com sucesso!'}), 201



@app.route('/departamento/<int:id>', methods=['GET'])
def view_departamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
    departamento = cursor.fetchone()

    if not departamento:
        return jsonify({'error': 'Departamento nao encontrado.'}), 404

    conn.close()
    
    return jsonify({'departamento': departamento}), 201


@app.route('/departamentos')
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

@app.route('/funcao/<int:id>', methods=['PUT'])
def edit_funcao(id):
    data = request.json
    #id = request.form.get('id')
    descricao = data.get('descricao')

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

    return jsonify({'message': 'Funcao atualizada com sucesso!'}), 201


@app.route('/funcao/<int:id>/delete', methods=['POST'])
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

    return jsonify({'message': 'Funcao deletada com sucesso!'}), 201



@app.route('/funcao/<int:id>', methods=['GET'])
def view_funcao(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
    funcao = cursor.fetchone()
    
    if not funcao:
        conn.close()
        return jsonify({'error': 'função não encontrada'}), 404

    conn.close()
    return jsonify({'funcao': funcao}), 201

@app.route('/funcoes')
def list_funcoes():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM FUNCAO')
    funcoes = cursor.fetchall()

    if not funcoes:
        conn.close()
        return jsonify({'message': 'Tabela de funções vazia'}), 200  # Retorna 200 OK se não houver funções
    
    funcoes_json = [
        {
            "id": funcao[0],           # Acesse os valores por índice
            "descricao": funcao[1]
        }
        for funcao in funcoes
    ]

    conn.close()

    return jsonify({'funcoes': funcoes_json}), 200

@app.route('/evento/novo', methods=['GET','POST'])
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


@app.route('/evento/<int:id>', methods=['PUT'])
def edit_evento(id):
    data = request.json
    codigo = data.get('codigo')
    descricao = data.get('descricao')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return jsonify({'error': 'Evento não encontrado'}), 404

    cursor.execute('UPDATE EVENTO SET codigo = ?, descricao = ? WHERE id = ?', (codigo, descricao, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Evento atualizado com sucesso!'})


@app.route('/evento/<int:id>/delete', methods=['POST'])
def delete_evento(id):
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

    return jsonify({'message': 'Evento deletado com sucesso!'})



@app.route('/evento/<int:id>', methods=['GET'])
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

@app.route('/eventos')
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
def add_ponto():
    data = request.json
    hora_entrada = data.get('hora_entrada')
    hora_saida = data.get('hora_saida')
    data_ponto = data.get('data')
    nome_funcionario = data.get('funcionario') 
    evento = data.get('evento')

    if not all([hora_entrada, hora_saida, data_ponto, nome_funcionario, evento]):
            return jsonify({'error': 'Dados incompletos'}), 404

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT codigo, descricao FROM evento')
    eventos = cursor.fetchall()

    cursor.execute('SELECT matricula FROM FUNCIONARIO WHERE nome = ?', (nome_funcionario,))
    resultado = cursor.fetchone()
        
    if resultado:
        matricula_funcionario = resultado['matricula']
    else:
        conn.close()
        return jsonify({'error': 'Funcionário não encontrado'}), 404

    try:
        cursor.execute(
            'INSERT INTO PONTO (funcionario, data, hora_entrada, hora_saida, evento) VALUES (?, ?, ?, ?, ?)',
            (matricula_funcionario, data_ponto, hora_entrada, hora_saida, evento)
        )
        conn.commit()
        return jsonify({'message': 'Ponto registrado com sucesso!'}), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Erro ao registrar ponto: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/ponto/<int:id>', methods=['PUT'])
def edit_ponto(id):
    data = request.json
    #id = request.form.get('id')
    hora_entrada = data.get('hora_entrada')
    hora_saida = data.get('hora_saida')
    data = data.get('data')
    funcionario = data.get('funcionario')
    evento = data.get('evento')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    ponto = cursor.fetchone()

    if not ponto:
        conn.close()
        return jsonify({'error': 'Ponto não encontrado'}), 404

    cursor.execute('UPDATE PONTO SET funcionario = ?, data = ?, hora_entrada = ?, hora_saida = ?, evento = ? WHERE id = ?', (hora_entrada, hora_saida, data, funcionario, evento, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Ponto atualizado com sucesso!'})

@app.route('/ponto/<int:id>/delete', methods=['DELETE'])
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


@app.route('/ponto/buscar')
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
def list_pontos():
    conn = get_db_connection()
    cursor = conn.cursor()

    pontos = []
    
    try:
        if request.method == 'POST':
            data = request.json  # Recebe JSON corretamente
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



@app.route('/usuario', methods=['POST'])
def add_usuario():
    data = request.json
    nome = data.get('nome')
    senha = data.get('senha')

    if not nome or not senha:
        return jsonify({"error":"Nome e senha sao obrigatorios"}), 400
    
    if senha.strip() == '':
        return jsonify({"error":"Senha nao pode ser vazia"}), 400
    
    try:
        hashed_password = generate_password_hash(senha)
    except Exception as e:
        return jsonify({"error": f"Erro ao criptografar a senha: {e}"}), 500
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO usuario (nome, senha) VALUES (?, ?)', (nome, hashed_password))
        conn.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso!"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao cadastrar o usuario: {e}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/usuario/<int:id>', methods=['GET','PUT'])
def edit_usuario(id):
    data = request.json
    nome = data.get('nome')
    senha = data.get('senha')

    if not nome or not senha:
        return jsonify({"error": "Nome e senha sao obrigatorios"}), 400
    
    hashed_password = generate_password_hash(senha)

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'PUT':
        nome = request.form['nome']
        senha = request.form['senha']

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

@app.route('/usuario/delete/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('delete from usuario where id = ?', (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Usuario deletado com sucesso!"})

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuario')
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    usuarios_json = [{"id": u['id'], "nome": u['nome']} for u in usuarios]

    return jsonify({"usuarios": usuarios_json})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
