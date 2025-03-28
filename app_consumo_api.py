from flask import Flask, redirect, request, jsonify, render_template, url_for, session, flash
from flask_cors import CORS
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

CORS(app, resources={r"/*": {"origins": "*"}})

api_url = "http://localhost:5000"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
  
@app.route('/funcionarios', methods=['GET'])
# @login_required
def list_funcionarios():
    try:
        response = requests.get(f"{api_url}/funcionarios")
        if response.status_code == 200:
            data = response.json()
            funcionarios = data.get("funcionarios", [])  # Extrai a lista corretamente
        else:
            funcionarios = []
    except requests.exceptions.RequestException as e:
        print("Erro ao acessar a API:", e)
        funcionarios = []

    return render_template("lista_funcionarios.html", funcionarios=funcionarios)

@app.route('/funcionario/<int:matricula>', methods=['GET', 'POST'])
def get_funcionario(matricula):
    try:
        response = requests.get(f"{api_url}/funcionario/{matricula}")
        if response.status_code == 200:
            funcionario = response.json()
        else:
            funcionario = None
    except requests.exceptions.RequestException as e:
        print("Erro ao acessar a API:", e)
        funcionario = None

    if request.method == 'POST':
        # Atualizar funcionário
        data = {
            "nome": request.form.get("nome"),
            "funcao": request.form.get("funcao"),
            "data_inicio": request.form.get("data_inicio"),
            "data_termino": request.form.get("data_termino"),
            "departamento": request.form.get("departamento"),
            "gerente": request.form.get("gerente"),
            "endereco": request.form.get("endereco"),
            "telefone": request.form.get("telefone"),
            "cpf": request.form.get("cpf"),
            "rg": request.form.get("rg"),
            "banco": request.form.get("banco"),
            "agencia": request.form.get("agencia"),
            "conta_corrente": request.form.get("conta_corrente"),
        }

        try:
            update_response = requests.put(f"{api_url}/funcionario/{matricula}", json=data)
            if update_response.status_code == 200:
                return redirect(url_for('list_funcionarios'))  # Redireciona para a lista de funcionários após sucesso
            else:
                error_msg = update_response.json().get("error", "Erro ao atualizar funcionário.")
                return render_template("funcionario.html", funcionario=funcionario, error=error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na comunicação com a API: {e}"
            return render_template("funcionario.html", funcionario=funcionario, error=error_msg)

    return render_template("funcionario.html", funcionario=funcionario)

@app.route('/funcionario/<int:matricula>/delete', methods=['DELETE'])
def delete_funcionario(matricula):
    try:
        response = requests.delete(f"{api_url}/funcionario/{matricula}")
        if response.status_code == 200:
            message = "Funcionário removido com sucesso!"
        else:
            message = "Erro ao remover funcionário."
    except requests.exceptions.RequestException as e:
        print("Erro ao acessar a API:", e)
        message = "Erro na comunicação com a API."

    # Redireciona para a lista de funcionários após a remoção
    return redirect(url_for('list_funcionarios'))


@app.route('/funcionario', methods=['GET', 'POST'])
def add_funcionario():
    if request.method == 'POST':
        # Coleta dados do formulário
        data = {
            "nome": request.form.get("nome"),
            "funcao": request.form.get("funcao"),
            "data_inicio": request.form.get("data_inicio"),
            "data_termino": request.form.get("data_termino"),
            "departamento": request.form.get("departamento"),
            "gerente": request.form.get("gerente"),
            "endereco": request.form.get("endereco"),
            "telefone": request.form.get("telefone"),
            "cpf": request.form.get("cpf"),
            "rg": request.form.get("rg"),
            "banco": request.form.get("banco"),
            "agencia": request.form.get("agencia"),
            "conta_corrente": request.form.get("conta_corrente"),
        }

        try:
            response = requests.post(f"{api_url}/funcionario", json=data)
            if response.status_code == 201:
                return redirect(url_for('list_funcionarios'))  # Redireciona para a lista de funcionários após sucesso
            else:
                error_msg = response.json().get("error", "Erro ao adicionar funcionário.")
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na comunicação com a API: {e}"

        return render_template("add_funcionario.html", error=error_msg)

    return render_template("add_funcionario.html")


@app.route('/funcionario/edit/<int:matricula>', methods=['GET', 'POST'])
def update_funcionario(matricula):
    # Buscar dados do funcionário atual para preencher o formulário
    response = requests.get(f"{api_url}/funcionario/{matricula}")
    
    if response.status_code == 404:
        return render_template("funcionario.html", error="Funcionário não encontrado.")

    funcionario = response.json()

    if request.method == 'POST':
        data = {
            "nome": request.form.get("nome"),
            "funcao": request.form.get("funcao"),
            "data_inicio": request.form.get("data_inicio"),
            "data_termino": request.form.get("data_termino"),
            "departamento": request.form.get("departamento"),
            "gerente": request.form.get("gerente"),
            "endereco": request.form.get("endereco"),
            "telefone": request.form.get("telefone"),
            "cpf": request.form.get("cpf"),
            "rg": request.form.get("rg"),
            "banco": request.form.get("banco"),
            "agencia": request.form.get("agencia"),
            "conta_corrente": request.form.get("conta_corrente"),
        }

        try:
            update_response = requests.put(f"{api_url}/funcionario/{matricula}", json=data)
            if update_response.status_code == 200:
                return redirect(url_for('list_funcionarios'))  # Redireciona para a lista de funcionários após sucesso
            else:
                error_msg = update_response.json().get("error", "Erro ao atualizar funcionário.")
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na comunicação com a API: {e}"

        return render_template("funcionario.html", funcionario=funcionario, error=error_msg)

    return render_template("funcionario.html", funcionario=funcionario)

@app.route('/endereco', methods=['GET', 'POST'])
def add_endereco():
    if request.method == 'POST':
        # Recebe os dados JSON do corpo da requisição
        data = request.json
        rua = data.get('rua')
        bairro = data.get('bairro')
        cidade = data.get('cidade')
        pais = data.get('pais')

        # Verifica se todos os campos necessários estão preenchidos
        if not all([rua, bairro, cidade, pais]):
            return render_template('add_endereco.html', mensagem="Dados incompletos")

        # Envia os dados para o backend (API)
        response = requests.post(f"{api_url}/endereco", json=data)

        if response.status_code == 201:
            return render_template('lista_enderecos.html', mensagem="Endereço adicionado com sucesso!")
        else:
            return render_template('add_endereco.html', mensagem="Erro ao adicionar o endereço")
    
    return render_template('add_endereco.html')


@app.route('/endereco/<int:id>', methods=['GET', 'POST'])
def edit_endereco(id):
    # Obtém os dados do endereço do backend
    response = requests.get(f"{api_url}/endereco/{id}")

    if response.status_code != 200:
        return render_template('erro.html', mensagem="Endereço não encontrado")

    endereco = response.json()

    if request.method == 'POST':
        # Coleta os dados atualizados
        data = request.json
        rua = data.get('rua')
        bairro = data.get('bairro')
        cidade = data.get('cidade')
        pais = data.get('pais')

        # Envia os dados para atualizar o endereço
        response = requests.put(f"{api_url}/endereco/{id}", json=data)

        if response.status_code == 200:
            return render_template('sucesso.html', mensagem="Endereço atualizado com sucesso!")
        else:
            return render_template('erro.html', mensagem="Erro ao atualizar o endereço")
    
    return render_template('endereco.html', endereco=endereco)


@app.route('/endereco/<int:id>/delete', methods=['POST'])
def delete_endereco(id):
    # Envia uma solicitação DELETE para a API
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
    return render_template('lista_enderecos.html', enderecos=enderecos)

@app.route('/departamento', methods=['GET', 'POST'])
def add_departamento():
    if request.method == 'POST':
        # Recebe os dados do formulário
        descricao = request.form.get('descricao')

        # Verifica se a descrição foi preenchida
        if not descricao:
            return render_template('add_departamento.html', mensagem="Dados incompletos")

        # Envia os dados para a API no formato JSON
        response = requests.post(f"{api_url}/departamentos", json={"descricao": descricao})

        if response.status_code == 201:
            return render_template('lista_departamentos.html', mensagem="Departamento adicionado com sucesso!")
        else:
            return render_template('add_departamento.html', mensagem="Erro ao adicionar o departamento")

    return render_template('add_departamento.html')


@app.route('/departamento/<int:id>', methods=['GET', 'POST'])
def edit_departamento(id):
    if request.method == 'POST':
        descricao = request.form.get('descricao')  # Pegando a nova descrição

        if not descricao:
            return render_template('error.html', message='Dados incompletos'), 400

        response = requests.put(f"{api_url}/departamento/{id}", json={"descricao": descricao})

        if response.status_code == 201:
            return render_template('success.html', message='Departamento atualizado com sucesso!'), 201
        else:
            return render_template('error.html', message='Erro ao atualizar departamento'), response.status_code

    response = requests.get(f"{api_url}/departamento/{id}")
    if response.status_code != 200:
        return render_template('error.html', message='Departamento não encontrado'), 404

    departamento = response.json()
    return render_template('edit_departamento.html', departamento=departamento)  # Página de edição com o departamento

@app.route('/departamento/<int:id>/delete', methods=['POST'])
def delete_departamento(id):
    response = requests.get(f"{api_url}/departamento/{id}")

    if response.status_code != 200:
        return render_template('error.html', message='Departamento não encontrado'), 404

    response = requests.delete(f"{api_url}/departamento/{id}")

    if response.status_code == 200:
        return render_template('success.html', message='Departamento deletado com sucesso!'), 200
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

@app.route('/departamentos', methods=['GET'])
def list_departamentos():
    response = requests.get(f"{api_url}/departamentos")

    if response.status_code == 200:
        try:
            data = response.json()  # JSON retorna um dicionário
            departamentos = data.get("departamentos", [])  # Pegamos apenas a lista dentro da chave "departamentos"

            return render_template('lista_departamentos.html', departamentos=departamentos), 200
        except ValueError:
            return render_template('error.html', message='Erro ao processar resposta da API.'), 500
    else:
        return render_template('message.html', message='Tabela de departamentos vazia.'), 200

@app.route('/funcao', methods=['GET', 'POST'])
def add_funcao():
    if request.method == 'POST':
        # Recebe os dados do formulário
        descricao = request.form.get('descricao')

        # Verifica se a descrição foi preenchida
        if not descricao:
            return render_template('add_funcao.html', mensagem="Dados incompletos")

        # Envia os dados para a API no formato JSON
        response = requests.post(f"{api_url}/funcao", json={"descricao": descricao})

        if response.status_code == 201:
            return render_template('list_funcoes.html', mensagem="Departamento adicionado com sucesso!")
        else:
            return render_template('add_funcao.html', mensagem="Erro ao adicionar o departamento")

    return render_template('add_funcao.html')

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

@app.route('/evento', methods=['GET', 'POST'])
def add_evento():
    if request.method == 'POST':
        # Recebe os dados do formulário
        descricao = request.form.get('descricao')

        # Verifica se a descrição foi preenchida
        if not descricao:
            return render_template('add_evento.html', mensagem="Dados incompletos")

        # Envia os dados para a API no formato JSON
        response = requests.post(f"{api_url}/evento", json={"descricao": descricao})

        if response.status_code == 201:
            return render_template('list_eventos.html', mensagem="Departamento adicionado com sucesso!")
        else:
            return render_template('add_evento.html', mensagem="Erro ao adicionar o departamento")

    return render_template('add_evento.html')

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

    return render_template('add_ponto.html')


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

@app.route('/pontos', methods=['GET'])
def listar_pontos():
    response = requests.get(f"{api_url}/pontos")

    if response.status_code == 200:
        pontos = response.json()
        return render_template('list_pontos.html', pontos=pontos)
    else:
        return render_template('error.html', message='Nenhum ponto encontrado'), 200

@app.route('/ponto/<int:id>', methods=['GET'])
def view_ponto(id):
    response = requests.get(f"{api_url}/pontos/{id}")

    if response.status_code == 200:
        ponto = response.json()
        return render_template('view_ponto.html', ponto=ponto)
    else:
        return render_template('error.html', message='Ponto não encontrado'), 404

@app.route('/usuario', methods=['GET', 'POST'])
def add_usuario():
    if request.method == 'POST':
        # Recebe os dados do formulário
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        # Verifica se o nome e senha foram preenchidos
        if not nome or senha:
            return render_template('add_usuario.html', mensagem="Dados incompletos")

        try:
            hashed_password = generate_password_hash(senha)
        except Exception as e:
            return render_template('add_usuario.html', mensagem="Erro ao encriptografar senha!")

    
        # Envia os dados para a API no formato JSON
        response = requests.post(f"{api_url}/usuario", json={"nome": nome, "senha":hashed_password})

        if response.status_code == 201:
            return render_template('listar_usuarios.html', mensagem="Departamento adicionado com sucesso!")
        else:
            return render_template('add_usuario.html', mensagem="Erro ao adicionar o departamento")

    return render_template('add_usuario.html')

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    response = requests.get(f"{api_url}/usuarios")

    if response.status_code == 200:
        usuarios = response.json()
        return render_template('list_usuarios.html', usuarios=usuarios)
    else:
        return render_template('list_usuarios.html', message='Nenhum usuário encontrado'), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
