from flask import Flask, Response, redirect, request, jsonify, render_template, url_for, session, flash
from flask_cors import CORS
from flask_socketio import SocketIO
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*")

app.jinja_env.cache = None

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
        descricao = request.form.get('descricao')

        if not descricao:
            return render_template('add_departamento.html', mensagem="Dados incompletos")
        try:

            response = requests.post(f"{api_url}/departamento", json={"descricao": descricao})
            
            print("Resposta da API:", response.status_code, response.text)

            if response.status_code == 200 or response.status_code == 201:
                return redirect(url_for('list_departamentos'))
            else:
                return render_template('add_departamento.html', mensagem="Erro ao adicionar o departamento")
        except requests.exceptions.RequestException as e:
            return render_template('error.html', mensagem=f"Erro de conexão com a API: {str(e)}"), 500
        
    return render_template('add_departamento.html')


@app.route('/departamento/<int:id>', methods=['GET', 'POST'])
def edit_departamento(id):
    if request.method == 'POST' and request.form.get('_method') == 'PUT':
        descricao = request.form.get('descricao')  

        if not descricao:
            return render_template('edit_departamento.html', message='Dados incompletos'), 400

        response = requests.put(f"{api_url}/departamento/{id}", json={"descricao": descricao})

        if response.status_code == 200 or response.status_code == 201:
            departamento = requests.get(f"{api_url}/departamento/{id}").json()
            #return redirect(url_for('list_departamentos')), 200
            return render_template('edit_departamento.html', message='Departamento atualizado com sucesso!', departamento=departamento), 200
        else:
            return render_template('edit_departamento.html', message='Erro ao atualizar departamento'), response.status_code

    response = requests.get(f"{api_url}/departamento/{id}")
    
    if response.status_code != 200:
        return render_template('edit_departamento.html', message='Departamento não encontrado'), 404

    departamento = response.json()  
    
    return render_template('edit_departamento.html', departamento=departamento)  

@app.route('/departamento/<int:id>/delete', methods=['POST'])
def delete_departamento(id):
    try:
        response = requests.get(f"{api_url}/departamento/{id}")
        if response.status_code != 200:
            return render_template('error.html', message='Departamento não encontrado'), 404

        response = requests.post(f"{api_url}/departamento/{id}/delete")

        if response.status_code == 200 or response.status_code == 201:
            return redirect(url_for('list_departamentos'))
        else:
            return render_template('error.html', message=f'Erro ao deletar departamento: {response.text}'), response.status_code

    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=f'Erro de conexão com a API: {str(e)}'), 500

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
            return render_template('add_funcao.html', mensagem="Funcao adicionada com sucesso!"), 200
        else:
            return render_template('add_funcao.html', mensagem="Erro ao adicionar o funcao"), 404

    return render_template('add_funcao.html')

@app.route('/funcao/<int:id>', methods=['GET', 'POST'])
def edit_funcao(id):
    if request.method == 'GET':
        response = requests.get(f"{api_url}/funcao/{id}")
        
        if response.status_code == 200:
            funcao = response.json().get('funcao', {})  
        
            if funcao:
                #return redirect(url_for('list_funcoes')), 200
                return render_template('edit_funcao.html', funcao=funcao), 200
            else:
                return render_template('edit_funcao.html', message='Função não encontrada', funcao=None), 404
        
        return render_template('error.html', message='Erro ao buscar a função'), 404

    elif request.method == 'POST':
        descricao = request.form.get('descricao')
        
        response = requests.put(f"{api_url}/funcao/{id}", json={'descricao': descricao})
        
        if response.status_code == 200:  
            funcao = response.json().get('funcao', {}) 
            return render_template('edit_funcao.html', message='Função atualizada com sucesso!', funcao=funcao), 200
        else:
            return render_template('edit_funcao.html', message=f'Erro ao atualizar função: {response.text}', funcao=None), 500

@app.route('/funcao/<int:id>/delete', methods=['POST'])
def delete_funcao(id):
    try:
        response = requests.get(f"{api_url}/funcao/{id}", headers={"Cache-Control": "no-cache"})
        
        if response.status_code != 200:
            return render_template('list_funcoes.html', message='Função não encontrada'), 404
        
        response = requests.delete(f"{api_url}/funcao/{id}/delete", headers={"Cache-Control": "no-cache"})
        
        if response.status_code == 204:
            #return redirect(url_for('list_funcoes')), 200
            return render_template('list_funcoes.html', message='Função deletada com sucesso!'), 200
        else:
            return render_template('list_funcoes.html', message='Erro ao deletar função'), response.status_code

    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=f'Erro de conexão com a API: {str(e)}'), 500

@app.route('/funcoes', methods=['GET'])
def list_funcoes():
    message = request.args.get('message')
    response = requests.get(f"{api_url}/funcoes")

    if response.status_code == 200:
        funcoes = response.json().get('funcoes', [])

        if isinstance(funcoes, dict) and 'funcoes' in funcoes:
            funcoes = funcoes['funcoes']

        return render_template('list_funcoes.html', funcoes=funcoes, message=message), 200
    else:
        return render_template('list_funcoes.html', funcoes=[], message='Tabela de funções vazia.'), 200
    
@app.route('/evento', methods=['GET', 'POST'])
def add_evento():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        descricao = request.form.get('descricao')

        # Verifica se a descrição foi preenchida
        if not descricao and not codigo:
            return render_template('add_evento.html', mensagem="Dados incompletos")

        # Envia os dados para a API no formato JSON
        response = requests.post(f"{api_url}/evento/novo", json={"codigo":codigo,"descricao": descricao})

        if response.status_code == 201:
            return render_template('list_eventos.html', mensagem="Departamento adicionado com sucesso!")
        else:
            return render_template('add_evento.html', mensagem="Erro ao adicionar o departamento")

    return render_template('add_evento.html')

@app.route('/evento/<int:id>', methods=['GET','POST'])
def edit_evento(id):
    if request.method == 'GET':
        response = requests.get(f"{api_url}/evento/{id}")
        
        if response.status_code == 200:
            evento = response.json().get('evento', {})  
        
            if evento:
                return render_template('edit_evento.html', evento=evento), 200
            else:
                return render_template('edit_evento.html', message='evento não encontrado', evento=[]), 404
        
        return render_template('error.html', message='Erro ao buscar a evento'), 404

    elif request.method == 'POST':
        codigo = request.form.get('codigo')
        descricao = request.form.get('descricao')
        
        response = requests.put(f"{api_url}/evento/{id}", json={'codigo':codigo,'descricao': descricao})
        
        if response.status_code == 200:  
            evento = response.json().get('evento', {}) 
            return render_template('edit_evento.html', message='evento atualizado com sucesso!', evento=evento), 200
        else:
            return render_template('edit_evento.html', message=f'Erro ao atualizar evento: {response.text}', evento=None), 500

    
@app.route('/evento/<int:id>/delete', methods=['POST'])
def delete_evento(id):
    try:
        response = requests.get(f"{api_url}/evento/{id}", headers={"Cache-Control": "no-cache"})
        
        if response.status_code != 200:
            return render_template('list_eventos.html', message='evento não encontrado'), 404
        
        response = requests.delete(f"{api_url}/evento/{id}", headers={"Cache-Control": "no-cache"})
        
        if response.status_code == 204:
            return render_template('list_eventos.html', message='evento deletada com sucesso!'), 200
        else:
            return render_template('list_eventos.html', message='Erro ao deletar evento'), response.status_code

    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=f'Erro de conexão com a API: {str(e)}'), 500

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

        if isinstance(eventos, dict) and 'eventos' in eventos:
            eventos = eventos['eventos']

        return render_template('list_eventos.html', eventos=eventos)
    else:
        return render_template('message.html', message='Nenhum evento encontrado'), 200


@app.route('/ponto', methods=['GET', 'POST'])
def add_ponto():
    if request.method == 'POST':
        # Corrigindo para capturar dados do formulário
        hora_entrada = request.form.get('hora_entrada')
        hora_saida = request.form.get('hora_saida')
        data_ponto = request.form.get('data')
        nome_funcionario = request.form.get('funcionario')
        evento = request.form.get('evento')

        # Verifica se todos os campos estão preenchidos
        if not all([hora_entrada, hora_saida, data_ponto, nome_funcionario, evento]):
            return render_template('error.html', message='Dados incompletos'), 400

        # Log para depuração
        print("Dados enviados para API:", {
            'hora_entrada': hora_entrada,
            'hora_saida': hora_saida,
            'data': data_ponto,
            'funcionario': nome_funcionario,
            'evento': evento
        })

        # Envia os dados para a API
        response = requests.post(f"{api_url}/ponto", json={
            'hora_entrada': hora_entrada,
            'hora_saida': hora_saida,
            'data': data_ponto,
            'funcionario': nome_funcionario,
            'evento': evento
        })

        print("Resposta da API:", response.status_code, response.text)  # Log da resposta da API

        if response.status_code >= 200 and response.status_code <= 205:
            return render_template('list_pontos.html')
        else:
            return render_template('error.html', message=f'Erro ao registrar ponto: {response.text}'), 500

    return render_template('add_ponto.html')



@app.route('/ponto/<int:id>', methods=['GET', 'POST'])
def edit_ponto(id):
    if request.method == 'GET':
        response = requests.get(f"{api_url}/ponto/{id}")
        
        if response.status_code == 200:
            data = response.json()
            print("Dados recebidos da API:", data)

            pontos = data.get('pontos', [])
            if pontos:
                ponto = pontos[0]
            else:
                return render_template('error.html', message='Ponto não encontrado'), 404

            return render_template('edit_ponto.html', ponto=ponto)

        return render_template('error.html', message='Erro ao buscar o ponto'), 404

    elif request.method == 'POST':
        # Recebe os dados editados do formulário
        hora_entrada = request.form.get('hora_entrada')
        hora_saida = request.form.get('hora_saida')
        data_ponto = request.form.get('data')
        funcionario = request.form.get('funcionario')
        evento = request.form.get('evento')

        # 🔍 Log dos valores recebidos antes de enviar para API
        print("Dados enviados para atualização:", {
            'hora_entrada': hora_entrada,
            'hora_saida': hora_saida,
            'data': data_ponto,
            'funcionario': funcionario,
            'evento': evento
        })

        # Atualiza via API
        response = requests.put(f"{api_url}/ponto/{id}", json={
            'hora_entrada': hora_entrada,
            'hora_saida': hora_saida,
            'data': data_ponto,
            'funcionario': funcionario,
            'evento': evento
        })

        print("Resposta da API:", response.status_code, response.text)  # 🔍 Log da resposta da API

        if response.status_code == 200:
            return render_template('list_pontos.html', message='Ponto atualizado com sucesso!')
        else:
            return render_template('error.html', message=f'Erro ao atualizar ponto: {response.text}'), 500

@app.route('/ponto/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_ponto(id):
    response = requests.delete(f"{api_url}/ponto/{id}")

    if response.status_code == 200:
        return render_template('success.html', message='Ponto deletado com sucesso!')
    else:
        return render_template('error.html', message='Erro ao deletar ponto'), 500

@app.route('/pontos', methods=['GET'])
def list_pontos():
    response = requests.get(f"{api_url}/pontos")
    # print(response)

    if response.status_code == 200:
        pontos = response.json()

        # Se os dados vierem dentro de uma chave 'pontos', acessar corretamente:
        if isinstance(pontos, dict) and 'pontos' in pontos:
            pontos = pontos['pontos']
        return render_template('list_pontos.html', pontos=pontos)
    else:
        return render_template('message.html', message='Nenhum ponto encontrado'), 200

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
        if not nome or not senha:
            return render_template('add_usuario.html', mensagem="Dados incompletos")
    
        # Envia os dados para a API no formato JSON
        response = requests.post(f"{api_url}/usuario", json={"nome": nome, "senha":senha})

        if response.status_code == 201:
            return render_template('list_usuarios.html', mensagem="Usuario adicionado com sucesso!")
        else:
            return render_template('add_usuario.html', mensagem="Erro ao adicionar o usuario")

    return render_template('add_usuario.html')

@app.route('/usuarios', methods=['GET'])
def list_usuarios():
    response = requests.get(f"{api_url}/usuarios")

    if response.status_code == 200:
        usuarios = response.json()

        if isinstance(usuarios, dict) and 'usuarios' in usuarios:
            usuarios = usuarios['usuarios']

        return render_template('list_usuarios.html', usuarios=usuarios)
    else:
        return render_template('list_usuarios.html', message='Nenhum usuário encontrado'), 200

@app.route('/usuario/<int:id>', methods=['GET','POST'])
# @login_required
def edit_usuario(id):
    if request.method == 'GET':
        response = requests.get(f"{api_url}/usuario/{id}")

        if response.status_code == 200:
            usuario = response.json().get('usuario', {})
            return render_template('edit_usuario.html', usuario=usuario)
        else:
            return render_template('error.html', message="Usuario nao encontrado")
    
    elif request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            return render_template('edit_usuario.html', message="Nome e senha obrigatorios!")
        

        response = requests.put(f"{api_url}/usuario/{id}", json={'nome': nome, 'senha': senha})

        if response.status_code == 200:
            return render_template('list_usuarios.html', message='Usuario atualizado com sucesso!')
        else:
            return render_template('error.html', message='Erro ao atualizar usuario'), 500

@app.route('/usuario/delete/<int:id>', methods=['POST'])
# @login_required
def delete_usuario(id):
    response = requests.delete(f"{api_url}/usuario/{id}")

    if response.status_code == 200:
        flash('Usuário deletado com sucesso!', 'success')
        return redirect(url_for('list_usuarios'))
    else:
        flash('Erro ao deletar usuário!', 'danger')
        return redirect(url_for('list_usuarios'))

@app.route('/importar_ponto', methods=['GET','POST'])
def importar_ponto_frontend():
    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            return render_template('importar_ponto.html', message='Nenhum arquivo selecionado')
        
        response = requests.post(f"{api_url}/importar_ponto", files={'file': file })

        if response.status_code == 201:
            return render_template('importar_ponto.html', message='Arquivo importado com sucesso')
        else:
            return render_template('importar_ponto.html', message=f'Erro na importacao: {response.json().get("error", "Erro desconhecido")}')
        
    return render_template('importar_ponto.html')

@app.route('/escala', methods=['GET', 'POST'])
def add_escala():
    if request.method == 'POST':
        descricao = request.form.get('descricao')

        if not descricao:
            return render_template('add_escala.html', mensagem="Dados incompletos")
        try:

            response = requests.post(f"{api_url}/escala", json={"descricao": descricao})
            
            print("Resposta da API:", response.status_code, response.text)

            if response.status_code == 200 or response.status_code == 201:
                return redirect(url_for('list_escalas'))
            else:
                return render_template('add_escala.html', mensagem="Erro ao adicionar a escala")
        except requests.exceptions.RequestException as e:
            return render_template('error.html', mensagem=f"Erro de conexão com a API: {str(e)}"), 500
        
    return render_template('add_escala.html')


@app.route('/escala/<int:id>', methods=['GET', 'POST'])
def edit_escala(id):
    if request.method == 'POST' and request.form.get('_method') == 'PUT':
        descricao = request.form.get('descricao')  

        if not descricao:
            return render_template('edit_escala.html', message='Dados incompletos'), 400

        response = requests.put(f"{api_url}/escala/{id}", json={"descricao": descricao})

        if response.status_code == 200 or response.status_code == 201:
            escala = requests.get(f"{api_url}/escala/{id}").json()
            #return redirect(url_for('list_escalas')), 200
            return render_template('edit_escala.html', message='escala atualizada com sucesso!', escala=escala), 200
        else:
            return render_template('edit_escala.html', message='Erro ao atualizar escala'), response.status_code

    response = requests.get(f"{api_url}/escala/{id}")
    
    if response.status_code != 200:
        return render_template('edit_escala.html', message='escala não encontrada'), 404

    escala = response.json()  
    
    return render_template('edit_escala.html', escala=escala)  

@app.route('/escala/<int:id>/delete', methods=['POST'])
def delete_escala(id):
    try:
        response = requests.get(f"{api_url}/escala/{id}")
        if response.status_code != 200:
            return render_template('error.html', message='escala não encontrada'), 404

        response = requests.post(f"{api_url}/escala/{id}/delete")

        if response.status_code == 200 or response.status_code == 201:
            return redirect(url_for('list_escalas'))
        else:
            return render_template('error.html', message=f'Erro ao deletar escala: {response.text}'), response.status_code

    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=f'Erro de conexão com a API: {str(e)}'), 500

@app.route('/escala/<int:id>', methods=['GET'])
def view_escala(id):
    response = requests.get(f"{api_url}/escala/{id}")

    if response.status_code == 200:
        escala = response.json()
        return render_template('view_escala.html', escala=escala), 200
    else:
        return render_template('error.html', message='escala não encontrada'), 404

@app.route('/escalas', methods=['GET'])
def list_escalas():
    response = requests.get(f"{api_url}/escalas")

    if response.status_code == 200:
        try:
            data = response.json()  # JSON retorna um dicionário
            escalas = data.get("escalas", [])  # Pegamos apenas a lista dentro da chave "escalas"

            return render_template('lista_escalas.html', escalas=escalas), 200
        except ValueError:
            return render_template('error.html', message='Erro ao processar resposta da API.'), 500
    else:
        return render_template('message.html', message='Tabela de escalas vazia.'), 200

# endpoints para mensageria com socketio
BACKEND_URL = 'http://127.0.0.1:5000'  # URL do backend de mensageria
@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/conversas')
def proxy_conversas():
    resposta = requests.get(f'{BACKEND_URL}/conversas')
    return Response(resposta.content, status=resposta.status_code, content_type=resposta.headers['Content-Type'])

@app.route('/conversas', methods=['POST'])
def criar_conversa():
    # Encaminha a solicitação POST para o backend de mensagens
    response = requests.post(f'{BACKEND_URL}/conversas', json=request.get_json())
    return jsonify(response.json()), response.status_code

@app.route('/conversas', methods=['GET'])
def listar_conversas():
    # Encaminha a solicitação GET para o backend de mensagens
    response = requests.get(f'{BACKEND_URL}/conversas')
    return jsonify(response.json()), response.status_code

@app.route('/conversas/<int:conversa_id>/mensagens', methods=['GET'])
def listar_mensagens(conversa_id):
    # Encaminha a solicitação GET para o backend de mensagens
    response = requests.get(f'{BACKEND_URL}/conversas/{conversa_id}/mensagens')
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
