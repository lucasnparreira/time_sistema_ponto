from flask import Flask, redirect, request, jsonify, render_template, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

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

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/funcionario', methods=['POST', 'GET'])
@login_required
def add_funcionario():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Verifica se o formulário inclui uma busca
        search = request.form.get('search')
        if search:
            # Tenta buscar o funcionário pelo nome ou matrícula
            cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ? OR nome = ?', (search, search))
            funcionario = cursor.fetchone()

            if funcionario:
                conn.close()
                return render_template('funcionario.html', funcionario=funcionario)
            else:
                conn.close()
                return render_template('funcionario.html', message='Funcionário não encontrado.')

        data = request.form 
        
        print("Dados recebidos:", data)
        matricula = data.get('matricula')
        nome = data.get('nome')
        if not matricula or not nome:
            return jsonify("Matrícula e nome são obrigatórios.")
        
        # Executa a inserção no banco
        query = '''
            INSERT INTO FUNCIONARIO (matricula, nome, funcao, data_inicio, data_termino, 
                                    departamento, gerente, endereco, telefone, cpf, rg, banco, agencia, conta_corrente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        values = (
            data.get('matricula'), data.get('nome'), data.get('funcao'), data.get('data_inicio'), data.get('data_termino'),
            data.get('departamento'), data.get('gerente'), data.get('endereco'), data.get('telefone'), data.get('cpf'), 
            data.get('rg'), data.get('banco'), data.get('agencia'), data.get('conta_corrente')
        )

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('funcionario.html', message='Funcionário cadastrado com sucesso!')

    return render_template('funcionario.html')


@app.route('/funcionario/<int:matricula>', methods=['DELETE'])
@login_required
def delete_funcionario(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('select * from funcionario where matricula = ?', (matricula,) )
    funcionario = cursor.fetchone()

    if funcionario is None:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    cursor.execute('DELETE FROM FUNCIONARIO WHERE matricula = ?', (matricula,))
    conn.commit()

    cursor.close()
    conn.close()
  
    return jsonify({'message': 'Funcionário deletado com sucesso'}), 200


@app.route('/funcionario/<int:matricula>', methods=['PUT'])
@login_required
def update_funcionario(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o funcionário existe
    cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ?', (matricula,))
    funcionario = cursor.fetchone()

    if funcionario is None:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    # Capturar os dados da requisição
    data = request.get_json()

    # Atualizar os dados do funcionário no banco
    query = '''
        UPDATE FUNCIONARIO
        SET nome = ?, funcao = ?, data_inicio = ?, data_termino = ?, 
            departamento = ?, gerente = ?, endereco = ?, telefone = ?, 
            cpf = ?, rg = ?, banco = ?, agencia = ?, conta_corrente = ?
        WHERE matricula = ?
    '''
    values = (
        data['nome'], data['funcao'], data['data_inicio'], data.get('data_termino'),
        data['departamento'], data.get('gerente'), data.get('endereco'), data['telefone'],
        data['cpf'], data['rg'], data['banco'], data['agencia'], data['conta_corrente'], matricula
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Funcionário atualizado com sucesso'}), 200


@app.route('/funcionario/<int:matricula>', methods=['GET'])
@login_required
def get_funcionario(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar o funcionário pela matrícula
    cursor.execute('SELECT * FROM FUNCIONARIO WHERE matricula = ?', (matricula,))
    funcionario = cursor.fetchone()

    if funcionario is None:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Funcionário não encontrado'}), 404

    # Extrair os dados do funcionário
    funcionario_data = {
        'matricula': funcionario['matricula'],
        'nome': funcionario['nome'],
        'funcao': funcionario['funcao'],
        'data_inicio': funcionario['data_inicio'],
        'data_termino': funcionario['data_termino'],
        'departamento': funcionario['departamento'],
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


@app.route('/funcionarios')
@login_required
def list_funcionarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM FUNCIONARIO')
    funcionarios = cursor.fetchall()
    conn.close()
    
    return render_template('lista_funcionarios.html', funcionarios=funcionarios)


@app.route('/endereco/novo', methods=['GET','POST'])
@login_required
def add_endereco():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        #data = request.get_json()
        rua = request.form.get('rua')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        pais = request.form.get('pais')

        if not all([rua, bairro, cidade, pais]):
            return jsonify({'error':'Dados incompletos'}), 404
        
        cursor.execute('INSERT INTO ENDERECO (rua, bairro, cidade, pais) VALUES (?, ?, ?, ?)', (rua, bairro, cidade, pais))
        conn.commit()
        conn.close()

        return redirect(url_for('list_enderecos'))
    
    return render_template('endereco.html', action='Cadastrar', endereco={})


@app.route('/endereco/<int:id>', methods=['POST'])
@login_required
def edit_endereco(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    #data = request.get_json()

    rua = request.form.get('rua')
    bairro = request.form.get('bairro')
    cidade = request.form.get('cidade')
    pais = request.form.get('pais')

    cursor.execute('SELECT * FROM ENDERECO WHERE id = ?', (id,))
    endereco = cursor.fetchone()

    if not endereco:
        return jsonify({'error': 'Endereço não encontrado'}), 404

    cursor.execute('UPDATE ENDERECO SET rua = ?, bairro = ?, cidade = ?, pais = ? WHERE id = ?', (rua, bairro, cidade, pais, id))
    conn.commit()
    conn.close()

    return redirect(url_for('list_enderecos'))


@app.route('/endereco/<int:id>', methods=['POST'])
@login_required
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

    return redirect(url_for('list_enderecos'))


@app.route('/endereco/<int:id>', methods=['GET'])
@login_required
def view_endereco(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ENDERECO WHERE id = ?', (id,))
    endereco = cursor.fetchone()
    conn.close()
    
    if endereco:
        return render_template('endereco.html', action='Atualizar', endereco=endereco)
    return redirect(url_for('list_enderecos'))


@app.route('/enderecos', methods=['GET'])
@login_required
def list_enderecos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ENDERECO')
    enderecos = cursor.fetchall()
    conn.close()
    
    return render_template('lista_enderecos.html', enderecos=enderecos)


@app.route('/departamento/novo', methods=['GET','POST'])
@login_required
def add_departamento():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        #data = request.get_json()
        descricao = request.form.get('descricao')

        if not all([descricao]):
            return jsonify({'error':'Dados incompletos'}), 404
        
        cursor.execute('INSERT INTO DEPARTAMENTO (descricao) VALUES (?)', (descricao,))
        conn.commit()
        conn.close()

        return redirect(url_for('list_departamentos'))
    
    return render_template('departamento.html', action='Cadastrar', departamento={})


@app.route('/departamento/<int:id>', methods=['POST'])
@login_required
def edit_departamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    #data = request.get_json()

    id = request.form.get('id')
    descricao = request.form.get('descricao')

    cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
    departamento = cursor.fetchone()

    if not departamento:
        return jsonify({'error': 'Departamento não encontrado'}), 404

    cursor.execute('UPDATE DEPARTAMENTO SET descricao = ? WHERE id = ?', (descricao, id))
    conn.commit()
    conn.close()

    return redirect(url_for('list_departamentos'))


@app.route('/departamento/<int:id>/delete', methods=['POST'])
@login_required
def delete_departamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o departamento existe
    cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
    departamento = cursor.fetchone()

    if not departamento:
        conn.close()
        return jsonify({'error': 'Departamento não encontrado'}), 404
    
    # Excluir o departamento
    cursor.execute('DELETE FROM DEPARTAMENTO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Redirecionar de volta para a lista de departamentos
    return redirect(url_for('list_departamentos'))



@app.route('/departamento/<int:id>', methods=['GET'])
@login_required
def view_departamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM DEPARTAMENTO WHERE id = ?', (id,))
    departamento = cursor.fetchone()
    conn.close()
    
    if departamento:
        return render_template('departamento.html', action='Atualizar', departamento=departamento)
    return redirect(url_for('list_departamentos'))


@app.route('/departamentos')
@login_required
def list_departamentos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM DEPARTAMENTO')
    departamentos = cursor.fetchall()
    conn.close()
    
    return render_template('lista_departamentos.html', departamentos=departamentos)


@app.route('/funcao/novo', methods=['GET','POST'])
@login_required
def add_funcao():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        #data = request.get_json()
        descricao = request.form.get('descricao')

        if not all([descricao]):
            return jsonify({'error':'Dados incompletos'}), 404
        
        cursor.execute('INSERT INTO FUNCAO (descricao) VALUES (?)', (descricao,))
        conn.commit()
        conn.close()

        return redirect(url_for('list_funcoes'))
    
    return render_template('funcao.html', action='Cadastrar', funcao={})

@app.route('/funcao/<int:id>', methods=['POST'])
@login_required
def edit_funcao(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    #data = request.get_json()

    id = request.form.get('id')
    descricao = request.form.get('descricao')

    cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
    departamento = cursor.fetchone()

    if not departamento:
        return jsonify({'error': 'Função não encontrada'}), 404

    cursor.execute('UPDATE FUNCAO SET descricao = ? WHERE id = ?', (descricao, id))
    conn.commit()
    conn.close()

    return redirect(url_for('list_funcoes'))


@app.route('/funcao/<int:id>/delete', methods=['POST'])
@login_required
def delete_funcao(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o departamento existe
    cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
    departamento = cursor.fetchone()

    if not departamento:
        conn.close()
        return jsonify({'error': 'função não encontrada'}), 404
    
    # Excluir o departamento
    cursor.execute('DELETE FROM FUNCAO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Redirecionar de volta para a lista de departamentos
    return redirect(url_for('list_funcoes'))



@app.route('/funcao/<int:id>', methods=['GET'])
@login_required
def view_funcao(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM FUNCAO WHERE id = ?', (id,))
    funcao = cursor.fetchone()
    conn.close()
    
    if funcao:
        return render_template('funcao.html', action='Atualizar', funcao=funcao)
    return redirect(url_for('list_funcoes'))


@app.route('/funcoes')
@login_required
def list_funcoes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM FUNCAO')
    funcoes = cursor.fetchall()
    conn.close()
    
    return render_template('lista_funcoes.html', funcoes=funcoes)


@app.route('/evento/novo', methods=['GET','POST'])
@login_required
def add_evento():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        #data = request.get_json()
        codigo = request.form.get('codigo')
        descricao = request.form.get('descricao')

        if not all([descricao]):
            return jsonify({'error':'Dados incompletos'}), 404
        
        cursor.execute('INSERT INTO EVENTO (codigo, descricao) VALUES (?, ?)', (codigo, descricao,))
        conn.commit()
        conn.close()

        return redirect(url_for('list_eventos'))
    
    return render_template('evento.html', action='Cadastrar', evento={})


@app.route('/evento/<int:id>', methods=['POST'])
@login_required
def edit_evento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    #data = request.get_json()

    id = request.form.get('id')
    codigo = request.form.get('codigo')
    descricao = request.form.get('descricao')

    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    evento = cursor.fetchone()

    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404

    cursor.execute('UPDATE EVENTO SET codigo = ?, descricao = ? WHERE id = ?', (codigo, descricao, id))
    conn.commit()
    conn.close()

    return redirect(url_for('list_eventos'))


@app.route('/evento/<int:id>/delete', methods=['POST'])
@login_required
def delete_evento(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o departamento existe
    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return jsonify({'error': 'Evento não encontrado'}), 404
    
    # Excluir o evento
    cursor.execute('DELETE FROM EVENTO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Redirecionar de volta para a lista de departamentos
    return redirect(url_for('list_eventos'))



@app.route('/evento/<int:id>', methods=['GET'])
@login_required
def view_evento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    evento = cursor.fetchone()
    conn.close()
    
    if evento:
        return render_template('evento.html', action='Atualizar', evento=evento)
    return redirect(url_for('list_eventos'))


@app.route('/eventos')
@login_required
def list_eventos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM EVENTO')
    eventos = cursor.fetchall()
    conn.close()
    
    return render_template('lista_eventos.html', eventos=eventos)



@app.route('/ponto/cadastro', methods=['GET','POST'])
@login_required
def add_ponto():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('select codigo, descricao from evento')
    eventos = cursor.fetchall()

    if request.method == 'POST':
        #data = request.get_json()
        hora_entrada = request.form.get('hora_entrada')
        hora_saida = request.form.get('hora_saida')
        data = request.form.get('data')
        funcionario = request.form.get('funcionario')
        evento = request.form.get('evento')

        if not all([hora_entrada, hora_saida, data, funcionario, evento]):
            return jsonify({'error':'Dados incompletos'}), 404
        
        cursor.execute('INSERT INTO PONTO (funcionario, data, hora_entrada, hora_saida, evento) VALUES (?, ?, ?, ?, ?)', (funcionario, data, hora_entrada, hora_saida, evento,))
        conn.commit()
        conn.close()

        return redirect(url_for('list_pontos'))
    
    conn.close()

    return render_template('ponto.html', action='Cadastrar', ponto={}, eventos=eventos)


@app.route('/ponto/<int:id>', methods=['POST'])
@login_required
def edit_ponto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    #data = request.get_json()

    id = request.form.get('id')
    hora_entrada = request.form.get('hora_entrada')
    hora_saida = request.form.get('hora_saida')
    data = request.form.get('data')
    funcionario = request.form.get('funcionario')
    evento = request.form.get('evento')

    cursor.execute('SELECT * FROM EVENTO WHERE id = ?', (id,))
    ponto = cursor.fetchone()

    if not ponto:
        return jsonify({'error': 'Ponto não encontrado'}), 404

    cursor.execute('UPDATE PONTO SET funcionario = ?, data = ?, hora_entrada = ?, hora_saida = ?, evento = ? WHERE id = ?', (hora_entrada, hora_saida, data, funcionario, evento, id))
    conn.commit()
    conn.close()

    return redirect(url_for('list_pontos'))


@app.route('/ponto/<int:id>/delete', methods=['POST'])
@login_required
def delete_ponto(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o ponto existe
    cursor.execute('SELECT * FROM PONTO WHERE id = ?', (id,))
    ponto = cursor.fetchone()

    if not ponto:
        conn.close()
        return jsonify({'error': 'Ponto não encontrado'}), 404
    
    # Excluir o ponto
    cursor.execute('DELETE FROM PONTO WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Redirecionar de volta para a lista de pontos
    return redirect(url_for('list_pontos'))



@app.route('/ponto/<int:id>', methods=['GET'])
@login_required
def view_ponto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM PONTO WHERE id = ?', (id,))
    ponto = cursor.fetchone()
    conn.close()
    
    if ponto:
        return render_template('ponto.html', action='Atualizar', ponto=ponto)
    return redirect(url_for('list_pontos'))


@app.route('/pontos')
@login_required
def list_pontos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT p.id, f.nome, p.data, p.hora_entrada, p.hora_saida, e.descricao FROM PONTO p JOIN EVENTO e ON p.evento = e.codigo JOIN FUNCIONARIO f ON p.funcionario = f.matricula')
    pontos = cursor.fetchall()
    conn.close()
    
    return render_template('lista_pontos.html', pontos=pontos)


@app.route('/usuario', methods=['GET','POST'])
@login_required
def add_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            flash("Nome e senha são obrigatórios", "danger")
            return redirect(url_for('add_usuario')) 

        if senha is None or senha.strip() == '':
            flash("Senha não pode ser vazia", "danger")
            return redirect(url_for('add_usuario'))  

        try:
            hashed_password = generate_password_hash(senha)
        except Exception as e:
            flash(f"Erro ao criptografar a senha: {e}", "danger")
            return redirect(url_for('add_usuario'))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO usuario (nome, senha) VALUES (?, ?)
            ''', (nome, hashed_password))

            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao cadastrar o usuário: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for('listar_usuarios')) 
    return render_template('add_usuario.html')


@app.route('/usuario/<int:id>', methods=['GET','POST'])
@login_required
def edit_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
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

        return redirect(url_for('listar_usuarios'))
    
    cursor.execute('select * from usuario where id = ?', (id,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('usuario_form.html',action='Atualizar', usuario=usuario)


@app.route('/usuario/delete/<int:id>', methods=['POST'])
@login_required
def delete_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('delete from usuario where id = ?', (id,))

    cursor.close()
    conn.close()

    return redirect(url_for('listar_usuarios'))


@app.route('/usuarios')
@login_required
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuario')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('listar_usuarios.html', usuarios=usuarios)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('select * from usuario where nome = ?', (nome,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario and check_password_hash(usuario['senha'], senha):
            session['user_id'] = usuario['id']
            session['user_nome'] = usuario['nome']
            return redirect(url_for('index'))
        else:
            flash('Usuario ou senha incorretos!', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
