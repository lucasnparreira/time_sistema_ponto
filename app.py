from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/funcionario', methods=['POST','GET'])
def add_funcionario():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        query = '''
            INSERT INTO FUNCIONARIO (matricula, nome, funcao, data_inicio, data_termino, 
                                    departamento, gerente, endereco, telefone, cpf, rg, banco, agencia, conta_corrente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        values = (
            data['matricula'], data['nome'], data['funcao'], data['data_inicio'], data.get('data_termino'),
            data['departamento'], data['gerente'], data.get('endereco'), data['telefone'], data['cpf'], 
            data['rg'], data['banco'], data['agencia'], data['conta_corrente']
        )
        
        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        if request.is_json:
            return jsonify({'message': 'Funcionário adicionado com sucesso'}), 201
        else:
            return render_template('funcionario.html')
    elif request.method == 'GET':
        cursor.execute('select * from funcionario')
        funcionarios = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('funcionario.html', funcionarios=funcionarios)


@app.route('/funcionario/<int:matricula>', methods=['DELETE'])
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

if __name__ == '__main__':
    app.run(debug=True)
