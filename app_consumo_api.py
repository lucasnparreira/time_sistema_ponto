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
    data = request.json
    descricao = data.get('descricao')

    if not descricao:
        return render_template('error.html', message='Dados incompletos'), 400

    response = requests.post(f"{api_url}/departamento", json={"descricao": descricao})
    
    if response.status_code == 201:
        return render_template('success.html', message='Departamento criado com sucesso!'), 201
    else:
        return render_template('error.html', message='Erro ao criar departamento'), response.status_code

@app.route('/departamento/<int:id>', methods=['PUT'])
def edit_departamento(id):
    data = request.json
    descricao = data.get('descricao')

    response = requests.get(f"{api_url}/departamento/{id}")

    if response.status_code != 200:
        return render_template('error.html', message='Departamento não encontrado'), 404

    response = requests.put(f"{api_url}/departamento/{id}", json={"descricao": descricao})
    
    if response.status_code == 201:
        return render_template('success.html', message='Departamento atualizado com sucesso!'), 201
    else:
        return render_template('error.html', message='Erro ao atualizar departamento'), response.status_code

@app.route('/departamento/<int:id>/delete', methods=['POST'])
def delete_departamento(id):
    response = requests.get(f"{api_url}/departamento/{id}")

    if response.status_code != 200:
        return render_template('error.html', message='Departamento não encontrado'), 404

    response = requests.delete(f"{api_url}/departamento/{id}")

    if response.status_code == 201:
        return render_template('success.html', message='Departamento deletado com sucesso!'), 201
    else:
        return render_template('error.html', message='Erro ao deletar departamento'), response.status_code

@app.route('/departamento/<int:id>', methods=['GET'])
def view_departamento(id):
    response = requests.get(f"{api_url}/departamento/{id}")

    if response.status_code == 200:
        departamento = response.json()
        return render_template('view_departamento.html', departamento=departamento), 200
    else:
        return render_template('error.html', message='Departamento não encontrado'), 404

@app.route('/departamentos')
def list_departamentos():
    response = requests.get(f"{api_url}/departamentos")

    if response.status_code == 200:
        departamentos = response.json()
        return render_template('list_departamentos.html', departamentos=departamentos), 200
    else:
        return render_template('message.html', message='Tabela de departamentos vazia.'), 200

@app.route('/funcao', methods=['POST'])
def add_funcao():
    data = request.json
    descricao = data.get('descricao')

    if not descricao:
        return render_template('error.html', message='Dados incompletos'), 400

    response = requests.post(f"{api_url}/funcao", json={"descricao": descricao})

    if response.status_code == 201:
        return render_template('success.html', message='Função criada com sucesso!'), 201
    else:
        return render_template('error.html', message='Erro ao criar função'), response.status_code

@app.route('/funcao/<int:id>', methods=['PUT'])
def edit_funcao(id):
    data = request.json
    descricao = data.get('descricao')

    response = requests.get(f"{api_url}/funcao/{id}")

    if response.status_code != 200:
        return render_template('error.html', message='Função não encontrada'), 404

    response = requests.put(f"{api_url}/funcao/{id}", json={"descricao": descricao})

    if response.status_code == 201:
        return render_template('success.html', message='Função atualizada com sucesso!'), 201
    else:
        return render_template('error.html', message='Erro ao atualizar função'), response.status_code

@app.route('/funcao/<int:id>/delete', methods=['POST'])
def delete_funcao(id):
    response = requests.get(f"{api_url}/funcao/{id}")

    if response.status_code != 200:
        return render_template('error.html', message='Função não encontrada'), 404

    response = requests.delete(f"{api_url}/funcao/{id}")

    if response.status_code == 201:
        return render_template('success.html', message='Função deletada com sucesso!'), 201
    else:
        return render_template('error.html', message='Erro ao deletar função'), response.status_code

@app.route('/funcao/<int:id>', methods=['GET'])
def view_funcao(id):
    response = requests.get(f"{api_url}/funcao/{id}")

    if response.status_code == 200:
        funcao = response.json()
        return render_template('view_funcao.html', funcao=funcao), 200
    else:
        return render_template('error.html', message='Função não encontrada'), 404

@app.route('/funcoes')
def list_funcoes():
    response = requests.get(f"{api_url}/funcoes")

    if response.status_code == 200:
        funcoes = response.json()
        return render_template('list_funcoes.html', funcoes=funcoes), 200
    else:
        return render_template('message.html', message='Tabela de funções vazia.'), 200

@app.route('/evento/novo', methods=['GET','POST'])
def add_evento():
    if request.method == 'POST':
        data = request.json
        codigo = data.get('codigo')
        descricao = data.get('descricao')

        if not descricao:
            return render_template('error.html', message='Dados incompletos'), 400

        # Fazendo a requisição POST para a nova API
        response = requests.post(f"{api_url}/eventos", json={'codigo': codigo, 'descricao': descricao})

        if response.status_code == 201:
            return render_template('success.html', message='Evento criado com sucesso!')
        else:
            return render_template('error.html', message='Erro ao criar evento'), 500

    return render_template('form_evento.html')


@app.route('/evento/<int:id>', methods=['PUT'])
def edit_evento(id):
    data = request.json
    codigo = data.get('codigo')
    descricao = data.get('descricao')

    response = requests.put(f"{api_url}/eventos/{id}", json={'codigo': codigo, 'descricao': descricao})

    if response.status_code == 200:
        return render_template('success.html', message='Evento atualizado com sucesso!')
    else:
        return render_template('error.html', message='Erro ao atualizar evento'), 500


@app.route('/evento/<int:id>/delete', methods=['POST'])
def delete_evento(id):
    response = requests.delete(f"{api_url}/eventos/{id}")

    if response.status_code == 200:
        return render_template('success.html', message='Evento deletado com sucesso!')
    else:
        return render_template('error.html', message='Erro ao deletar evento'), 500


@app.route('/evento/<int:id>', methods=['GET'])
def view_evento(id):
    response = requests.get(f"{api_url}/eventos/{id}")

    if response.status_code == 200:
        evento = response.json()
        return render_template('view_evento.html', evento=evento)
    else:
        return render_template('error.html', message='Evento não encontrado'), 404


@app.route('/eventos')
def list_eventos():
    response = requests.get(f"{api_url}/eventos")

    if response.status_code == 200:
        eventos = response.json()
        return render_template('list_eventos.html', eventos=eventos)
    else:
        return render_template('message.html', message='Nenhum evento encontrado'), 200


@app.route('/ponto', methods=['GET', 'POST'])
def add_ponto():
    if request.method == 'POST':
        data = request.json
        hora_entrada = data.get('hora_entrada')
        hora_saida = data.get('hora_saida')
        data_ponto = data.get('data')
        nome_funcionario = data.get('funcionario') 
        evento = data.get('evento')

        if not all([hora_entrada, hora_saida, data_ponto, nome_funcionario, evento]):
                return render_template('error.html', message='Dados incompletos'), 404

        response = requests.post(f"{api_url}/pontos", json={
            'hora_entrada': hora_entrada,
            'hora_saida': hora_saida,
            'data': data_ponto,
            'funcionario': nome_funcionario,
            'evento': evento
        })

        if response.status_code == 201:
            return render_template('success.html', message='Ponto registrado com sucesso!')
        else:
            return render_template('error.html', message='Erro ao registrar ponto'), 500

    return render_template('form_ponto.html')


@app.route('/ponto/<int:id>', methods=['PUT'])
def edit_ponto(id):
    data = request.json
    hora_entrada = data.get('hora_entrada')
    hora_saida = data.get('hora_saida')
    data = data.get('data')
    funcionario = data.get('funcionario')
    evento = data.get('evento')

    response = requests.put(f"{api_url}/pontos/{id}", json={
        'hora_entrada': hora_entrada,
        'hora_saida': hora_saida,
        'data': data,
        'funcionario': funcionario,
        'evento': evento
    })

    if response.status_code == 200:
        return render_template('success.html', message='Ponto atualizado com sucesso!')
    else:
        return render_template('error.html', message='Erro ao atualizar ponto'), 500


@app.route('/ponto/<int:id>/delete', methods=['DELETE'])
def delete_ponto(id):
    response = requests.delete(f"{api_url}/pontos/{id}")

    if response.status_code == 200:
        return render_template('success.html', message='Ponto deletado com sucesso!')
    else:
        return render_template('error.html', message='Erro ao deletar ponto'), 500


@app.route('/ponto/<int:id>', methods=['GET'])
def view_ponto(id):
    response = requests.get(f"{api_url}/pontos/{id}")

    if response.status_code == 200:
        ponto = response.json()
        return render_template('view_ponto.html', ponto=ponto)
    else:
        return render_template('error.html', message='Ponto não encontrado'), 404


@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    response = requests.get(f"{api_url}/usuarios")

    if response.status_code == 200:
        usuarios = response.json()
        return render_template('list_usuarios.html', usuarios=usuarios)
    else:
        return render_template('error.html', message='Nenhum usuário encontrado'), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
