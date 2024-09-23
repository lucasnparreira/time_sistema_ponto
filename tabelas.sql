CREATE TABLE IF NOT EXISTS USUARIO (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL, -- Idealmente armazenar um hash da senha
    data TEXT NOT NULL -- Considerar renomear para `data_criacao` ou `data_registro`
);

CREATE TABLE IF NOT EXISTS EVENTO (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL,
    descricao TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS PONTO (
    id INTEGER PRIMARY KEY,
    hora TEXT NOT NULL,
    data TEXT NOT NULL,
    funcionario INTEGER, -- Definir o tipo da coluna
    evento INTEGER, -- Definir o tipo da coluna
    FOREIGN KEY (funcionario) REFERENCES funcionario(matricula),
    FOREIGN KEY (evento) REFERENCES evento(id)
);


CREATE TABLE IF NOT EXISTS FUNCAO (
    id INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS DEPARTAMENTO (
    id INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS ENDERECO (
    id INTEGER PRIMARY KEY,
    rua TEXT NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    pais TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS FUNCIONARIO (
    matricula INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    funcao TEXT NOT NULL,
    data_inicio TEXT NOT NULL,
    data_termino TEXT, -- Permitir NULL
    departamento TEXT NOT NULL,
    gerente TEXT,
    endereco INTEGER, -- Permitir NULL se nem todos tiverem
    telefone TEXT NOT NULL, -- Trocar para TEXT para suportar símbolos
    cpf TEXT NOT NULL,
    rg TEXT NOT NULL,
    banco TEXT NOT NULL,
    agencia TEXT NOT NULL,
    conta_corrente TEXT NOT NULL,
    FOREIGN KEY (endereco) REFERENCES endereco(id)
);