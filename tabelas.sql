CREATE TABLE IF NOT EXISTS USUARIO (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL, -- Idealmente armazenar um hash da senha
    data date CURRENT_DATE, -- Considerar renomear para `data_criacao` ou `data_registro`
    matricula TEXT NULL
);

CREATE TABLE IF NOT EXISTS CONVERSA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT
);

CREATE TABLE IF NOT EXISTS MENSAGEM (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversa_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    conteudo TEXT NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversa_id) REFERENCES CONVERSA (id),
    FOREIGN KEY (usuario_id) REFERENCES USUARIO (id)
);

CREATE TABLE IF NOT EXISTS PARTICIPANTE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversa_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (conversa_id) REFERENCES CONVERSA (id),
    FOREIGN KEY (usuario_id) REFERENCES USUARIO (id)
);

CREATE TABLE IF NOT EXISTS EVENTO (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL,
    descricao TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS PONTO (
    id INTEGER PRIMARY KEY,
    funcionario INTEGER,
    data TEXT NOT NULL,
    hora_entrada TEXT NULL,
    hora_saida TEXT NULL,
 -- Definir o tipo da coluna
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
    endereco TEXT NOT NULL, 
    telefone TEXT NOT NULL, -- Trocar para TEXT para suportar símbolos
    cpf TEXT NOT NULL,
    rg TEXT NOT NULL,
    banco TEXT NOT NULL,
    agencia TEXT NOT NULL,
    conta_corrente TEXT NOT NULL
);